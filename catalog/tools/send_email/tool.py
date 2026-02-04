import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SendEmailInput:
    """Input para envio de email."""
    to: str
    subject: str
    body: str


def send_email_tool(
    to: str,
    subject: str,
    body: str,
    email_service: Optional[object] = None
) -> None:
    """
    Envia um email usando um serviço de email pré-configurado.

    Args:
        to: Endereço de email do destinatário
        subject: Assunto do email
        body: Conteúdo do email em texto simples
        email_service: Instância do serviço de email (opcional, usa container se não fornecido)

    Returns:
        None se o email for enviado com sucesso

    Raises:
        ConnectionError: Se o serviço de email não estiver configurado
        Exception: Se houver erro ao enviar o email
    """
    try:
        if email_service is None:
            # Tenta obter do container de serviços
            try:
                from agents.container import services
                email_service = services.email_service
            except ImportError:
                pass

        if not email_service:
            raise ConnectionError("Serviço de email não foi configurado, por favor verifique as configurações.")

        send_email_input = SendEmailInput(to=to, subject=subject, body=body)
        email_service.send_email(input_data=send_email_input)

    except ConnectionError as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao enviar email para '{to}': {e}.'")
        raise Exception(f"Erro ao enviar email para '{to}': {e}.'")
