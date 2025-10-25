import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.utils.mail_send_settings import EmailSender
from src.config import settings

# -----------------------------
# Настройка Jinja2
# -----------------------------

# Путь к корню проекта (где лежит папка src и templates)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /src/src
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")  # /src/src/templates

# Проверка
print("Looking for templates in:", TEMPLATES_DIR)
print("Available templates:", os.listdir(TEMPLATES_DIR))

# Jinja2 Environment
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


# -----------------------------
# Функция рендера шаблона
# -----------------------------
def render_checkin_email(data: dict) -> str:
    template = env.get_template("checkin_email.html")
    return template.render(**data)


# -----------------------------
# Функция отправки писем
# -----------------------------
async def send_checkin_emails(bookings):
    sender = EmailSender(settings)
    for booking in bookings:
        html_body = render_checkin_email(booking)
        subject = f"Ваше бронирование — {booking['room_title']}"
        print(f"---------------{booking['email']}")
        sender.send_email(to_email=booking["email"], subject=subject, body=html_body, html=True)
