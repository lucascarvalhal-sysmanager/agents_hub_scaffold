import logging
import tempfile
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)


async def read_repo_context(
    repo_url: str,
    branch: str,
    provider: str,
    username: str,
    token: str
) -> str:
    """Clona um repositório e retorna o contexto via repomix."""

    if not (username and token and provider):
        raise RuntimeError("Configurações de autenticação incompletas (username, token ou provider).")

    base_repo = repo_url.removesuffix(".git").removeprefix("https://").removeprefix("http://")

    if provider not in base_repo:
        raise RuntimeError(f"URL '{repo_url}' não pertence ao provedor '{provider}'.")

    source_url = f"https://{username}:{token}@{base_repo}.git"

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
                raise RuntimeError(f"Falha ao clonar '{repo_url}': {clone_out.decode().strip()}")

            repomix = await asyncio.create_subprocess_exec(
                "npx", "-y", "repomix", "--stdout",
                cwd=tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await repomix.communicate()

            if repomix.returncode != 0:
                raise RuntimeError(f"Erro ao executar repomix: {stderr.decode().strip()}")

            return stdout.decode().strip()

    except RuntimeError:
        raise
    except Exception as e:
        logger.exception("Erro ao ler repositório '%s'", repo_url)
        raise RuntimeError(f"Erro inesperado: {e}") from e
