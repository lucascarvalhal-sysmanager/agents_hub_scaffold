import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
import google.genai as genai

from agents.core.domain.agent.enums import PRE_BUILT_TOOL_VALUES
from agents.helpers.finops_persistence import FinopsReport

logger = logging.getLogger(__name__)

def inject_log_before_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
):
    agent_name = tool_context.agent_name
    tool_name = tool.name
    logger.info(f"[Tool] {agent_name}: Start tool call '{tool_name}'")
    return None

def _translate_to_ptbr(text: str) -> Tuple[str, Optional[types.GenerateContentResponseUsageMetadata], float]:
    """Traduz text do inglês para português usando Gemini."""
    if not text or len(text.strip()) < 10:
        return text, None, 0.0

    try:
        logger.info(f"Iniciando tradução ({len(text)} chars)")
        client = genai.Client(vertexai=True)
        
        start_time = time.time()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Traduza o seguinte texto para português do Brasil. Retorne APENAS a tradução, sem explicações:\n\n{text}"
        )
        duration_ms = (time.time() - start_time) * 1000.0
        
        logger.info("Tradução concluída")
        return response.text.strip(), response.usage_metadata, duration_ms
    except Exception as e:
        logger.error(f"Erro ao traduzir: {e}")
        return text, None, 0.0

def translate_thought(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Intercepta o pensamento REAL do Gemini e traduz para português."""

    if not llm_response.content or not llm_response.content.parts:
        return llm_response

    new_parts = []
    modified = False

    # Modelo usado para tradução
    TRANSLATION_MODEL = "gemini-2.0-flash"

    for part in llm_response.content.parts:
        # Se for pensamento real (thought=True), traduz e formata
        if hasattr(part, 'thought') and part.thought and part.text:
            logger.info(f"Pensamento detectado ({len(part.text)} chars)")

            translated_text, usage_meta, duration_ms = _translate_to_ptbr(part.text)

            if usage_meta:
                try:
                    state_data = callback_context.state.to_dict()
                    usage_stats = state_data.get("model_usage_stats", {})

                    if TRANSLATION_MODEL not in usage_stats:
                        usage_stats[TRANSLATION_MODEL] = {"prompt": 0, "candidates": 0, "total": 0}

                    p_count = getattr(usage_meta, "prompt_token_count", 0)
                    c_count = getattr(usage_meta, "candidates_token_count", 0)
                    t_count = getattr(usage_meta, "total_token_count", 0)

                    usage_stats[TRANSLATION_MODEL]["prompt"] += p_count
                    usage_stats[TRANSLATION_MODEL]["candidates"] += c_count
                    usage_stats[TRANSLATION_MODEL]["total"] += t_count

                    callback_context.state["model_usage_stats"] = usage_stats
                    logger.info(f"Tradução contabilizada: +{t_count} tokens")

                    report = FinopsReport(
                        user_prompt=part.text,
                        agent_response=translated_text,
                        model_name=TRANSLATION_MODEL,
                        prompt_token_count=p_count,
                        candidates_token_count=c_count,
                        total_token_count=t_count,
                        execution_time_ms=duration_ms,
                        interaction_timestamp=datetime.now(timezone.utc).isoformat(),
                        interaction_kind="translation"
                    )

                    side_reports = state_data.get("temp:finops_side_reports", [])
                    side_reports.append(report)
                    callback_context.state["temp:finops_side_reports"] = side_reports

                except Exception as e:
                    logger.warning(f"Falha ao registrar uso de tradução: {e}")

            # Formata o pensamento traduzido
            formatted_thought = f"💭 Raciocínio:\n{translated_text}"
            new_parts.append(types.Part(thought=True, text=formatted_thought))
            modified = True
            logger.info("Pensamento traduzido com sucesso")
        else:
            new_parts.append(part)

    if modified:
        logger.info("Retornando LlmResponse com pensamento traduzido")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=new_parts
            )
        )

    return llm_response