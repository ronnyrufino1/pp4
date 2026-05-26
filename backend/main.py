import os
from contextlib import asynccontextmanager
from typing import List
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

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

def get_session():
    with Session(engine) as session:
        yield session

from .schemas import ClienteCreate, ClienteRead, ProcessoCreate, ProcessoRead
from . import crud
from .models import Cliente, Processo
from .schemas import ClienteCreate, ClienteRead, ProcessoCreate, ProcessoRead
from . import crud


# ==========================================
# ==========================================
# ROTAS - CLIENTES
# ==========================================
# ==========================================

@app.post("/clientes/", response_model=ClienteRead, status_code=201)
def criar_cliente_api(cliente: ClienteCreate, session: Session = Depends(get_session)):
    return crud.criar_cliente(data=cliente, session=session)

@app.get("/clientes/", response_model=List[ClienteRead])
def listar_clientes_api(session: Session = Depends(get_session)):
    return crud.listar_clientes(session=session)

@app.get("/clientes/{id_}", response_model=ClienteRead)
def buscar_cliente_api(id_: int, session: Session = Depends(get_session)):
    try:
        return crud.buscar_cliente(id_=id_, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/clientes/{id_}", response_model=ClienteRead)
def atualizar_cliente_api(id_: int, data: ClienteCreate, session: Session = Depends(get_session)):
    try:
        return crud.atualizar_cliente(id_, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

@app.delete("/clientes/{id_}", status_code=204)
def deletar_cliente_api(id_: int):
    try:
        crud.deletar_cliente(id_)
        return Response(status_code=204)
    except ValueError:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")


# ==========================================
# ==========================================
# ROTAS - PROCESSOS
# ==========================================
# ==========================================

@app.post("/processos/", response_model=ProcessoRead, status_code=201)
def criar_processo_api(proc: ProcessoCreate, session: Session = Depends(get_session)):
    try:
        return crud.criar_processo(data=proc, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/processos/", response_model=List[ProcessoRead])
def listar_processos_api(session: Session = Depends(get_session)):
    return crud.listar_processos(session=session)

@app.get("/processos/{id_}", response_model=ProcessoRead)
def buscar_processo_api(id_: int, session: Session = Depends(get_session)):
    try:
        return crud.buscar_processo(id_=id_, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/processos/{id_}", response_model=ProcessoRead)
def atualizar_processo_api(id_: int, data: ProcessoCreate, session: Session = Depends(get_session)):
    try:
        return crud.atualizar_processo(id_=id_, data=data, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/processos/{id_}", status_code=204)
def deletar_processo_api(id_: int, session: Session = Depends(get_session)):
    try:
        crud.deletar_processo(id_=id_, session=session)
        return Response(status_code=204)
    except ValueError:
        raise HTTPException(status_code=404, detail="Processo não encontrado ou já deletado.") 

@app.get("/processos/cliente/{cliente_id}", response_model=List[ProcessoRead])
def listar_processos_por_cliente_api(cliente_id: int, session: Session = Depends(get_session)):
    return crud.processos_por_cliente(cliente_id=cliente_id, session=session)