import logging

from agents.container import services
from agents.core.domain.email.entities import SendEmailInput

logger = logging.getLogger(__name__)


def send_email_tool(to: str, subject: str, body: str) -> str:
    """Envia um email usando o serviço pré-configurado."""

    email_service = services.email_service
    if not email_service:
        return "Erro: serviço de email não configurado."

    try:
        email_service.send_email(input_data=SendEmailInput(to=to, subject=subject, body=body))
        return f"Email enviado com sucesso para {to}."
    except Exception as e:
        logger.exception("Erro ao enviar email para '%s'", to)
        return f"Erro ao enviar email para {to}: {e}"
