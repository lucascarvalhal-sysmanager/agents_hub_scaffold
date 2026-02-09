from pydantic import BaseModel, Field
from enum import Enum

class EmailProvider(str, Enum):
    GMAIL="gmail"
    FAKE_EMAIL="fake_email"

class SendEmailInput(BaseModel):
    to: str = Field(..., description="Endereço de email do destinatário")
    subject: str = Field(..., description="Assunto do e-mail")
    body: str = Field(..., description="Conteúdo do e-mail em texto simples")