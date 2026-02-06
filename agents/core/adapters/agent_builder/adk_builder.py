import logging
import importlib
from typing import Optional, Dict, List, Any
from google.adk.agents import Agent, SequentialAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types

from agents.core.domain.agent.enums import AgentFlowType, CallbackType
from agents.helpers import hooks, finops_callbacks
from agents.core.adapters.agent_builder.adk_tools_builder import ADKToolsBuilder
from agents.utils import prompt_functions
from catalog.tools.datetime_tool import get_current_datetime
from .model_builder import ModelBuilder
from agents.core.domain.exceptions import (
    AgentConfigurationError,
    ToolResolutionError,
    CallbackResolutionError,
    AgentCreationError
)

logger = logging.getLogger(__name__)

class ADKAgentBuilder:
    def __init__(self, config):
        if not config:
            raise AgentConfigurationError("Configuração do agente não pode ser vazia.")
        self.config = config
        self.tools_builder = ADKToolsBuilder(self.config.get("tools", []))
        logger.info(f"Construindo agente com essa configuração: {self.config}")

    def create_agent(self):
        try:
            logger.debug(f"Tipo de agente: {self.config.get('type')}")
            agent_flow_map = {
                AgentFlowType.SINGLE: self._create_single_agent,
                AgentFlowType.HIERARCHICAL: self._create_hierarchical_agents,
                AgentFlowType.SEQUENTIAL: self._create_sequential_agents,
            }
            
            agent_type = self.config.get("type")
            if not agent_type:
                raise AgentConfigurationError("Tipo de agente ('type') não especificado na configuração.")
                
            creator_func = agent_flow_map.get(agent_type)
            if not creator_func:
                 raise AgentConfigurationError(f"Tipo de agente desconhecido: {agent_type}")
                 
            root_agent = creator_func()
            return root_agent
        except (AgentConfigurationError, AgentCreationError):
            raise
        except Exception as e:
            logger.critical(f"Erro inesperado ao criar agente: {e}", exc_info=True)
            raise AgentCreationError(f"Falha crítica na criação do agente: {e}") from e
    
    def _create_single_agent(self) -> Agent:
        try:
            agent_config = self.config.get("agent")
            if not agent_config:
                 raise AgentConfigurationError("Configuração 'agent' ausente para tipo single.")

            tools_config = self.config.get("tools", [])
            
            dict_tools = self.tools_builder.create_dict_tools()
            agent_tools_names = [tool["name"] for tool in tools_config if "name" in tool]
            agent_tools = self.tools_builder.assign_agent_tools(
                dict_tools = dict_tools, 
                agent_name = agent_config.get("name"), 
                agent_tools_names = agent_tools_names
            )

            agent = self._create_adk_llm_agent(
                name = agent_config.get("name"),
                model = agent_config.get("model"),
                generate_content_config = agent_config.get("generate_content_config"),
                description= agent_config.get("description"),
                instruction = agent_config.get("instruction"),
                tools = agent_tools,
                callbacks=agent_config.get("callbacks", None)
            )
            return agent
        except (AgentConfigurationError, ToolResolutionError, AgentCreationError):
            raise
        except Exception as e:
             raise AgentCreationError(f"Erro ao criar single agent: {e}") from e

    def _create_hierarchical_agents(self) -> Agent:
        try:
            all_agents = []    
            dict_tools = self.tools_builder.create_dict_tools()

            agents_config = self.config.get("agent", {}).get("agents", [])
            if not agents_config:
                raise AgentConfigurationError("Lista de sub-agentes ('agents') vazia ou ausente para hierárquico.")

            for agent_config in agents_config:
                agent_tools = self.tools_builder.assign_agent_tools(
                    dict_tools = dict_tools, 
                    agent_name = agent_config.get("name"), 
                    agent_tools_names = agent_config.get("tools", [])
                )

                agent = self._create_adk_llm_agent(
                    name = agent_config.get("name"), 
                    model = agent_config.get("model"), 
                    generate_content_config = agent_config.get("generate_content_config"),
                    description = agent_config.get("description"), 
                    instruction = agent_config.get("instruction"), 
                    tools = agent_tools,
                    callbacks=agent_config.get("callbacks", None)
                )
                all_agents.append(agent)
            
            hierarchical_config = self.config.get("agent")
            if not hierarchical_config:
                 raise AgentConfigurationError("Configuração do coordenador ausente.")

            model_builder = ModelBuilder(hierarchical_config.get("generate_content_config"))
            content_config = model_builder.model_generate_configuration()
            resolved_callbacks = self._configure_callbacks(hierarchical_config.get("callbacks"))

            coordinator_agent = Agent(
                name = hierarchical_config.get("name"),
                model = hierarchical_config.get("model"),
                generate_content_config = types.GenerateContentConfig(
                    temperature = content_config.get("temperature"),
                    max_output_tokens = content_config.get("max_output_tokens"),
                    top_k = content_config.get("top_k"),
                    top_p = content_config.get("top_p"),
                    http_options=types.HttpOptions(
                        retry_options=types.HttpRetryOptions(
                            initial_delay=20,
                            attempts=10,
                            exp_base=120,
                            max_delay=2
                        ),
                    ),
                ),
                description = hierarchical_config.get("description"),
                instruction = f"{get_current_datetime(include_time=False)} \n {hierarchical_config.get('instruction')}",
                sub_agents = all_agents,
                **resolved_callbacks
            )
            return coordinator_agent
        except (AgentConfigurationError, ToolResolutionError, AgentCreationError, CallbackResolutionError):
            raise
        except Exception as e:
            raise AgentCreationError(f"Erro ao criar agente hierárquico: {e}") from e

    def _create_sequential_agents(self) -> SequentialAgent:
        try:
            all_agents = []
            dict_tools = self.tools_builder.create_dict_tools()

            agents_config = self.config.get("agent", {}).get("agents", [])
            if not agents_config:
                 raise AgentConfigurationError("Lista de sub-agentes ('agents') vazia ou ausente para sequencial.")

            for agent_config in agents_config:
                agent_tools = self.tools_builder.assign_agent_tools(
                    dict_tools=dict_tools, 
                    agent_name=agent_config.get("name"), 
                    agent_tools_names=agent_config.get("tools", [])
                )

                agent = self._create_adk_llm_agent(
                    name = agent_config.get("name"), 
                    model = agent_config.get("model"), 
                    generate_content_config = agent_config.get("generate_content_config"),
                    description = agent_config.get("description"), 
                    instruction = agent_config.get("instruction"), 
                    tools = agent_tools,
                    callbacks=agent_config.get("callbacks", None)
                )
                all_agents.append(agent)
            
            sequential_config = self.config.get("agent")
            if not sequential_config:
                 raise AgentConfigurationError("Configuração do coordenador sequencial ausente.")

            coordinator_agent = SequentialAgent(
                name = sequential_config.get("name"),
                description = sequential_config.get("description"),
                sub_agents = all_agents
            )
            return coordinator_agent
        except (AgentConfigurationError, ToolResolutionError, AgentCreationError):
             raise
        except Exception as e:
            raise AgentCreationError(f"Erro ao criar agente sequencial: {e}") from e

    def _create_adk_llm_agent(self, name: str, model: str, generate_content_config: Optional[dict], description: str, instruction: str, tools: list, callbacks: Optional[dict] = None) -> Agent:
        try:
            model_builder = ModelBuilder(generate_content_config)
            content_config = model_builder.model_generate_configuration()

            resolved_callbacks = self._configure_callbacks(callbacks)

            agent = Agent(
                name = name,
                model = model,
                description = description,  
                instruction = f"{get_current_datetime(include_time=False)} \n {instruction}",
                tools = tools,
                planner=BuiltInPlanner(
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=True,
                        thinking_budget=content_config.get("thinking_budget", None)
                    )
                ),
                generate_content_config = types.GenerateContentConfig(
                    temperature = content_config.get("temperature", None),
                    max_output_tokens = content_config.get("max_output_tokens", None),
                    top_k = content_config.get("top_k", None),
                    top_p = content_config.get("top_p", None),
                    http_options=types.HttpOptions(
                        retry_options=types.HttpRetryOptions(
                            initial_delay=20,
                            attempts=10,
                            exp_base=120,
                            max_delay=2
                        ),
                    ),
                ),
                **resolved_callbacks
            )
            return agent
        except CallbackResolutionError:
             raise
        except Exception as e:
            logger.error(f"Erro ao instanciar Agent '{name}': {e}")
            raise AgentCreationError(f"Falha na instanciação do agente '{name}': {e}") from e
    
    def _configure_callbacks(self, callbacks_config: Optional[dict]) -> Dict[str, List[Any]]:
        try:
            callbacks = {
                CallbackType.BEFORE_AGENT.value: [],
                CallbackType.BEFORE_MODEL.value: [finops_callbacks.finops_before_model_callback],
                CallbackType.BEFORE_TOOL.value: [hooks.inject_log_before_tool_callback],
                CallbackType.AFTER_MODEL.value: [hooks.translate_thought, finops_callbacks.collect_finops_metrics],
                CallbackType.AFTER_TOOL.value: [],
                CallbackType.AFTER_AGENT.value: [finops_callbacks.persist_finops_metrics]
            }

            if callbacks_config:
                for callback_type in CallbackType:
                    key = callback_type.value
                    if key in callbacks_config:
                        resolved = self._resolve_callbacks(callbacks_config[key], callback_type)
                        callbacks[key].extend(resolved)
            
            return callbacks
        except CallbackResolutionError:
            raise
        except Exception as e:
             raise CallbackResolutionError(f"Erro inesperado ao configurar callbacks: {e}") from e

    def _resolve_callbacks(self, callback_names: list[str], callback_type: CallbackType) -> list:
        try:
            if not callback_names:
                return []

            resolved_callbacks = []
            for name in callback_names:
                module_name, func_name = name.rsplit(".", 1)
                module = importlib.import_module(f"libs.{callback_type.value}.{module_name}")
                func = getattr(module, func_name)
                resolved_callbacks.append(func)

            return resolved_callbacks
        except Exception as e:
             logger.error(f"Failed to load callbacks for '{callback_type.value}': {e}")
             raise CallbackResolutionError(f"Falha ao carregar callbacks: {e}") from e
    # TODO: Construir implementação do loop agent
