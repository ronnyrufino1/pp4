import os
import re
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, Response, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, create_engine, Session, or_, select, func
from dotenv import load_dotenv
from schemas import (
    ProcessoUpdate, UsuarioCreate, UsuarioRead, 
    ClienteCreate, ClienteRead, 
    ProcessoCreate, ProcessoRead,
    ProcessoComCliente, ProcessoPaginadoResponse  
)
from models import Usuario, Cliente, Processo
import crud
from security import gerar_hash_senha, verificar_senha
from auth import criar_token_acesso, obter_usuario_atual, RequererRole
from database import engine, get_session
from email_service import enviar_email_boas_vindas, enviar_email_movimentacao
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
origins = [
    "https://ronnyrufino1.github.io",
    "https://pp4.railway.internal", # Se ainda testar local
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def raiz():
    return {"status": "Online", "documentacao": "/docs"}


CODIGO_MESTRE_ADMIN = "LegalTech2026" # Código de segurança

# ==========================================
# REQUISITO 2 - CADASTRO DE USUÁRIO (ABERTO AO PÚBLICO)
# ==========================================

@app.post("/usuarios", response_model=UsuarioRead, status_code=201)
def cadastrar_usuario_api(
    usuario_in: UsuarioCreate, 
    background_tasks: BackgroundTasks, # Permite o envio do e-mail em segundo plano
    session: Session = Depends(get_session)
):
    # 1. VALIDAÇÃO: Verifica se o e-mail já está cadastrado no sistema (Evita duplicidade)
    email_existe = session.exec(select(Usuario).where(Usuario.email == usuario_in.email)).first()
    if email_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="O endereço de e-mail informado já está em uso por outra conta."
        )
        
    cpf_existe = session.exec(select(Usuario).where(Usuario.cpf == usuario_in.cpf)).first()
    if cpf_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este CPF já está cadastrado no sistema."
        )

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
        
        background_tasks.add_task(enviar_email_boas_vindas, novo_usuario.email, novo_usuario.nome)
        
        return novo_usuario
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Erro de integridade ao salvar o usuário.")    
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


@app.get("/clientes/{id}", response_model=ClienteRead, dependencies=[Depends(RequererRole(["adm", "comum"]))])
def buscar_cliente_api(id: int, session: Session = Depends(get_session)):
    try:
        return crud.buscar_cliente(id_=id, session=session) # Mantém id_=id para o seu crud
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/clientes/{id}", response_model=ClienteRead, dependencies=[Depends(RequererRole(["adm"]))])
def atualizar_cliente_api(id: int, data: ClienteCreate, session: Session = Depends(get_session)):
    try:
        return crud.atualizar_cliente(id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    

@app.delete("/clientes/{id}", status_code=204, dependencies=[Depends(RequererRole(["adm"]))])
def deletar_cliente_api(id: int):
    try:
        crud.deletar_cliente(id)
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


@app.get("/processos/", response_model=ProcessoPaginadoResponse)  
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


@app.get("/processos/{id}", response_model=ProcessoRead)
def buscar_processo_api(
    id: int, 
    session: Session = Depends(get_session), 
    usuario_logado: Usuario = Depends(RequererRole(["adm", "comum"]))
):
    try:
        return crud.buscar_processo(id_=id, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/processos/{id}", response_model=ProcessoRead)
def atualizar_processo_api(
    id: int,
    data: ProcessoUpdate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    usuario_logado: Usuario = Depends(RequererRole(["adm", "comum"]))
):
    try:
        proc_atualizado = crud.atualizar_processo(id_=id, data=data, session=session)
        
        if proc_atualizado and proc_atualizado.cliente_id:
            from models import Cliente 
            cliente = session.get(Cliente, proc_atualizado.cliente_id)
            
            if cliente and cliente.email:
                num_proc = proc_atualizado.numero_cnj or proc_atualizado.numero or str(id)
                
                from email_service import enviar_email_movimentacao
                
                background_tasks.add_task(
                    enviar_email_movimentacao,
                    email_destino=cliente.email,
                    nome_cliente=cliente.nome,
                    numero_processo=num_proc,
                    nova_descricao=data.descricao
                )
                print(f"==> [BACKEND] Disparo de e-mail agendado para: {cliente.email}")

        return proc_atualizado
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.delete("/processos/{id}", status_code=204)
def deletar_processo_api(
    id: int, 
    session: Session = Depends(get_session), 
    usuario_logado: Usuario = Depends(RequererRole(["adm", "comum"]))
):
    try:
        crud.deletar_processo(id_=id, session=session)
        return Response(status_code=204)
    except ValueError:
        raise HTTPException(status_code=404, detail="Processo não encontrado ou já deletado.")