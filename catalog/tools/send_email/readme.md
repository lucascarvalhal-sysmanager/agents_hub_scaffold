# Send Email Tool

Ferramenta para envio de emails.

## Funcionalidade

- Envia emails usando serviço configurado
- Suporta diferentes providers (Gmail, etc)
- Integrado com o container de serviços do agente

## Uso

```python
from catalog.tools.send_email import send_email_tool

# Usando com container de serviços (automático)
send_email_tool(
    to="destinatario@email.com",
    subject="Assunto do email",
    body="Conteúdo do email"
)

# Usando com serviço customizado
send_email_tool(
    to="destinatario@email.com",
    subject="Assunto",
    body="Conteúdo",
    email_service=meu_servico_email
)
```

## Parâmetros

| Parâmetro | Descrição | Obrigatório |
|-----------|-----------|-------------|
| to | Email do destinatário | Sim |
| subject | Assunto do email | Sim |
| body | Conteúdo do email | Sim |
| email_service | Serviço de email | Não |

## Configuração

Requer configuração do serviço de email no `config.yaml`:

```yaml
tools:
  - name: send_email
    transport: pre_built
    type: send_email
    provider: gmail
    connection_config:
      credentials_path: path/to/credentials.json
```

## Erros

- `ConnectionError`: Serviço de email não configurado
