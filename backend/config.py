import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Simulação de e-mail (usado para evitar enviar emails reais na Sprint)
class EmailSettings:
    SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.example.com")
    PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER = os.getenv("EMAIL_USER", "user@example.com")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
