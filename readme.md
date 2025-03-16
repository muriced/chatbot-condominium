# Telegram PDF Bot

Bot para Telegram que permite consultar informações de documentos PDF através de linguagem natural.

## Funcionalidades

- 📚 Processamento de documentos PDF
- 🔍 Pesquisa semântica usando FAISS
- 🤖 Integração com Google Gemini 2.0 Flash
- 💬 Interface de chat pelo Telegram

## Pré-requisitos

- Docker e Docker Compose
- Token de bot do Telegram (BotFather)
- API Key do Google Gemini

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/muriced/chatbot-condominium.git
cd chatbot-condominium
```

2. Copie o arquivo de exemplo de variáveis de ambiente:
```bash
cp .env.example .env
```

3. Edite o arquivo `.env` com suas credenciais:
```
TELEGRAM_BOT_TOKEN=seu_token_aqui
GOOGLE_API_KEY=sua_api_key_aqui
```

4. Crie a pasta para armazenar seus PDFs:
```bash
mkdir -p data/pdfs
"Coloque seus pdfs na pasta data/pdfs"
```

## Executando com Docker

Inicie o bot usando Docker Compose:

```bash
docker-compose up -d
```

Para visualizar os logs:
```bash
docker-compose logs -f
```

## Uso

1. Inicie uma conversa com seu bot no Telegram
2. Envie o comando `/start` para iniciar o bot
3. Faça perguntas sobre o conteúdo dos PDFs

## Comandos disponíveis

- `/start` - Inicia o bot
- `/help` - Mostra ajuda
- `/reload` - Recarrega todos os documentos PDF

## Desenvolvimento local sem Docker

1. Instale o Poetry (se ainda não tiver):
```bash
pip install poetry
```

2. Instale as dependências:
```bash
poetry install
```

3. Execute o bot:
```bash
PYTHONPATH=chatbot-condominium/src poetry run python src/main.py
```

## Estrutura do projeto

```
chatbot-condominium/
├── docker-compose.yml     # Configuração do Docker Compose
├── Dockerfile             # Configuração do Docker
├── .env.example           # Exemplo de variáveis de ambiente
├── pyproject.toml         # Dependências do Poetry
├── README.md              # Este arquivo
├── src/                   # Código-fonte
│   ├── main.py            # Ponto de entrada
│   ├── bot/               # Código do bot
│   ├── db/                # Código do banco de dados
│   └── config.py          # Configurações
└── data/                  # Dados
    └── pdfs/              # Armazenamento de PDFs
```

