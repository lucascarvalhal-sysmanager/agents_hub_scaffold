import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Any
from google.adk.agents.callback_context import CallbackContext

from catalog.callbacks.finops_persistence import (
    FinopsReport,
    FinopsPersistenceService,
    PersistenceFactory
)

logger = logging.getLogger(__name__)

# Configuração do relatório de performance
PERFORMANCE_REPORT_ENABLED = os.getenv("PERFORMANCE_REPORT_ENABLED", "true").lower() == "true"
PERFORMANCE_REPORT_LOG = os.getenv("PERFORMANCE_REPORT_LOG", "true").lower() == "true"
PERFORMANCE_REPORT_SAVE = os.getenv("PERFORMANCE_REPORT_SAVE", "false").lower() == "true"
PERFORMANCE_REPORT_DIR = os.getenv("PERFORMANCE_REPORT_DIR", ".adk/performance_reports")

# --- Singleton Factory ---
_finops_service_instance: Optional[FinopsPersistenceService] = None


def get_finops_service() -> Optional[FinopsPersistenceService]:
    """
    Lazy singleton factory for the FinopsPersistenceService.
    Delegates creation to the PersistenceFactory.
    """
    global _finops_service_instance
    if _finops_service_instance:
        return _finops_service_instance

    _finops_service_instance = PersistenceFactory.create_service()

    return _finops_service_instance


def _generate_performance_report(reports: List[FinopsReport], session_id: str) -> Optional[str]:
    """
    Gera relatório de performance usando a skill analyze_performance.

    Returns:
        Relatório em formato Markdown ou None se falhar
    """
    try:
        from catalog.skills.analyze_performance import get_performance_report_md

        # Converter FinopsReport para dict se necessário
        reports_data = []
        for r in reports:
            if hasattr(r, '__dict__'):
                # É um dataclass/objeto
                report_dict = {
                    "session_id": getattr(r, 'session_id', session_id),
                    "model_name": getattr(r, 'model_name', 'unknown'),
                    "prompt_token_count": getattr(r, 'prompt_token_count', 0),
                    "candidates_token_count": getattr(r, 'candidates_token_count', 0),
                    "total_token_count": getattr(r, 'total_token_count', 0),
                    "execution_time_ms": getattr(r, 'execution_time_ms', 0),
                    "interaction_timestamp": getattr(r, 'interaction_timestamp', ''),
                    "interaction_kind": getattr(r, 'interaction_kind', 'agent'),
                }
            else:
                # Já é dict
                report_dict = r
            reports_data.append(report_dict)

        return get_performance_report_md(reports=reports_data)

    except ImportError as e:
        logger.warning(f"[FinOps] Skill analyze_performance não disponível: {e}")
        return None
    except Exception as e:
        logger.error(f"[FinOps] Erro ao gerar relatório de performance: {e}")
        return None


def _save_performance_report(report_md: str, session_id: str) -> Optional[str]:
    """
    Salva o relatório de performance em arquivo.

    Returns:
        Caminho do arquivo salvo ou None se falhar
    """
    try:
        report_dir = Path(PERFORMANCE_REPORT_DIR)
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"performance_{session_id[:8]}_{timestamp}.md"
        filepath = report_dir / filename

        filepath.write_text(report_md, encoding="utf-8")
        logger.info(f"[FinOps] Relatório salvo em: {filepath}")

        return str(filepath)

    except Exception as e:
        logger.error(f"[FinOps] Erro ao salvar relatório: {e}")
        return None


def persist_finops_metrics(
    callback_context: CallbackContext,
    agent_response: Any = None
) -> None:
    """
    Persists all buffered FinOps reports in batch and generates performance report.

    Registrar como: after_agent_callback

    Configuração via variáveis de ambiente:
    - PERFORMANCE_REPORT_ENABLED: Habilita geração do relatório (default: true)
    - PERFORMANCE_REPORT_LOG: Exibe relatório no log (default: true)
    - PERFORMANCE_REPORT_SAVE: Salva relatório em arquivo (default: false)
    - PERFORMANCE_REPORT_DIR: Diretório para salvar (default: .adk/performance_reports)
    """
    try:
        state_dict = callback_context.state.to_dict()
        buffer: List[FinopsReport] = state_dict.get("finops_reports_buffer", [])

        if not buffer:
            return None

        logger.info(f"[FinOps] Persisting batch of {len(buffer)} reports...")

        # 1. Persistir no BigQuery (se configurado)
        service = get_finops_service()
        if service:
            service.save_reports_batch(buffer)

        # 2. Gerar relatório de performance (se habilitado)
        if PERFORMANCE_REPORT_ENABLED:
            session_id = state_dict.get("session_id", "unknown")

            # Incluir side reports (traduções) se existirem
            side_reports = state_dict.get("temp:finops_side_reports", [])
            all_reports = list(buffer) + list(side_reports)

            report_md = _generate_performance_report(all_reports, session_id)

            if report_md:
                # Exibir no log
                if PERFORMANCE_REPORT_LOG:
                    logger.info(f"\n[FinOps] Performance Report:\n{report_md}")

                # Salvar em arquivo
                if PERFORMANCE_REPORT_SAVE:
                    _save_performance_report(report_md, session_id)

                # Armazenar no state para acesso posterior
                callback_context.state["last_performance_report"] = report_md

        # 3. Limpar buffers
        callback_context.state["finops_reports_buffer"] = []
        callback_context.state["temp:finops_side_reports"] = []

    except Exception as e:
        logger.error(f"[FinOps] Batch persistence failed: {e}", exc_info=True)
