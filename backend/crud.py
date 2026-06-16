from typing import List, Optional
from sqlmodel import Session, select
from .models import Cliente, Processo
from .schemas import ClienteCreate, ProcessoCreate

# ==========================================
# ==========================================
# CRUD DE CLIENTES
# ==========================================
# ==========================================

def listar_clientes(session: Session, limit: int = 10, offset: int = 0):
    statement = select(Cliente).limit(limit).offset(offset)
    return session.exec(statement).all()

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

from sqlmodel import select, or_

def listar_processos(session: Session, limit: int = 10, offset: int = 0, termo: Optional[str] = None, status: Optional[str] = None):
    # Fazemos um JOIN com Cliente para podermos pesquisar pelo nome dele também!
    statement = select(Processo).join(Cliente, Processo.cliente_id == Cliente.id, isouter=True)
    
    if status and status != "Todos":
        statement = statement.where(Processo.status == status)
        
    if termo:
        busca_lk = f"%{termo}%"
        statement = statement.where(
            or_(
                Processo.numero_cnj.ilike(busca_lk),
                Processo.descricao.ilike(busca_lk),
                Cliente.nome.ilike(busca_lk)
            )
        )
        
    statement = statement.limit(limit).offset(offset)
    return session.exec(statement).all()

def criar_processo(session: Session, data: ProcessoCreate) -> Processo:
    novo_processo = Processo(
        cliente_id=data.cliente_id,
        numero_cnj=data.numero_cnj,
        descricao=data.descricao,
        status=data.status if data.status else "Ativo"
    )
    
    session.add(novo_processo)
    session.commit()
    session.refresh(novo_processo)
    return novo_processo

def buscar_processo(id_: int, session: Session) -> Processo:
    p = session.get(Processo, id_)
    if not p:
        raise ValueError("Processo não encontrado")
    return p

def atualizar_processo(id_: int, data: any, session: Optional[Session] = None) -> Processo:
    if session is None:
        from backend.main import engine
        with Session(engine) as nova_sessao:
            p = buscar_processo(id_, nova_sessao)
            dados_atualizados = data.model_dump(exclude_unset=True) if hasattr(data, "model_dump") else data
            for k, v in dados_atualizados.items():
                setattr(p, k, v)
            nova_sessao.add(p)
            nova_sessao.commit()
            nova_sessao.refresh(p)
            return p
    else:
        p = buscar_processo(id_, session)
        dados_atualizados = data.model_dump(exclude_unset=True) if hasattr(data, "model_dump") else data
        for k, v in dados_atualizados.items():
            setattr(p, k, v)
        session.add(p)
        session.commit()
        session.refresh(p)
        return p

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

def processos_por_cliente(cliente_id: int, session: Session) -> List[Processo]:
    statement = select(Processo).where(Processo.cliente_id == cliente_id)
    processos = session.exec(statement).all()
    return processos