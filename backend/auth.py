# === backend/auth.py ===
from datetime import datetime, timedelta, timezone
import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select
from dotenv import load_dotenv
from backend.database import get_session
from backend.models import Usuario

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "uma_chave_secreta_e_muito_longa_para_seguranca_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def criar_token_acesso(data: dict) -> str:
    dados_para_criptografar = data.copy()
    
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    dados_para_criptografar.update({"exp": tempo_expiracao})
    
    token_jwt = jwt.encode(dados_para_criptografar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

def obter_usuario_atual(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> Usuario:
    erro_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido, expirado ou não fornecido.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        cpf: str = payload.get("sub")
        if cpf is None:
            raise erro_credenciais
    except InvalidTokenError:
        raise erro_credenciais
        
    usuario = session.exec(select(Usuario).where(Usuario.cpf == cpf)).first()
    if usuario is None:
        raise erro_credenciais
        
    return usuario

def verificar_se_eh_admin(usuario_atual: Usuario = Depends(obter_usuario_atual)) -> Usuario:
    if usuario_atual.role != "adm":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Esta operação é exclusiva para administradores."
        )
    return usuario_atual

class RequererRole:
    def __init__(self, roles_permitidos: list[str]):
        self.roles_permitidos = roles_permitidos

    def __call__(self, usuario_atual: Usuario = Depends(obter_usuario_atual)) -> Usuario:
        if usuario_atual.role not in self.roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Você não tem permissão para executar esta ação."
            )
        return usuario_atual