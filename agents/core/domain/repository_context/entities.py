from pydantic import BaseModel, Field
from enum import Enum

class CodeRepositoryProvider(str, Enum):
    GITHUB="github"
    FAKE_REPO="fake_repo"

class CodeRepositoryAuthConfig(BaseModel):
    provider: CodeRepositoryProvider = Field(..., description="Provedor de repositório de código")
    username: str = Field(..., description="Nome do usuário no repositório de código")
    token: str = Field(..., description="Token de acesso do usuário no repositório de código")
