from enum import Enum

class AgentFlowType(str, Enum):
    """Tipos de ferramentas suportadas."""
    SINGLE = "single"
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"

class ToolsType(str, Enum):
    """Tipos de ferramentas suportadas."""
    SSE = "sse"
    STREAMABLE = "streamable"
    STDIO = "stdio"
    PRE_BUILT = "pre_built"

class PreBuiltTools(str, Enum):
    """Tipos de ferramentas pré-construídas."""
    READ_REPO_CONTEXT = "read_repo_context"
    GOOGLE_SEARCH = "SearchAgent"
    SEND_EMAIL = "send_email_tool"
    GET_DATETIME = "get_current_datetime"
PRE_BUILT_TOOL_VALUES = [tool.value for tool in PreBuiltTools]

class CallbackType(Enum):
    BEFORE_AGENT = "before_agent_callback"
    AFTER_AGENT = "after_agent_callback"
    BEFORE_MODEL = "before_model_callback"
    AFTER_MODEL = "after_model_callback"
    BEFORE_TOOL = "before_tool_callback"
    AFTER_TOOL = "after_tool_callback"