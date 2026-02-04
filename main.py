import os
import logging
import uvicorn
import google.cloud.logging
from google.adk.cli.fast_api import get_fast_api_app

from agents.container import services

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOCAL_DEVELOPMENT = os.getenv("LOCAL_DEVELOPMENT", "false").lower() == "true"

trace_to_cloud = False
web=True
if LOCAL_DEVELOPMENT is False:
    trace_to_cloud = True
    web=False
    client = google.cloud.logging.Client()
    client.setup_logging()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

# Seguindo issue do ADK para suprimir log desnecessário: https://github.com/google/adk-python/issues/2200
logging.getLogger("google_adk.google.adk.tools.base_authenticated_tool").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Inciando API... Log Level: {LOG_LEVEL.upper()}")
    config = services.config
    solution = config.get("solution", None)
    session_service_uri = None
    if solution:
        session_service_uri = solution.get("session_service_uri", None)
   
    app = get_fast_api_app(
        agents_dir=".",
        session_service_uri=session_service_uri,
        artifact_service_uri=None,
        memory_service_uri=None,
        eval_storage_uri=None,
        allow_origins=["*"],
        web=web,
        trace_to_cloud=trace_to_cloud,
        a2a=False,
        host="0.0.0.0",
        port=8080,
        reload_agents=False,
    )
    uvicorn.run(app, host="0.0.0.0", port=8080)