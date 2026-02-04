from abc import ABC, abstractmethod

from agents.core.domain.email.entities import SendEmailInput
class EmailService(ABC):
    @abstractmethod
    def send_email(self, input_data: SendEmailInput) -> None:
        """
        Sends an email.

        Args:
            to: The recipient's email address.
            subject: The subject of the email.
            body: The body of the email.

        Returns:
            If the email is sent successfully, there is no return.
        """
        pass
