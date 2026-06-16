from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    cpf: str = Field(unique=True, index=True)
    email: str
    hashed_password: str
    role: str = Field(default="comum")
    
class Cliente(SQLModel, table=True):
    __tablename__ = "clientes"
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    cpf_cnpj: str = Field(unique=True)
    email: str
    telefone: Optional[str] = None
    processos: List["Processo"] = Relationship(back_populates="cliente")

class Processo(SQLModel, table=True):
    __tablename__ = "processos"
    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="clientes.id")
    numero_cnj: str = Field(unique=True)
    descricao: str
    status: str
    cliente: Optional[Cliente] = Relationship(back_populates="processos")