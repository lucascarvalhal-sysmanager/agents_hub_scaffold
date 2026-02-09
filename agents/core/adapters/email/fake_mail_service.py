import logging

from agents.core.ports.email.email_service import EmailService
from agents.core.domain.email.entities import SendEmailInput

logger = logging.getLogger(__name__)

class FakeMailService(EmailService):
    def __init__(self, connection_config: dict):        
        logger.debug("FakeMailService initialized.")

    def send_email(self, input_data: SendEmailInput) -> dict:
        logger.info(f"--- FAKE EMAIL SENT ---")
        logger.info(f"To: {input_data.to}")
        logger.info(f"Subject: {input_data.subject}")
        logger.info(f"Body: {input_data.body}")
        logger.info(f"-----------------------")
        return {"status": "success", "message": "Fake email sent successfully."}