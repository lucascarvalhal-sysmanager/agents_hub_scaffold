from jsonschema import validate, ValidationError
import yaml
import logging
import re
import os
from typing import Dict

logger = logging.getLogger(__name__)

class YAMLHandler:
    def __init__(self):
        pass 

    def resolve_env_vars(self, obj) -> Dict:
        if isinstance(obj, dict):
            return {k: self.resolve_env_vars(v) for k, v in obj.items()}

        elif isinstance(obj, list):
            return [self.resolve_env_vars(i) for i in obj]

        elif isinstance(obj, str):
            # Procura e substitui todas as variáveis no formato ${VAR}
            pattern = re.compile(r"\$\{([^}]+)\}")
            matches = pattern.findall(obj)

            if matches:
                result = obj
                for var in matches:
                    value = os.getenv(var, "")
                    result = result.replace(f"${{{var}}}", value)
                return result
            return obj
        else:
            return obj

    def validate_config(self, user_config): 
        with open("config/schema/schema_validator.yaml") as f:
            schema = yaml.safe_load(f)
        try:
            validate(instance=user_config, schema=schema)
        except ValidationError as e:
            logger.error(f"Erro no campo {'/'.join(map(str, e.path))}: {e.message}")
        except Exception as e:
            logger.error(f"Erro: {e}")

    def read_solution_config(self) -> Dict:
        path = "config/agent"
        dir = os.listdir(path=path)

        for item in dir:
            filepath = os.path.join(path, item)
            with open(filepath, 'r') as file:
                content = yaml.safe_load(file)
                config = self.resolve_env_vars(content)
                self.validate_config(config)
                logger.debug("==========================================================")
                logger.debug("Dicionário contendo as configurações do agente:")
                logger.debug(config)
                logger.debug("==========================================================")
                
        return config