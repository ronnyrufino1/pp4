from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# ==========================================
# ==========================================
# SCHEMAS DE CLIENTE
# ==========================================
# ==========================================

class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100, description="Nome completo do cliente ou Razão Social")
    cpf_cnpj: str = Field(..., description="CPF ou CNPJ apenas números")
    email: EmailStr = Field(..., description="E-mail válido para notificações e alertas")
    telefone: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None

class ClienteRead(ClienteBase):
    id: int

    class Config:
        from_attributes = True 


# ==========================================
# ==========================================
# SCHEMAS DE PROCESSO
# ==========================================
# ==========================================

class ProcessoBase(BaseModel):
    cliente_id: int = Field(..., description="ID do cliente proprietário do processo")
    numero: str = Field(..., description="Número único do processo (ex: CNJ)")
    descricao: str = Field(..., description="Resumo ou objeto do processo")
    status: str = Field(..., description="Status atual (ex: Ativo, Suspenso, Arquivado)")

class ProcessoCreate(ProcessoBase):
    pass

class ProcessoUpdate(BaseModel):
    cliente_id: Optional[int] = None
    numero: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = None

class ProcessoRead(ProcessoBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# ==========================================
# SCHEMAS COM RELACIONAMENTOS (OPCIONAL)
# ==========================================
# ==========================================

class ProcessoComCliente(ProcessoRead):
    cliente: Optional[ClienteRead] = None