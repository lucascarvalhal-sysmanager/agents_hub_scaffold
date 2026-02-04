import smtplib
from email.message import EmailMessage

from agents.core.domain.email.entities import SendEmailInput
from agents.core.ports.email.email_service import EmailService

class GmailService(EmailService):
    def __init__(self, connection_config: dict):
        self.smtp_user = connection_config.get('user')
        self.smtp_password = connection_config.get('password')

        if not self.smtp_user or not self.smtp_password:
            raise ValueError("Invalid email connection config. It must contain 'user' and 'password'.")

        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, input_data: SendEmailInput) -> None:
        try:
            msg = EmailMessage()
            msg["From"] = self.smtp_user
            msg["To"] = input_data.to
            msg["Subject"] = input_data.subject
            msg.set_content(input_data.body)

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as smtp:
                smtp.starttls()
                smtp.login(self.smtp_user, self.smtp_password)
                smtp.send_message(msg)

        except Exception as e:
            raise ConnectionError(f"Failed to send email: {str(e)}")
