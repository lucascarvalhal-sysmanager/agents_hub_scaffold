# Tools Catalog

Repositório centralizado de ferramentas reutilizáveis para agentes de IA. Cada tool é um componente isolado, versionado e documentado, pronto para ser integrado por qualquer time da organização.

## Conceito

O catálogo funciona como um **registry interno de ferramentas**. A ideia é que todos os times compartilhem e contribuam com tools, evitando retrabalho e garantindo padrões de qualidade.

```
Seu Agente → config.yaml → pre_built tool → catalog/tools/sua_tool/
```

O agente não conhece a implementação — ele só sabe o `kind` configurado no YAML. O catálogo resolve o resto.

## Tools Disponíveis

| Tool | Descrição |
|------|-----------|
| [google_search](./google_search/) | Agente especializado em buscas no Google |
| [read_repo_context](./read_repo_context/) | Lê contexto de repositórios Git via repomix |
| [send_email](./send_email/) | Envio de emails via Gmail |
| [datetime_tool](./datetime_tool/) | Data e hora atual com suporte multi-idioma |

## Estrutura de uma Tool

Cada tool segue a mesma estrutura:

```
tool_name/
├── __init__.py        # Exports públicos
├── tool.py            # Implementação
├── spec.yaml          # Metadados e configuração
├── requirements.txt   # Dependências Python
└── readme.md          # Documentação
```

| Arquivo | Obrigatório | Propósito |
|---------|:-----------:|-----------|
| `__init__.py` | Sim | Define o que é público via `__all__` |
| `tool.py` | Sim | Implementação da tool |
| `spec.yaml` | Sim | Metadados, entry point e configuração |
| `requirements.txt` | Sim | Dependências (vazio se não tiver) |
| `readme.md` | Sim | Documentação de uso |

## Como Criar uma Nova Tool

### 1. Criar a estrutura

```bash
mkdir catalog/tools/minha_tool
touch catalog/tools/minha_tool/{__init__.py,tool.py,spec.yaml,requirements.txt,readme.md}
```

### 2. Implementar a tool

```python
# catalog/tools/minha_tool/tool.py

def minha_tool(param: str) -> str:
    """Descrição curta do que faz."""
    # implementação
    return resultado
```

### 3. Exportar no __init__.py

```python
# catalog/tools/minha_tool/__init__.py

from .tool import minha_tool

__all__ = ["minha_tool"]
```

### 4. Preencher o spec.yaml

```yaml
metadata:
  name: minha_tool
  version: 1.0.0
  description: O que a tool faz
  author: Eneva Foundations IA
  kind: function_tool

entry_point: tool.minha_tool

config:
  # configurações específicas
```

### 5. Registrar no agente

Para que o agente consiga usar a tool, é necessário registrá-la no framework:

**a) Adicionar o enum** em `agents/core/domain/agent/enums.py`:

```python
class PreBuiltTools(str, Enum):
    MINHA_TOOL = "minha_tool"
```

**b) Mapear no builder** em `agents/core/adapters/agent_builder/adk_tools_builder.py`:

```python
PreBuiltTools.MINHA_TOOL: lambda _: minha_tool_function,
```

**c) Configurar no** `config/agent/config.yaml`:

```yaml
tools:
  - name: minha_tool
    transport: pre_built
    kind: minha_tool
```

**d) Adicionar na lista de tools do agente:**

```yaml
agent:
  tools:
    - minha_tool
```

### 6. Documentar

Escreva o `readme.md` seguindo o padrão das tools existentes. Consulte o [datetime_tool](./datetime_tool/) como referência.

## Convenções

- **Erros como retorno** — tools retornam string de erro em vez de levantar exceção, para o agente receber feedback sem quebrar
- **Docstring em uma linha** — descreve o que faz, sem repetir a assinatura
- **Uma função resolve** — não criar múltiplas funções quando uma dá conta
- **Dados separados de lógica** — variações em constantes, função só processa
- **`kind` no YAML** — usar `kind` (não `type`) para identificar tools pre_built
