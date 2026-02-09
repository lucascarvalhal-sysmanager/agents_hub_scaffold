class RepoReadError(Exception):
    """Erro genérico ao ler o contexto de um repositório."""
    pass

class AgentConfigurationError(Exception):
    """Erro ao processar a configuração do agente."""
    pass

class ToolResolutionError(Exception):
    """Erro ao resolver ou carregar ferramentas."""
    pass

class CallbackResolutionError(Exception):
    """Erro ao resolver ou carregar callbacks."""
    pass

class AgentCreationError(Exception):
    """Erro genérico durante a criação do agente."""
    pass