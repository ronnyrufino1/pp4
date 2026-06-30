from passlib.context import CryptContext

# Configuração do Argon2id
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB em KB (Memory Hard + CPU Hard)
    argon2__time_cost=3,        # Número de iterações/passagens
    argon2__parallelism=4       # Número de threads paralelas
)

def gerar_hash_senha(senha_limpa: str) -> str:
    """Transforma a senha em texto limpo em um hash seguro Argon2id."""
    return pwd_context.hash(senha_limpa)

def verificar_senha(senha_limpa: str, senha_criptografada: str) -> bool:
    """Compara a senha digitada com o hash guardado no banco."""
    return pwd_context.verify(senha_limpa, senha_criptografada)