import os
import fitz  # PyMuPDF
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE, CHUNK_OVERLAP, PDF_DIR


class PDFProcessor:
    """Processa arquivos PDF para extração de texto e criação de chunks."""

    def __init__(self, pdf_dir: Path = PDF_DIR):
        self.pdf_dir = pdf_dir

    def get_pdf_files(self) -> List[Path]:
        """Retorna a lista de arquivos PDF no diretório configurado."""
        if not self.pdf_dir.exists():
            os.makedirs(self.pdf_dir, exist_ok=True)
            return []
        
        return list(self.pdf_dir.glob("*.pdf"))

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extrai texto de um arquivo PDF."""
        text = ""
        
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Erro ao processar PDF {pdf_path}: {e}")
            
        return text

    def create_chunks(self, text: str, pdf_path: Path) -> List[Document]:
        """Divide o texto em chunks para processamento."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        
        chunks = splitter.create_documents([text])
        
        # Adiciona metadados sobre a origem do chunk
        for chunk in chunks:
            chunk.metadata = {
                "source": str(pdf_path.name),
                "file_path": str(pdf_path),
            }
            
        return chunks

    def process_pdfs(self) -> List[Document]:
        """Processa todos os PDFs e retorna os documentos."""
        documents = []
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            print(f"Nenhum arquivo PDF encontrado em {self.pdf_dir}")
            return documents
            
        print(f"Processando {len(pdf_files)} arquivos PDF...")
        
        for pdf_path in pdf_files:
            print(f"Processando {pdf_path.name}...")
            text = self.extract_text_from_pdf(pdf_path)
            if text:
                chunks = self.create_chunks(text, pdf_path)
                documents.extend(chunks)
                print(f"  - Extraídos {len(chunks)} chunks de {pdf_path.name}")
            else:
                print(f"  - Nenhum texto extraído de {pdf_path.name}")
                
        print(f"Total de {len(documents)} chunks extraídos de todos os PDFs.")
        return documents