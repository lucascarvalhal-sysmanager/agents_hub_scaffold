import re
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
from typing import Optional

def formatar_resposta(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """Formata separando raciocínio da resposta final."""
    if not llm_response.content or not llm_response.content.parts:
        return None
    
    texto = llm_response.content.parts[0].text or ""
    
    if "PLANEJAMENTO:" not in texto and "RACIONAL:" not in texto:
        return None
    
    planejamento = ""
    racional = ""
    resposta_final = ""
    
    match_plan = re.search(r'PLANEJAMENTO:(.+?)(?=RACIONAL:|RESPOSTA FINAL:|$)', texto, re.DOTALL | re.IGNORECASE)
    if match_plan:
        planejamento = match_plan.group(1).strip()
    
    match_rac = re.search(r'RACIONAL:(.+?)(?=RESPOSTA FINAL:|$)', texto, re.DOTALL | re.IGNORECASE)
    if match_rac:
        racional = match_rac.group(1).strip()
    
    match_resp = re.search(r'RESPOSTA FINAL:(.+?)$', texto, re.DOTALL | re.IGNORECASE)
    if match_resp:
        resposta_final = match_resp.group(1).strip()
    
    # Formatação com separação visual forte
    partes = []
    
    if planejamento or racional:
        partes.append("```")
        partes.append("💭 PENSAMENTO")
        partes.append("─" * 40)
        if planejamento:
            partes.append(f"📋 Plano: {planejamento}")
        if racional:
            partes.append(f"🧠 Racional: {racional}")
        partes.append("```")
        partes.append("")
    
    if resposta_final:
        partes.append(f"🤖 {resposta_final}")
    
    texto_formatado = "\n".join(partes)
    
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=texto_formatado)]
        )
    )
