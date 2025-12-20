class SMTPClient:  # pragma: no cover
    def send(self, subject: str, text: str, email_address: str) -> bool:
        """
        Send an email via SMTP.

        Args:
            subject: Email subject
            text: Email body text
            email_address: Recipient email address

        Returns:
            True if email was sent successfully, False otherwise
        """
        return False
