from pydantic import BaseModel, Field, EmailStr, field_validator
import re
from pydantic import BaseModel, EmailStr, field_validator
import re
from pydantic import BaseModel
from typing import List, Optional

# ==========================================
# ==========================================
# SCHEMAS DE USUÁRIOS
# ==========================================
# ==========================================

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    cpf: str
    telefone: str
    senha: str
    role: Optional[str] = "comum"
    codigo_admin: Optional[str] = None

    @field_validator('cpf', mode='before')
    @classmethod
    def limpar_e_validar_cpf_usuario(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("CPF inválido.")
        numeros = re.sub(r'\D', '', v)
        if len(numeros) != 11:
            raise ValueError("O CPF deve conter exatamente 11 dígitos numéricos.")
        return numeros

    @field_validator('telefone', mode='before')
    @classmethod
    def limpar_telefone_usuario(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Telefone inválido.")
        numeros = re.sub(r'\D', '', v)
        if len(numeros) < 10 or len(numeros) > 11:
            raise ValueError("O telefone deve conter entre 10 e 11 dígitos numéricos.")
        return numeros
class UsuarioRead(BaseModel):
    id: int
    nome: str
    email: str
    cpf: str
    role: str

    class Config:
        from_attributes = True


# ==========================================
# ==========================================
# SCHEMAS DE CLIENTE
# ==========================================
# ==========================================

class ClienteBase(BaseModel):
    nome: str
    email: str
    cpf_cnpj: str
    telefone: Optional[str] = None

    @field_validator('cpf_cnpj', mode='before')
    @classmethod
    def validar_e_limpar_cpf_cnpj(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("CPF/CNPJ inválido.")
        
        numeros = re.sub(r'\D', '', v)
        
        if len(numeros) not in [11, 14]:
            raise ValueError("O CPF deve conter 11 dígitos ou o CNPJ deve conter 14 dígitos numéricos.")
            
        return numeros

    @field_validator('telefone', mode='before')
    @classmethod
    def limpar_telefone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
    
        numeros = re.sub(r'\D', '', v)
        
        if len(numeros) < 10 or len(numeros) > 11:
            raise ValueError("O telefone informado deve conter um DDD válido e entre 10 e 11 dígitos numéricos.")
            
        return numeros
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

class ClienteSimplesRead(BaseModel):
    id: int
    nome: str
    email: str

    class Config:
        from_attributes = True

# ==========================================
# ==========================================
# SCHEMAS DE PROCESSO
# ==========================================
# ==========================================

class ProcessoBase(BaseModel):
    numero_cnj: str
    descricao: Optional[str] = None
    cliente_id: int
    status: Optional[str] = "Ativo"

    @field_validator('numero_cnj', mode='before')
    @classmethod
    def validar_e_limpar_cnj(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Número de processo inválido.")
        numeros = re.sub(r'\D', '', v)
        if len(numeros) != 20:
            raise ValueError("O número do processo CNJ deve conter exatamente 20 dígitos numéricos.")
            
        return numeros

class ProcessoCreate(BaseModel):
    cliente_id: int
    numero_cnj: str
    descricao: str
    status: str

class ProcessoUpdate(BaseModel):
    descricao: str
    status: str

class ProcessoRead(BaseModel):
    id: int
    cliente_id: int
    numero_cnj: str
    descricao: str
    status: str
    cliente: Optional[ClienteSimplesRead] = None 

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True

# ==========================================
# ==========================================
# SCHEMAS COM RELACIONAMENTOS (OPCIONAL)
# ==========================================
# ==========================================

class ProcessoComCliente(ProcessoRead):
    cliente: Optional[ClienteRead] = None


class ProcessoPaginadoResponse(BaseModel):
    total: int
    dados: List[ProcessoComCliente]
