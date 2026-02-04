# Skills

Combinações de tools e callbacks com instruções específicas para casos de uso.

## Skills Disponíveis

| Skill | Descrição | Triggers | Tools usadas |
|-------|-----------|----------|--------------|
| [analyze_performance](./analyze_performance/) | Analisa performance com métricas e recomendações | `/performance` | Nenhuma |
| [smart_search](./smart_search/) | Pesquisa inteligente com resultados estruturados | `/search`, `/pesquisar` | google_search |

## O que são Skills?

Skills são **receitas automatizadas** que combinam múltiplas ferramentas (tools) e lógica para executar tarefas complexas.

```
┌─────────────────────────────────────────┐
│              SKILL                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Tool 1  │→│ Lógica  │→│ Tool 2  │   │
│  └─────────┘ └─────────┘ └─────────┘   │
│         ↓         ↓         ↓          │
│     [ Output estruturado ]              │
└─────────────────────────────────────────┘
```

## Estrutura de cada Skill

```
skill_name/
├── __init__.py           # Exports
├── skill.py              # Código principal
├── spec.yaml             # Metadados e configuração
├── prompts/
│   ├── instructions.md   # Instruções de execução
│   └── agent_prompt.md   # Prompt para sub-agentes (opcional)
├── requirements.txt      # Dependências Python
└── readme.md             # Documentação
```

## Como usar uma Skill

### Via Trigger (conversa)
```
Usuário: /performance
Agente: [Executa skill automaticamente]
```

### Via Código
```python
from catalog.skills.analyze_performance import get_performance_report_md

report = get_performance_report_md(state=session_state)
```

## Como adicionar uma nova Skill

1. Crie uma pasta com o nome da skill
2. Adicione os arquivos obrigatórios
3. Preencha o `spec.yaml` com os metadados
4. Documente no `readme.md`
5. Atualize este README

## Skills vs Tools vs Callbacks

| Tipo | Quando usar | Exemplo |
|------|-------------|---------|
| **Tool** | Ação simples e isolada | `google_search`, `send_email` |
| **Callback** | Automático em eventos do ciclo de vida | `finops_after_model`, `translate_thought` |
| **Skill** | Fluxo complexo com múltiplas etapas | `analyze_performance`, `review_pr` |
