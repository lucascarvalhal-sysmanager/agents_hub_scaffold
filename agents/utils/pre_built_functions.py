import logging
import tempfile
import asyncio
from pathlib import Path

from agents.container import services
from agents.core.domain.email.entities import SendEmailInput

logger = logging.getLogger(__name__)


async def read_repo_context(repo_url: str, branch: str) -> str:
    """Clona um repositório e retorna o contexto via repomix."""

    config = services.setup_code_repo_auth
    if not (config and config.username and config.token and config.provider):
        return "Erro: configurações de autenticação incompletas (username, token ou provider)."

    base_repo = repo_url.removesuffix(".git").removeprefix("https://").removeprefix("http://")

    if config.provider not in base_repo:
        return f"Erro: URL '{repo_url}' não pertence ao provedor '{config.provider}'."

    source_url = f"https://{config.username}:{config.token}@{base_repo}.git"

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            clone = await asyncio.create_subprocess_exec(
                "git", "clone", "-b", branch, source_url, str(tmp_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            clone_out, _ = await clone.communicate()

            if clone.returncode != 0:
                return f"Erro: falha ao clonar '{repo_url}'. Verifique se a URL e a branch estão corretas."

            repomix = await asyncio.create_subprocess_exec(
                "npx", "-y", "repomix", "--stdout",
                "--style", "markdown",
                cwd=tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await repomix.communicate()

            if repomix.returncode != 0:
                return f"Erro: falha ao executar repomix no repositório."

            return stdout.decode().strip()

    except Exception as e:
        logger.exception("Erro ao ler repositório '%s'", repo_url)
        return f"Erro inesperado ao ler repositório: {e}"

def send_email_tool(to: str, subject: str, body: str) -> None:
    """Envia um email usando um serviço de email pré-configurado.  
    
    Para isso, utiliza os seguintes parâmetros:  
    Args:  
        to (str): Endereço de email do destinatário.  
        subject (str): Assunto do email.  
        body (str): Conteúdo do email em texto simples.  
    Returns: 
        Caso o email seja enviado com sucesso, não há retorno.
    """
    try: 
        email_service_instance = services.email_service

        if not email_service_instance:
            raise ConnectionError("Serviço de email não foi configurado, por favor verifique as configurações.")

        send_email_input = SendEmailInput(to=to, subject=subject, body=body)
        email_service_instance.send_email(input_data=send_email_input)
    except ConnectionError as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao enviar email para '{to}': {e}.'")
        raise Exception(f"Erro ao enviar email para '{to}': {e}.'")