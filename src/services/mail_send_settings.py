from src.config import Settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL


class EmailSender:
    def __init__(self, settings: Settings):
        self.settings = settings

    def send_email(self, to_email: str, subject: str, body: str, html: bool = False):
        message = MIMEMultipart()
        message["From"] = self.settings.FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject

        # Добавляем контент письма
        if html:
            message.attach(MIMEText(body, "html"))
        else:
            message.attach(MIMEText(body, "plain"))

        # Отправляем письмо
        with SMTP_SSL(self.settings.SMTP_SERVER, self.settings.SMTP_PORT) as smtp:
            smtp.login(self.settings.SMTP_USERNAME, self.settings.SMTP_PASSWORD)
            smtp.sendmail(self.settings.FROM_EMAIL, to_email, message.as_string())
