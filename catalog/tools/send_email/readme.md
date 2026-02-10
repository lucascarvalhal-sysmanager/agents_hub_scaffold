# Send Email Tool

Envia emails para destinatários usando o serviço de email configurado.

## Visão Geral

| | |
|---|---|
| **Entry Point** | `tool.send_email_tool` |
| **Provider** | Gmail (configurável) |
| **Dependências** | `google-auth`, `google-auth-oauthlib` |

## Como Funciona

A tool utiliza o padrão de injeção de dependências do projeto. O serviço de email é instanciado pelo `Container` na inicialização da aplicação, com base no provider e credenciais configurados no YAML. A tool apenas consome o serviço já pronto.

```
config.yaml → Container → EmailServiceFactory → GmailService
                                                      ↑
send_email_tool(to, subject, body) ──────────────────┘
```

## Configuração

Defina as credenciais do email via variáveis de ambiente no `.env`:

```bash
EMAIL_USER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_app
```

> Para Gmail, use uma [senha de app](https://support.google.com/accounts/answer/185833) em vez da senha da conta.

## Uso

### Importando a função

```python
from catalog.tools.send_email import send_email_tool
```

### Enviando um email

```python
resultado = send_email_tool(
    to="destinatario@email.com",
    subject="Relatório diário",
    body="Segue o relatório de performance do agente."
)
# "Email enviado com sucesso para destinatario@email.com."
```

### Assinatura

```python
def send_email_tool(to: str, subject: str, body: str) -> str
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `to` | `str` | Endereço de email do destinatário |
| `subject` | `str` | Assunto do email |
| `body` | `str` | Conteúdo do email em texto simples |

**Retorno:** string confirmando o envio ou descrevendo o erro.

### Tratamento de Erros

A tool retorna strings de erro em vez de exceções, seguindo a convenção do catálogo:

```python
"Erro: serviço de email não configurado."
"Erro ao enviar email para destinatario@email.com: <detalhe>"
```

## Registro no Agente

### 1. Enum

O kind está registrado em `agents/core/domain/agent/enums.py`:

```python
class PreBuiltTools(str, Enum):
    SEND_EMAIL = "send_email_tool"
```

### 2. Mapeamento no Builder

Registrado em `agents/core/adapters/agent_builder/adk_tools_builder.py`, apontando diretamente para a tool do catálogo:

```python
PreBuiltTools.SEND_EMAIL: lambda _: catalog_send_email.send_email_tool,
```

### 3. Configuração no YAML

Em `config/agent/config.yaml`:

```yaml
agent:
  tools:
    - send_email

tools:
  - name: send_email
    transport: pre_built
    kind: send_email_tool
    provider: gmail
    connection_config:
      user: ${EMAIL_USER}
      password: ${EMAIL_PASSWORD}
```

O `Container` lê essa configuração e instancia o `GmailService` automaticamente via `EmailServiceFactory`.

## Providers Disponíveis

| Provider | Enum | Descrição |
|----------|------|-----------|
| `gmail` | `EmailProvider.GMAIL` | Envio via SMTP do Gmail |
| `fake_email` | `EmailProvider.FAKE_EMAIL` | Mock para testes (não envia de verdade) |

