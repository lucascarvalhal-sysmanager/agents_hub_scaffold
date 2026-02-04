import logging
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def log_inicio(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback executado ANTES do agente começar a processar.
    Registra informações de auditoria para monitoramento.
    """
    timestamp = datetime.now().isoformat()
    agent_name = callback_context.agent_name

    logger.info(f"[AUDITORIA] ========================================")
    logger.info(f"[AUDITORIA] Timestamp: {timestamp}")
    logger.info(f"[AUDITORIA] Agente: {agent_name}")
    logger.info(f"[AUDITORIA] Agente iniciando processamento...")
    logger.info(f"[AUDITORIA] ========================================")

    return None
