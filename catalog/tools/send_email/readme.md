# Send Email Tool

Envia emails para destinatários usando o serviço de email configurado.

## Visão Geral

| | |
|---|---|
| **Entry Point** | `tool.send_email_tool` |
| **Provider** | Configurável (Gmail, Outlook, etc.) |
| **Dependências** | `google-auth`, `google-auth-oauthlib` |

## Como Funciona

A tool não se conecta diretamente a nenhum serviço de email. Ela consome o serviço que foi configurado no `config.yaml` e instanciado pelo `Container` na inicialização da aplicação. Isso significa que você pode trocar o provedor de email sem alterar a tool, basta mudar a configuração.

```
config.yaml (provider + credenciais)
    │
    ▼
Container → EmailServiceFactory → Adapter do provider (Gmail, Outlook, etc.)
                                        ↑
send_email_tool(to, subject, body) ────┘
```

## Configuração

### 1. Variáveis de ambiente

Defina as credenciais do seu provedor no `.env`:

```bash
EMAIL_USER=seu_email@provedor.com
EMAIL_PASSWORD=sua_senha_ou_token
```

### 2. Configuração no YAML

Em `config/agent/config.yaml`, defina o provider e aponte para as variáveis:

```yaml
tools:
  - name: send_email
    transport: pre_built
    kind: send_email_tool
    provider: gmail                     # ← troque pelo provider desejado
    connection_config:
      user: ${EMAIL_USER}
      password: ${EMAIL_PASSWORD}
```

O `connection_config` é passado diretamente para o adapter do provider. Cada provider pode exigir campos diferentes — consulte a seção de providers abaixo.

## Providers Disponíveis

| Provider | Valor no YAML | Descrição |
|----------|:-------------:|-----------|
| Gmail | `gmail` | SMTP via `smtp.gmail.com:587` |
| Fake Email | `fake_email` | Mock para testes (loga no console, não envia) |

### Gmail

Usa SMTP com TLS. Requer uma [senha de app](https://support.google.com/accounts/answer/185833) (não a senha da conta).

```bash
EMAIL_USER=seu_email@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop     # senha de app (16 caracteres)
```

### Fake Email

Não envia nada. Apenas loga o email no console. Útil para testar o fluxo sem configurar credenciais reais.

```yaml
provider: fake_email
```

## Como Adicionar um Novo Provider

Para adicionar suporte a outro serviço de email (Outlook, SendGrid, SES, etc.):

### 1. Criar o adapter

Crie uma classe que implemente a interface `EmailService` em `agents/core/adapters/email/`:

```python
# agents/core/adapters/email/outlook_service.py

from agents.core.ports.email.email_service import EmailService
from agents.core.domain.email.entities import SendEmailInput

class OutlookService(EmailService):
    def __init__(self, connection_config: dict):
        self.smtp_user = connection_config.get('user')
        self.smtp_password = connection_config.get('password')
        self.smtp_host = "smtp.office365.com"
        self.smtp_port = 587

    def send_email(self, input_data: SendEmailInput) -> None:
        # implementação SMTP similar ao GmailService
        ...
```

### 2. Registrar no enum

Em `agents/core/domain/email/entities.py`:

```python
class EmailProvider(str, Enum):
    GMAIL = "gmail"
    FAKE_EMAIL = "fake_email"
    OUTLOOK = "outlook"              # ← novo
```

### 3. Registrar no factory

Em `agents/core/factories/email_service_factory.py`:

```python
from agents.core.adapters.email.outlook_service import OutlookService

elif provider == EmailProvider.OUTLOOK:
    return OutlookService(connection_config=connection_config)
```

### 4. Configurar no YAML

```yaml
provider: outlook
connection_config:
  user: ${EMAIL_USER}
  password: ${EMAIL_PASSWORD}
```

Nenhuma alteração na tool é necessária pois ela continua chamando `services.email_service` independente do provider.

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

## Registro no Agente

### 1. Enum

O kind está registrado em `agents/core/domain/agent/enums.py`:

```python
class PreBuiltTools(str, Enum):
    SEND_EMAIL = "send_email_tool"
```

### 2. Mapeamento no Builder

Registrado em `agents/core/adapters/agent_builder/adk_tools_builder.py`:

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
