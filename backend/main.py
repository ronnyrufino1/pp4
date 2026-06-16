import os
import re
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, create_engine, Session, or_, select, func
from dotenv import load_dotenv
from backend.schemas import (
    ProcessoUpdate, UsuarioCreate, UsuarioRead, 
    ClienteCreate, ClienteRead, 
    ProcessoCreate, ProcessoRead,
    ProcessoComCliente, ProcessoPaginadoResponse  
)
from backend.models import Usuario, Cliente, Processo
from backend import crud
from backend.security import gerar_hash_senha, verificar_senha
from backend.auth import criar_token_acesso, obter_usuario_atual, RequererRole
from backend.database import engine, get_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Servidor iniciando... Criando tabelas!")
    SQLModel.metadata.create_all(engine)
    yield 

app = FastAPI(
    title="LegalTech - Sistema de Gestão Jurídica",
    version="1.0",
    lifespan=lifespan
)

# ==============================================
# ==============================================
# CONFIGURAÇÃO DE CORS PARA PERMITIR O FRONTEND
# ==============================================
# ==============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def raiz():
    return {"status": "Online", "documentacao": "/docs"}


CODIGO_MESTRE_ADMIN = "LegalTech2026" # Código de segurança

@app.post("/auth/cadastro", response_model=UsuarioRead, status_code=201)
def cadastrar_usuario_api(usuario_in: UsuarioCreate, session: Session = Depends(get_session)):
    try:
        perfil_final = "comum"
        if usuario_in.role == "adm":
            if usuario_in.codigo_admin != CODIGO_MESTRE_ADMIN:
                raise HTTPException(
                    status_code=403, 
                    detail="Código de Autenticação Admin incorreto ou inválido."
                )
            perfil_final = "adm"

        senha_criptografada = gerar_hash_senha(usuario_in.senha)
        
        novo_usuario = Usuario(
            nome=usuario_in.nome,
            email=usuario_in.email,
            cpf=usuario_in.cpf,
            hashed_password=senha_criptografada,
            role=perfil_final
        )
        
        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)
        return novo_usuario
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Este CPF já está cadastrado.")
    
# ==========================================
# ==========================================
# ROTAS - AUTENTCAÇÁO
# ==========================================
# ==========================================

@app.post("/auth/login")
def login_api(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    cpf_limpo = re.sub(r'\D', '', form_data.username)
    
    usuario = session.exec(select(Usuario).where(Usuario.cpf == cpf_limpo)).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="CPF ou senha incorretos.")
        
    if not verificar_senha(form_data.password, usuario.hashed_password):
        raise HTTPException(status_code=400, detail="CPF ou senha incorretos.")
        
    token_acesso = criar_token_acesso(data={"sub": usuario.cpf, "nome": usuario.nome})
    
    return {"access_token": token_acesso, "token_type": "bearer"}


# ==========================================
# ==========================================
# ROTAS - CLIENTES
# ==========================================
# ==========================================

@app.post("/clientes/", response_model=ClienteRead, status_code=201, dependencies=[Depends(RequererRole(["adm", "comum"]))])
def criar_cliente_api(cliente: ClienteCreate, session: Session = Depends(get_session)):
    return crud.criar_cliente(data=cliente, session=session)


@app.get("/clientes/", dependencies=[Depends(RequererRole(["adm", "comum"]))])
def listar_clientes_api(
    session: Session = Depends(get_session),
    limit: int = 10,
    offset: int = 0
):
    total_registros = session.exec(select(func.count(Cliente.id))).one()
    
    clientes_paginados = crud.listar_clientes(session=session, limit=limit, offset=offset)
    
    return {
        "total": total_registros,
        "dados": clientes_paginados
    }


@app.get("/clientes/{id_}", response_model=ClienteRead, dependencies=[Depends(RequererRole(["adm", "comum"]))])
def buscar_cliente_api(id_: int, session: Session = Depends(get_session)):
    try:
        return crud.buscar_cliente(id_=id_, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/clientes/{id_}", response_model=ClienteRead, dependencies=[Depends(RequererRole(["adm"]))])
def atualizar_cliente_api(id_: int, data: ClienteCreate, session: Session = Depends(get_session)):
    try:
        return crud.atualizar_cliente(id_, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    

@app.delete("/clientes/{id_}", status_code=204, dependencies=[Depends(RequererRole(["adm"]))])
def deletar_cliente_api(id_: int):
    try:
        crud.deletar_cliente(id_)
        return Response(status_code=204)
    except ValueError:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    

# ==========================================
# ROTAS - PROCESSOS
# ==========================================

@app.post("/processos/", response_model=ProcessoRead, status_code=201)
def criar_processo_api(
    proc: ProcessoCreate, 
    session: Session = Depends(get_session), 
    usuario_logado: Usuario = Depends(RequererRole(["adm"]))
):
    cliente_existe = session.get(Cliente, proc.cliente_id)
    if not cliente_existe:
        raise HTTPException(
            status_code=404, 
            detail=f"Não foi possível criar o processo. O Cliente com ID {proc.cliente_id} não existe."
        )
    try:
        return crud.criar_processo(data=proc, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/processos/", response_model=ProcessoPaginadoResponse)  # <-- Agora o tipo será reconhecido!
def listar_processos_api(
    limit: int = 10, 
    offset: int = 0, 
    termo: Optional[str] = None, 
    status: Optional[str] = None, 
    session: Session = Depends(get_session)
):
    processos_paginados = crud.listar_processos(session, limit=limit, offset=offset, termo=termo, status=status)
    
    statement_total = select(func.count(Processo.id)).join(Cliente, Processo.cliente_id == Cliente.id, isouter=True)
    if status and status != "Todos":
        statement_total = statement_total.where(Processo.status == status)
    if termo:
        busca_lk = f"%{termo}%"
        statement_total = statement_total.where(
            or_(Processo.numero_cnj.ilike(busca_lk), Processo.descricao.ilike(busca_lk), Cliente.nome.ilike(busca_lk))
        )
    total_registros = session.exec(statement_total).one()

    return {
        "total": total_registros,
        "dados": processos_paginados
    }


@app.get("/processos/{id_}", response_model=ProcessoRead)
def buscar_processo_api(
    id_: int, 
    session: Session = Depends(get_session), 
    usuario_logado: Usuario = Depends(RequererRole(["adm", "comum"]))
):
    try:
        return crud.buscar_processo(id_=id_, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/processos/{id_}", response_model=ProcessoRead)
def atualizar_processo_api(
    id_: int, 
    data: ProcessoUpdate, 
    session: Session = Depends(get_session),
    usuario_logado: Usuario = Depends(RequererRole(["adm", "comum"]))
):
    try:
        return crud.atualizar_processo(id_=id_, data=data, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.delete("/processos/{id_}", status_code=204)
def deletar_processo_api(
    id_: int, 
    session: Session = Depends(get_session), 
    usuario_logado: Usuario = Depends(RequererRole(["adm", "comum"]))
):
    try:
        crud.deletar_processo(id_=id_, session=session)
        return Response(status_code=204)
    except ValueError:
        raise HTTPException(status_code=404, detail="Processo não encontrado ou já deletado.")