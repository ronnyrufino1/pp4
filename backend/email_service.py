import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com").replace('"', '').strip()
SMTP_PORT = int(os.getenv("EMAIL_PORT", 587))
SMTP_USER = os.getenv("EMAIL_USER", "").replace('"', '').strip()
SMTP_PASSWORD = os.getenv("EMAIL_PASSWORD", "").replace('"', '').strip()

def enviar_email_boas_vindas(email_destino: str, nome_usuario: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("Aviso: Credenciais de e-mail não configuradas. Ignorando envio.")
        return

    mensagem = MIMEMultipart()
    mensagem["From"] = SMTP_USER
    mensagem["To"] = email_destino
    mensagem["Subject"] = f"Bem-vindo(a) ao LegalTech, {nome_usuario}!"

    corpo = f"Olá, {nome_usuario}!\n\nSeu cadastro no LegalTech foi realizado com sucesso."
    mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as servidor:
            servidor.starttls()
            servidor.login(SMTP_USER, SMTP_PASSWORD)
            servidor.sendmail(SMTP_USER, email_destino, mensagem.as_string())
        print(f"E-mail de boas-vindas enviado para {email_destino}")
    except Exception as e:
        print(f"Erro ao enviar boas-vindas: {e}")


def enviar_email_movimentacao(email_destino: str, nome_cliente: str, numero_processo: str, nova_descricao: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("Aviso: Credenciais de e-mail ausentes no .env. Ignorando notificação.")
        return
    corpo = f"""Olá, {nome_cliente}!

    Informamos que o seu processo número 
    {numero_processo} 
    sofreu uma nova atualização.

    Nova movimentação registrada: "{nova_descricao}" 
    
    Atenciosamente, 
    Equipe LegalTech."""

    mensagem = MIMEText(corpo, "plain", "utf-8")
    
    mensagem["From"] = Header(SMTP_USER, "utf-8")
    mensagem["To"] = Header(email_destino, "utf-8")
    mensagem["Subject"] = Header(f"LegalTech: Movimentação no Processo Nº {numero_processo}", "utf-8")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as servidor:
            servidor.starttls()
            servidor.login(SMTP_USER, SMTP_PASSWORD)
            
            servidor.sendmail(SMTP_USER, email_destino, mensagem.as_string())
            
        print(f"Notificação de processo enviada com sucesso para {email_destino}!")
    except Exception as e:
        print(f"Erro ao enviar e-mail de movimentação: {e}")