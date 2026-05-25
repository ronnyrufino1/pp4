from typing import List, Optional
from sqlmodel import Session, select
from backend.main import get_session
from .models import Cliente, Processo
from .schemas import ClienteCreate, ProcessoCreate
from .email_service import send_email


# ==========================================
# ==========================================
# CRUD DE CLIENTES
# ==========================================
# ==========================================

def listar_clientes(session: Session) -> List[Cliente]:
    return session.exec(select(Cliente)).all()

def criar_cliente(data: ClienteCreate, session: Session) -> Cliente:
    dump_data = data.model_dump() if hasattr(data, "model_dump") else data.dict()
    novo = Cliente(**dump_data)
    session.add(novo)
    session.commit()
    session.refresh(novo)
    return novo

def buscar_cliente(id_: int, session: Session) -> Cliente:
    c = session.get(Cliente, id_)
    if not c: 
        raise ValueError("Cliente não encontrado")
    return c

def atualizar_cliente(id_: int, data: ClienteCreate, session: Optional[Session] = None) -> Cliente:
    if session is None:
        from backend.main import engine
        with Session(engine) as nova_sessao:
            c = buscar_cliente(id_, nova_sessao)
            for k, v in data.model_dump().items():
                setattr(c, k, v)
            nova_sessao.add(c)
            nova_sessao.commit()
            nova_sessao.refresh(c)
            return c
    else:
        c = buscar_cliente(id_, session)
        for k, v in data.model_dump().items():
            setattr(c, k, v)
        session.add(c)
        session.commit()
        session.refresh(c)
        return c
    
def deletar_cliente(id_: int, session: Optional[Session] = None):
    if session is None:
        from backend.main import engine
        with Session(engine) as nova_sessao:
            c = buscar_cliente(id_, nova_sessao)
            nova_sessao.delete(c)
            nova_sessao.commit()
    else:
        c = buscar_cliente(id_, session)
        session.delete(c)
        session.commit()



# ==========================================
# ==========================================
# CRUD DE PROCESSOS
# ==========================================
# ==========================================

def listar_processos(session: Session) -> List[Processo]:
    return session.exec(select(Processo)).all()

def criar_processo(data: ProcessoCreate, session: Session) -> Processo:
    cliente = buscar_cliente(data.cliente_id, session)
    dump_data = data.model_dump() if hasattr(data, "model_dump") else data.dict()
    novo = Processo(**dump_data)
    session.add(novo)
    session.commit()
    session.refresh(novo)

    send_email(
        to_email=cliente.email,
        subject=f"Novo processo criado: {novo.numero}",
        body=f"Olá, {cliente.nome},\n\nUm novo processo foi vinculado a sua conta:\n{novo.descricao}\nStatus atual: {novo.status}"
    )
    return novo

def buscar_processo(id_: int, session: Session) -> Processo:
    p = session.get(Processo, id_)
    if not p:
        raise ValueError("Processo não encontrado")
    return p

def atualizar_cliente(id_: int, data: ClienteCreate, session: Optional[Session] = None) -> Cliente:
    if session is None:
        from backend.main import engine
        with Session(engine) as nova_sessao:
            c = buscar_cliente(id_, nova_sessao)
            for k, v in data.model_dump().items():
                setattr(c, k, v)
            nova_sessao.add(c)
            nova_sessao.commit()
            nova_sessao.refresh(c)
            return c
    else:
        c = buscar_cliente(id_, session)
        for k, v in data.model_dump().items():
            setattr(c, k, v)
        session.add(c)
        session.commit()
        session.refresh(c)
        return c

def deletar_processo(id_: int, session: Optional[Session] = None):
    if session is None:
        from backend.main import engine
        with Session(engine) as nova_sessao:
            p = buscar_processo(id_, nova_sessao)
            nova_sessao.delete(p)
            nova_sessao.commit()
    else:
        p = buscar_processo(id_, session)
        session.delete(p)
        session.commit()

def processos_por_cliente(cliente_id: int, session: Session = next(get_session())) -> List[Processo]:
    from sqlmodel import select
    
    statement = select(Processo).where(Processo.cliente_id == cliente_id)
    processos = session.exec(statement).all()
    
    return processos