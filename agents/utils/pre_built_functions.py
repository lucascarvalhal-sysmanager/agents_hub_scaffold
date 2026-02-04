"""
Pre-Built Functions - Re-exporta do catálogo para manter compatibilidade.

Os códigos reais estão em:
- catalog/tools/read_repo_context/
- catalog/tools/send_email/
"""

import logging
from typing import Optional

from agents.container import services
from agents.core.domain.email.entities import SendEmailInput
from agents.core.domain.exceptions import RepoReadError

from catalog.tools.read_repo_context import read_repo_context as _read_repo_context
from catalog.tools.send_email import send_email_tool as _send_email_tool

logger = logging.getLogger(__name__)


async def read_repo_context(repo_url: str, branch: str) -> str:
    """
    Wrapper que usa as configurações do container de serviços.
    """
    connection_config = services.setup_code_repo_auth
    return await _read_repo_context(
        repo_url=repo_url,
        branch=branch,
        provider=connection_config.provider,
        username=connection_config.username,
        token=connection_config.token
    )


def send_email_tool(to: str, subject: str, body: str) -> None:
    """
    Wrapper que usa o serviço de email do container.
    """
    email_service = services.email_service

    if not email_service:
        raise ConnectionError("Serviço de email não foi configurado, por favor verifique as configurações.")

    send_email_input = SendEmailInput(to=to, subject=subject, body=body)
    email_service.send_email(input_data=send_email_input)


__all__ = ["read_repo_context", "send_email_tool", "RepoReadError"]
