import logging
from dotenv import load_dotenv
from .container import services
from .core.adapters.agent_builder.adk_builder import ADKAgentBuilder

load_dotenv()
logger = logging.getLogger(__name__)

config = services.config

logger.debug("Iniciando agente através do Google ADK framework...")
adk_builder = ADKAgentBuilder(config=config)
root_agent = adk_builder.create_agent()