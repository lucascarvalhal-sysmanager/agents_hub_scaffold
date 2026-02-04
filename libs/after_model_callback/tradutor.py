import logging
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types
from typing import Optional

logger = logging.getLogger(__name__)

def traduzir_pensamento(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """
    Processa a resposta para manter o formato o mais "clean" possível.
    O "Thought" é interno do Gemini, então não foi achada ainda uma solução para traduzir ele diretamente sem callback.
    """
    if not llm_response.content or not llm_response.content.parts:
        return None
    
    texto = llm_response.content.parts[0].text or ""
    
    # Remove prefixos desnecessários se existirem
    texto_limpo = texto.strip()
    for prefixo in ["RESPOSTA FINAL:", "RESPOSTA:", "Resposta Final:", "Resposta:"]:
        if texto_limpo.startswith(prefixo):
            texto_limpo = texto_limpo[len(prefixo):].strip()
    
    # Retorna resposta limpa
    if texto_limpo != texto.strip():
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=texto_limpo)]
            )
        )
    
    return None
