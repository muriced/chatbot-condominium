import os
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL
from db.pdf_processor import PDFProcessor


class FAISSManager:
    """Gerencia o banco de dados vetorial FAISS."""
    
    def __init__(self, embedding_model: str = EMBEDDING_MODEL):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.pdf_processor = PDFProcessor()
        self.index_path = Path("./data/faiss_index")
        self.db: Optional[VectorStore] = None
        
    def create_or_load_index(self, force_reload: bool = False) -> VectorStore:
        """Cria um novo índice ou carrega um existente."""
        if self.db is not None and not force_reload:
            return self.db
        
        # Se force_reload é True ou o índice não existe, remover diretório do índice
        if force_reload and self.index_path.exists():
            import shutil
            print("Removendo índice FAISS existente...")
            shutil.rmtree(self.index_path)
        
        if self.index_path.exists() and not force_reload:
            print("Carregando índice FAISS existente...")
            try:
                self.db = FAISS.load_local(str(self.index_path), self.embeddings)
                print(f"Índice FAISS carregado com sucesso.")
                return self.db
            except Exception as e:
                print(f"Erro ao carregar índice FAISS: {e}")
                print("Criando novo índice...")
        
        # Processar PDFs e criar novo índice
        documents = self.pdf_processor.process_pdfs()
        
        if not documents:
            print("Nenhum documento para indexar.")
            # Criar um índice vazio
            self.db = FAISS.from_documents(
                [Document(page_content="Índice vazio. Nenhum PDF carregado.")], 
                self.embeddings
            )
        else:
            print(f"Criando índice FAISS com {len(documents)} documentos...")
            self.db = FAISS.from_documents(documents, self.embeddings)
            
        self._save_index()
        return self.db
    
    def _save_index(self) -> None:
        """Salva o índice FAISS no disco."""
        if self.db is not None:
            os.makedirs(self.index_path, exist_ok=True)
            self.db.save_local(str(self.index_path))
            print(f"Índice FAISS salvo em {self.index_path}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """Adiciona novos documentos ao índice."""
        if not documents:
            return
            
        if self.db is None:
            self.create_or_load_index()
            
        self.db.add_documents(documents)
        self._save_index()
        print(f"Adicionados {len(documents)} documentos ao índice FAISS.")
    
    def similarity_search(self, query: str, k: int = 6) -> List[Document]:
        """Realiza uma busca de similaridade."""
        if self.db is None:
            self.create_or_load_index()
            
        results = self.db.similarity_search(query, k=k)
        return results