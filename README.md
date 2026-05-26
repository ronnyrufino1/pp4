## Como Executar o Projeto Localmente

### Pré-requisitos

- Python 3.10 ou superior instalado.
- Navegador web moderno.

### 1. Configurando o Backend

1. Abra o terminal e navegue até a pasta do projeto:

```bash
cd caminho/para/o/seu/projeto

```

2. Crie e ative um ambiente virtual (recomendado):

```bash
# No macOS/Linux
python3 -m venv venv
source venv/bin/activate

# No Windows
python -m venv venv
venv\Scripts\activate

```

3. Instale as dependências necessárias:

```bash
pip install fastapi uvicorn sqlmodel pydantic[email]

```

4. Inicie o servidor de desenvolvimento do **FastAPI**:

```bash
uvicorn backend.main:app --reload

```

_O backend estará rodando e pronto para receber requisições em `http://127.0.0.1:8000`._

### 2. Executando o Frontend

Como o frontend é composto por arquivos estáticos (`HTML/CSS/JS`), você pode executá-lo de duas formas:

- **Opção 1 (Recomendada):** Se utiliza o VS Code, instale a extensão **Live Server**, abra a pasta `frontend/`, clique com o botão direito sobre o arquivo `index-clientes.html` e selecione **Open with Live Server**.
- **Opção 2 (Navegador):** Dê um duplo clique diretamente no arquivo `frontend/index-clientes.html` para abri-lo no seu navegador.
