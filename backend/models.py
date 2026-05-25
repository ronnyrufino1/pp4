from typing import Optional
from sqlmodel import SQLModel, Field

class Cliente(SQLModel, table=True):
    __tablename__ = "clientes"
    id: int = Field(default=None, primary_key=True)
    nome: str
    cpf_cnpj: str
    email: str
    telefone: Optional[str] = None

class Processo(SQLModel, table=True):
    __tablename__ = "processos"
    id: int = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="clientes.id")
    numero: str 
    descricao: str
    status: str
