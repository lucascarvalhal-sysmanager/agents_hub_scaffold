import logging
from dotenv import load_dotenv

from agents.helpers.yaml_handler import YAMLHandler
from .core.factories.email_service_factory import EmailServiceFactory
from .core.domain.agent.enums import PreBuiltTools
from .core.domain.repository_context.entities import CodeRepositoryAuthConfig

load_dotenv()

logger = logging.getLogger(__name__)

class Container:
    """
    A simple service container that instantiates and holds the application's
    configuration and shared services.
    """
    def __init__(self):
        self.config = YAMLHandler().read_solution_config()
        self.email_service = self._create_email_service()
        self.setup_code_repo_auth = self._setup_code_repo_auth()

    def _create_email_service(self):
        tools_config = self.config.get("tools", [])
        email_config = None
        for tool in tools_config:
            if tool.get("kind") == PreBuiltTools.SEND_EMAIL:
                email_config = tool
        
        if not email_config:
            return None

        provider = email_config.get("provider")
        connection_config = email_config.get("connection_config")
        logger.debug(f"Configurando serviço de email com provider '{provider}' e configuração '{connection_config}'")

        if provider and connection_config is not None:
            return EmailServiceFactory.get_email_service(provider, connection_config)
        
        return None
    
    def _setup_code_repo_auth(self) -> CodeRepositoryAuthConfig:
        tools_config = self.config.get("tools", [])
        github_config = None
        for tool in tools_config:
            if tool.get("kind") == PreBuiltTools.READ_REPO_CONTEXT:
                github_config = tool
        
        if github_config is None:
            return None
        
        provider = github_config.get("provider")
        connection_config = github_config.get("connection_config")
        username = connection_config.get("username")
        token = connection_config.get("token")
        code_repository_auth_config = CodeRepositoryAuthConfig(
            provider=provider,
            username=username,
            token=token
        )                        
        return code_repository_auth_config        
        
services = Container()
