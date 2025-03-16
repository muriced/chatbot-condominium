FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar poetry
RUN pip install poetry==2.1.1

# Configurar poetry para não usar ambiente virtual
RUN poetry config virtualenvs.create false

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock* ./

# Instalar dependências
RUN poetry install --no-dev --no-interaction --no-ansi

# Copiar código-fonte
COPY src/ ./src/
COPY .env ./

# Criar diretório para PDFs
RUN mkdir -p /app/data/pdfs

# Definir comando de inicialização
CMD ["python", "-m", "src.main"]