import logging
import tempfile
import asyncio
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class RepoReadError(Exception):
    """Erro ao ler repositório."""
    pass


async def read_repo_context(
    repo_url: str,
    branch: str,
    provider: str,
    username: str,
    token: str
) -> str:
    """
    Clona um repositório (público ou privado) em um diretório temporário,
    executa `npx repomix --stdout` e retorna o resultado como string.

    Args:
        repo_url: URL do repositório
        branch: Branch a ser clonada
        provider: Provedor do repositório (github, gitlab, etc)
        username: Usuário para autenticação
        token: Token para autenticação

    Returns:
        String com o contexto do repositório

    Raises:
        RepoReadError: Se houver erro ao ler o repositório
    """
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
