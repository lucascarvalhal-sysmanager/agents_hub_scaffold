import os
import logging
import tempfile
import asyncio
from pathlib import Path
from typing import Optional

from agents.container import services
from agents.core.domain.email.entities import SendEmailInput
from agents.core.domain.exceptions import RepoReadError
from agents.core.domain.repository_context import entities

logger = logging.getLogger(__name__)

async def read_repo_context(repo_url: str, branch: str) -> str:
    """
    Clona um repositório (público ou privado) em um diretório temporário,
    executa `npx repomix --stdout` e retorna o resultado como string.
    
    É uma função assíncrona, totalmente isolada, com logs e tratamento de erros robustos.
    """
    connection_config = services.setup_code_repo_auth
    provider = connection_config.provider
    username = connection_config.username
    token = connection_config.token

    repo_url = repo_url.removesuffix(".git")
    base_repo = repo_url.removeprefix("https://").removeprefix("http://")
    if not (username or token or provider):
        raise RepoReadError("Não foi encontrado todas as configurações para autenticação no repositório de código.")
    
    if provider not in base_repo:
        raise RepoReadError(f"URL do repositório '{repo_url}' não pertence ao provedor '{provider}'")
    
    source_repo_url = f"https://{username}:{token}@{base_repo}.git"   
    try:
        logger.debug(f"Iniciando leitura do repositório '{repo_url}' na branch '{branch}'")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            logger.debug(f"Clonando para diretório temporário: {tmp_path}")

            clone_cmd = ["git", "clone", "-b", branch, source_repo_url, str(tmp_path)]
            clone_proc = await asyncio.create_subprocess_exec(
                *clone_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )

            clone_output = []
            async for line in clone_proc.stdout:
                line = line.decode().strip()
                if line:
                    logger.debug(f"[git] {line}")
                    clone_output.append(line)

            await clone_proc.wait()

            if clone_proc.returncode != 0:
                error_msg = f"Falha ao clonar o repositório '{repo_url}'. Saída: {clone_output[-5:]}"
                raise RepoReadError(error_msg)

            logger.debug("Clone concluído com sucesso.")

            repomix_cmd = ["npx", "-y", "repomix", "--stdout"]
            repomix_proc = await asyncio.create_subprocess_exec(
                *repomix_cmd,
                cwd=tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await repomix_proc.communicate()

            if repomix_proc.returncode != 0:
                raise RepoReadError(f"Erro ao executar repomix:\n{stderr}")

            logger.debug("Repomix executado com sucesso.")
            return stdout.decode().strip()

    except RepoReadError as e:
        logger.error(f"[RepoReadError] {e}")
        raise

    except FileNotFoundError as e:
        logger.error("Comando não encontrado (git ou npx ausente no ambiente): %s", e)
        raise RepoReadError("Ambiente sem suporte a git ou npx.") from e

    except asyncio.TimeoutError:
        logger.error("Tempo limite excedido ao processar o repositório '%s'", repo_url)
        raise RepoReadError("Tempo limite excedido durante a leitura do repositório.")

    except Exception as e:
        logger.exception(f"Erro inesperado ao ler o repositório '{repo_url}': {e}")
        raise RepoReadError(f"Erro inesperado: {e}") from e    

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