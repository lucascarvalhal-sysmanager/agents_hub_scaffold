import logging
from typing import Any, List, Callable, Union, Optional
from google.adk.tools.mcp_tool import MCPToolset, SseConnectionParams, StreamableHTTPConnectionParams, StdioConnectionParams
from google.adk.tools.function_tool import FunctionTool
from mcp.client.stdio import StdioServerParameters

from agents.core.domain.agent.enums import ToolsType, PreBuiltTools
from agents.utils import pre_built_functions, adk_pre_built_tools, prompt_functions
from catalog.tools.send_email import tool as catalog_send_email

logger = logging.getLogger(__name__)

ToolInstance = Union[MCPToolset, FunctionTool]

class ADKToolsBuilder:
    def __init__(self, tools_config: List[dict[str, Any]]):
        self.tools_config = tools_config or []

    def _create_sse_tool(self, tool_name: str, url: str) -> MCPToolset:
        logger.debug(f"Criando SSE Tool '{tool_name}' com url '{url}'")
        if url == "":
            raise ValueError(f"URL não encontrada para acessar a tool '{tool_name}'")    
        tool = MCPToolset(
            connection_params=SseConnectionParams(url=url),
            errlog=False
        )
        return tool

    def _create_streamable_tool(self, tool_name: str, url: str, headers: dict[str, Any]) -> MCPToolset:    
        if url == "":
            raise ValueError(f"URL não encontrada para acessar a tool '{tool_name}'")    
        
        tool = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=url,
                headers=headers,
                errlog=False
            )
        )
        return tool

    def _create_stdio_tool(self, tool_name: str, configs: dict[str, Any]) -> MCPToolset:
        command = configs.get("command", "")
        if command == "":
            raise ValueError(f"Comando para executar Stdio não encontrado para tool '{tool_name}'")    
        args = configs.get("args", "")
        if args == "":
            raise ValueError(f"Argumentos para iniciar Stdio não encontrado para tool '{tool_name}'")       
        env = configs.get("env", {})
        tool_filter = configs.get("tool_filter", None)

        tool = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=command,
                    args=args,
                    env=env
                ),
                timeout=60
            ),
            tool_filter=tool_filter,
            errlog=False
        )
        return tool

    def _get_pre_built_tool(self, tool_name: str, params: dict) -> FunctionTool:
        try:
            pre_built_functions_map: dict[str, Callable[[dict], FunctionTool]] = {
                PreBuiltTools.READ_REPO_CONTEXT: lambda _: pre_built_functions.read_repo_context,
                PreBuiltTools.SEND_EMAIL: lambda _: catalog_send_email.send_email_tool,
                PreBuiltTools.GOOGLE_SEARCH: lambda _: adk_pre_built_tools.search_agent_tool,
                PreBuiltTools.GET_DATETIME: lambda _: prompt_functions.get_current_datetime,
            }

            if tool_name not in pre_built_functions_map:
                raise ValueError(f"Tool pré construída '{tool_name}' não encontrada.")

            return pre_built_functions_map[tool_name](params)
        except ValueError as e:
            logger.error(f"Erro ao obter tool pré construída '{tool_name}': {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao obter tool pré construída '{tool_name}': {e}")
            raise Exception(f"Erro inesperado ao obter tool pré construída '{tool_name}': {e}")

    def get_tools(self) -> Optional[List[ToolInstance]]:
        logger.debug(f"[Tools] Contidas no arquivo de configuração: '{self.tools_config}'")
        if not self.tools_config:
            return []
            
        dispatch_map: dict[ToolsType, Callable[[dict[str, Any]], ToolInstance]] = {
            ToolsType.SSE: lambda cfg: self._create_sse_tool(tool_name=cfg.get("name", ""), url=cfg.get("url", "")),
            ToolsType.STREAMABLE: lambda cfg: self._create_streamable_tool(tool_name=cfg.get("name", ""), url=cfg.get("url", ""), headers=cfg.get("headers", None)),
            ToolsType.STDIO: lambda cfg: self._create_stdio_tool(tool_name=cfg.get("name", ""), configs=cfg.get("configs", "")),
            ToolsType.PRE_BUILT: lambda cfg: self._get_pre_built_tool(tool_name=cfg.get("kind", ""), params=cfg.get("params", {}))
        }
            
        tools: List[Union[MCPToolset, FunctionTool]] = []
        for cfg in self.tools_config:
            transport = cfg.get("transport")
            if transport not in dispatch_map:
                raise ValueError(f"Tipo de tool '{transport}' não suportado.")
            
            tool = dispatch_map[transport](cfg)
            tools.append(tool)
        return tools

    def create_dict_tools(self) -> Optional[dict[str, MCPToolset]]:
        if not self.tools_config:
            return {}
        
        instantiated_tools = self.get_tools()
        dict_tools = {cfg["name"]: tool for cfg, tool in zip(self.tools_config, instantiated_tools)}    
        return dict_tools

    def assign_agent_tools(self, dict_tools: dict[str, MCPToolset], agent_name: str, agent_tools_names: Optional[List[str]]) -> Optional[List[MCPToolset]]:
        if not agent_tools_names:
            return []
        
        agent_tools = [dict_tools[name] for name in agent_tools_names if name in dict_tools]
        missing_tools = [name for name in agent_tools_names if name not in dict_tools]
        if missing_tools:
            raise ValueError(f"Tools não encontradas para o agente '{agent_name}': {missing_tools}")
        return agent_tools