import logging
from dotenv import load_dotenv

from bot.handlers import TelegramBot
from config import TELEGRAM_BOT_TOKEN, GOOGLE_API_KEY
from db.initialize_db import initialize_database

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def check_environment():
    """Verifica se todas as variáveis de ambiente necessárias estão configuradas."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN não configurado no arquivo .env")
        return False
        
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY não configurado no arquivo .env")
        return False
        
    return True

def main():
    """Função principal para iniciar o bot."""
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar ambiente
    if not check_environment():
        logger.error("Configuração incompleta. Abortando processo de inicialização...")
        return
    
    # Inicializar banco de dados FAISS com os PDFs existentes
    try:
        logger.info("Inicializando banco de dados...")
        initialize_database()
        logger.info("Banco de dados inicializado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        return
    
    # Criar e iniciar o bot
    bot = TelegramBot()
    bot.start()

if __name__ == "__main__":
    main()