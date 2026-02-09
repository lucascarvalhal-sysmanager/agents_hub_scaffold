from agents.core.ports.email.email_service import EmailService
from agents.core.adapters.email.gmail_service import GmailService
from agents.core.adapters.email.fake_mail_service import FakeMailService
from agents.core.domain.email.entities import EmailProvider


class EmailServiceFactory:
    @staticmethod
    def get_email_service(provider: str, connection_config: dict) -> EmailService:
        provider = provider.lower()

        if provider == EmailProvider.GMAIL:
            return GmailService(connection_config=connection_config)
        elif provider == EmailProvider.FAKE_EMAIL:
            return FakeMailService(connection_config=connection_config)
        else:
            raise ValueError(f"Unsupported email provider: {provider}")
