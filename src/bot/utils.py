from typing import List, Optional
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import GOOGLE_API_KEY
from bot.conversation import ConversationManager


class ChatbotUtils:
    """Utilitários para o chatbot."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True,
            max_output_tokens=2048
        )

        self.conversation_manager = ConversationManager(max_history=5)

        # Inicializar o prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Você é um assistente de condomínio que responde perguntas do
            usuário com informações presentes nos documentos PDFs fornecidos
            (Regimento Interno).
            
            Instruções importantes:
            1. Sempre forneça respostas COMPLETAS, incluindo TODAS as informações relevantes do contexto
            2. Ao encontrar listas ou enumerações (ex: a, b, c, d...), SEMPRE inclua TODOS os itens
            3. Nunca trunque listas - mostre todos os itens na íntegra
            4. Se a resposta não estiver no contexto, diga "Não encontrei esta informação nos documentos disponíveis"
            5. Nunca invente informações ou faça suposições além do conteúdo fornecido
            6. Informe a fonte (nome do documento) no início da conversa ao responder pela primeira vez
            7. Mantenha a formatação original do texto (ex: numeração, letras, parágrafos)
            8. Seja educado e gentil
            9. Responda em português
            
            Lembre-se: É CRUCIAL fornecer TODAS as informações disponíveis no contexto, sem omitir nenhum item ou detalhe.
            """),
            ("human", """
            Contextos:
            {contexts}
            
            {conversation_history}
            
            Pergunta atual: {question}
            
            Lembre-se de considerar o histórico da conversa ao formular sua resposta.
            """)
        ])

        # Definir a cadeia de processamento
        self.chain = self.prompt | self.llm | StrOutputParser()

    def format_documents(self, docs: List[Document]) -> str:
        """Formata uma lista de documentos em texto para contexto."""
        formatted_docs = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', f'Documento {i+1}')
            formatted_docs.append(f"[{source}]:\n{doc.page_content}")
        return "\n\n".join(formatted_docs)

    def generate_response(self, query: str, docs: List[Document], chat_id: Optional[int] = None) -> str:
        """Gera uma resposta para a consulta com base nos documentos recuperados e histórico."""
        if not docs:
            return "Não encontrei informações relevantes sobre essa consulta nos documentos disponíveis."

        contexts = self.format_documents(docs)

        # Adicionar a pergunta ao histórico
        if chat_id is not None:
            self.conversation_manager.add_message(chat_id, "user", query)
            conversation_history = self.conversation_manager.format_history_for_prompt(
                chat_id)
        else:
            conversation_history = ""

        response = self.chain.invoke({
            "contexts": contexts,
            "question": query,
            "conversation_history": conversation_history
        })

        # Adicionar a resposta ao histórico
        if chat_id is not None:
            self.conversation_manager.add_message(
                chat_id, "assistant", response)

        return response
