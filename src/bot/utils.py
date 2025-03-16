from typing import List
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import GOOGLE_API_KEY


class ChatbotUtils:
    """Utilitários para o chatbot."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.5,
            convert_system_message_to_human=True
        )

        # Inicializar o prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Você é um assistente de condomínio que responde APENAS com informações presentes
            nos documentos pdfs fornecidos (Convenção Condominal e Regimento Interno).
            Se a resposta não estiver explicitamente no contexto, diga "Não encontrei esta informação nos documentos disponíveis."
            Nunca invente informações ou faça suposições além do conteúdo fornecido.
            Cite a fonte (nome do documento) para cada informação que fornecer.
            Seja claro, conciso e útil em suas respostas.
            """),
            ("human", """
            Contextos:
            {contexts}
            
            Pergunta: {question}
            """)
        ])

        # Definir a cadeia de processamento
        self.chain = self.prompt | self.llm | StrOutputParser()

    def format_documents(self, docs: List[Document]) -> str:
        """Formata uma lista de documentos em texto para contexto."""
        return "\n\n".join([f"Documento {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])

    def generate_response(self, query: str, docs: List[Document]) -> str:
        """Gera uma resposta para a consulta com base nos documentos recuperados."""
        if not docs:
            return "Não encontrei informações relevantes sobre essa consulta nos documentos disponíveis."

        contexts = self.format_documents(docs)

        response = self.chain.invoke({
            "contexts": contexts,
            "question": query
        })

        return response
