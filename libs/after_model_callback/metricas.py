import logging
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def log_resposta(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """
    Callback executado DEPOIS do LLM responder.
    Registra métricas e informações sobre a resposta gerada.
    """
    timestamp = datetime.now().isoformat()
    agent_name = callback_context.agent_name

    response_text = ""
    if llm_response.content and llm_response.content.parts:
        response_text = llm_response.content.parts[0].text or ""

    response_length = len(response_text)
    word_count = len(response_text.split())

    logger.info(f"[METRICAS] ========================================")
    logger.info(f"[METRICAS] Timestamp: {timestamp}")
    logger.info(f"[METRICAS] Agente: {agent_name}")
    logger.info(f"[METRICAS] Tamanho da resposta: {response_length} caracteres")
    logger.info(f"[METRICAS] Quantidade de palavras: {word_count}")
    logger.info(f"[METRICAS] Preview: {response_text[:100]}...")
    logger.info(f"[METRICAS] ========================================")

    return None
