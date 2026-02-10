# Catálogo de Componentes

## Objetivo do Catálogo

Centralizar todos os componentes reutilizáveis para agentes de IA em um único lugar. O catálogo funciona como um registry interno onde qualquer time pode consumir implementações prontas e documentadas, ou contribuir com novas tools, callbacks e skills, seguindo as convenções de governança definidas neste repositório.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    Catálogo de Componentes                      │
│                         README.md                               │
├────────────────────┬────────────────────┬───────────────────────┤
│                    │                    │                       │
│    ┌──────────┐    │    ┌──────────┐    │    ┌─────────────┐    │
│    │  Tools   │    │    │  Skills  │    │    │  Callbacks  │    │
│    │ README.md│    │    │ README.md│    │    │  README.md  │    │
│    └────┬─────┘    │    └────┬─────┘    │    └──────┬──────┘    │
│         │          │         │          │           │           │
│    ┌────┴────┐     │    ┌────┴────┐     │    ┌──────┴──────┐    │
│    │         │     │    │         │     │    │             │    │
│  ┌─┴──┐   ┌──┴─┐   │  ┌─┴──────┐  │     │  ┌─┴──────┐   ┌──┴─┐  │
│  │tool│   │tool│   │  │ skill  │  │     │  │callback│   │cb  │  │
│  │ A  │   │ B  │   │  │ A + B  │  │     │  │   X    │   │ Y  │  │
│  └─┬──┘   └──┬─┘   │  └─┬──────┘  │     │  └─┬──────┘   └──┬─┘  │
│    │         │     │    │         │     │    │             │    │
│ spec.yaml  spec.yaml  instructions.md   │ spec.yaml    spec.yaml│
│ tool.py    tool.py │    │         │     │ callback.py  callback.py
│ req.txt    req.txt │    │         │     │ req.txt      req.txt  │
│ readme     readme  │    │         │     │ readme.md    readme.md│
│         │          │         │          │           │           │
└────────────────────┴────────────────────┴───────────────────────┘
```

## Tipos de Componentes

O catálogo organiza os componentes em três categorias, cada uma com um papel específico no ciclo de vida do agente.

### Tools

Ações isoladas que o agente pode executar. Quem decide quando chamá-la é o agente (o modelo de IA), com base na conversa com o usuário.

**Exemplos:** buscar no Google, enviar email, obter data/hora atual, ler repositório.

```
Usuário pergunta algo → Agente decide qual tool usar → Tool executa e retorna resultado
```

Cada tool contém:

| Arquivo | Propósito |
|---------|-----------|
| `tool.py` | Implementação |
| `spec.yaml` | Metadados (nome, versão, kind, author) |
| `requirements.txt` | Dependências Python |
| `readme.md` | Documentação de uso |
| `__init__.py` | Exports públicos |

Consulte o [README de Tools](./tools/) para detalhes sobre como criar e registrar uma nova tool.

### Skills

Fluxos que combinam múltiplas tools com instruções específicas. Uma skill orquestra a execução de tools em sequência para resolver tarefas mais complexas.

**Exemplo:** uma skill de "pesquisa inteligente" que usa a tool `google_search`, processa os resultados e gera um relatório estruturado.

```
Skill recebe um objetivo → Chama tool A → Processa resultado → Chama tool B → Entrega resultado final
```

Cada skill contém:

| Arquivo | Propósito |
|---------|-----------|
| `instructions.md` | Instruções do fluxo |
| `spec.yaml` | Metadados e dependências |
| `readme.md` | Documentação |

### Callbacks

Hooks automáticos que executam em eventos do ciclo de vida do agente. Diferente de tools (que o agente decide chamar), callbacks são executados automaticamente pelo framework em momentos específicos.

**Exemplos:** capturar métricas antes/depois de cada chamada ao modelo, traduzir pensamentos para português, persistir dados de performance.

```
[before_model] → Modelo processa → [after_model] → Agente responde → [after_agent]
```

Cada callback contém:

| Arquivo | Propósito |
|---------|-----------|
| `callback.py` ou `hooks.py` | Implementação |
| `spec.yaml` | Metadados e configuração |
| `requirements.txt` | Dependências Python |
| `readme.md` | Documentação |

## Hierarquia

```
Callbacks executam automaticamente em eventos do framework
    │
    ├── podem acionar Skills
    │       │
    │       └── que orquestram Tools
    │               │
    │               └── que executam ações isoladas
    │
Tools são chamadas diretamente pelo agente
```

| Componente | Quem chama | Quando |
|------------|------------|--------|
| **Tool** | O agente (modelo de IA) | Quando o agente decide que precisa |
| **Skill** | Uma tool ou um callback | Quando um fluxo complexo é necessário |
| **Callback** | O framework (automático) | Em eventos do ciclo de vida |

## Governança

Para contribuir com o catálogo, todo componente deve seguir estas regras:

1. **Estrutura padronizada** — respeitar os arquivos obrigatórios de cada tipo
2. **spec.yaml preenchido** — campos obrigatórios: `name`, `version`, `description`, `author` e `entry_point`. Campos extras podem ser adicionados quando necessário para dar instruções (ex: `requires_auth`, `external_deps`, `model`)
3. **readme.md completo** — visão geral, como funciona, uso, configuração e registro
4. **Código isolado** — a implementação (tool.py, callback.py) deve ter o mínimo de dependências externas

## Estrutura do Repositório

```
catalog/
├── README.md
├── tools/
│   ├── README.md
│   ├── tool_1/
│   ├── tool_2/
│   └── tool_n/
├── skills/
│   ├── README.md
│   ├── skill_1/
│   └── skill_n/
└── callbacks/
    ├── README.md
    ├── callback_1/
    └── callback_n/
```
