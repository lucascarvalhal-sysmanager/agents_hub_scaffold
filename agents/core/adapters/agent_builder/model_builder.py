import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class ModelBuilder: 
    def __init__(self, model_config):
        self.config = model_config
        logger.info(f"Construindo agente com essa configuração: {self.config}")

    def model_generate_configuration(self) -> Dict:
        if not self.config:
            return {
                "temperature": None,
                "max_output_tokens": None,
                "top_k": None,
                "top_p": None
            }
        
        temperature = self.config.get("temperature")
        max_output_tokens = self.config.get("max_output_tokens")
        top_k = self.config.get("top_k")
        top_p = self.config.get("top_p")

        return {
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
            "top_k": top_k,
            "top_p": top_p
        }