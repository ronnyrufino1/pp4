import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email: str, subject: str, body: str):
    """
    Função simulada para envio de e-mail.
    Neste projeto final, o backend retorna status HTTP 200 com mensagem "E-mail enviado",
    mas não realmente envia emails reais (pode usar smtplib em ambientes controlados).

    """
    msg = MIMEMultipart()
    msg['From'] = 'noreply@example.com'
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    print(f"[SIMULADO] Enviando e-mail para {to_email}")
    return {"detail": "E-mail enviado com sucesso"}
