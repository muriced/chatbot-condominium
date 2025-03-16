"""Script para inicialização do banco de dados FAISS e processamento dos PDFs."""
import logging

from db.faiss_db import FAISSManager


def initialize_database(force_reload: bool = False) -> None:
    """Inicializa o banco de dados FAISS com os PDFs existentes."""
    logging.info("Iniciando inicialização do banco de dados...")
    
    # Instância do FAISSManager
    faiss_manager = FAISSManager()
    
    try:
        # Forçar recriação do índice
        faiss_manager.create_or_load_index(force_reload=force_reload)
        logging.info("Banco de dados inicializado com sucesso!")
        
    except Exception as e:
        logging.error(f"Erro ao inicializar banco de dados: {e}")
        raise
