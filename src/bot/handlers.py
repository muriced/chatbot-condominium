import os
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters

from db.faiss_db import FAISSManager
from db.pdf_processor import PDFProcessor
from bot.utils import ChatbotUtils
from config import TELEGRAM_BOT_TOKEN


class TelegramBot:
    """Implementação do bot do Telegram."""
    
    def __init__(self):
        self.faiss_manager = FAISSManager()
        self.pdf_processor = PDFProcessor()
        self.chatbot_utils = ChatbotUtils()
        
        # Carregar o índice FAISS
        self.faiss_manager.create_or_load_index()
        
        # Configurar o bot do Telegram
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Configura os handlers de comandos e mensagens."""
        # Comandos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("reload", self._reload_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("stopApplication", self.stop_command))
        
        # Mensagens de texto (perguntas)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
        # Erro handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Envia uma mensagem quando o comando /start é emitido."""
        # Limpar histórico de conversa existente
        self.chatbot_utils.conversation_manager.clear_conversation(update.effective_chat.id)
        
        await update.message.reply_text(
            "👋 Olá! Eu sou o assistente virtual do seu condomínio.\n\n"
            "Você pode me fazer perguntas sobre o Regimento Interno ou "
            "sobre a Convenção Condominial.\n\n"
            "Use /help para ver todos os comandos disponíveis.\n\n"
            "💬 Nova conversa iniciada! Posso manter o contexto do nosso diálogo."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Envia uma mensagem quando o comando /help é emitido."""
        await update.message.reply_text(
            "📚 Comandos disponíveis:\n\n"
            "/start - Inicia uma nova conversa\n"
            "/help - Mostra esta mensagem de ajuda\n"
            "/reload - Recarrega a base de conhecimento\n"
            "/clear - Limpa o histórico da conversa atual\n"
            "🔍 Como usar:\n"
            "1. Faça perguntas sobre o seu condomínio\n"
            "2. Receba respostas baseadas nos documentos\n"
            "3. Continue o diálogo - eu mantenho o contexto da conversa!"
        )
    
    async def _reload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Recarrega a base de dados de PDFs."""
        await update.message.reply_text("🔄 Recarregando base de dados de PDFs...")
        
        # Recriar o índice
        try:
            self.faiss_manager.create_or_load_index(force_reload=True)
            # Limpar histórico de conversa ao recarregar a base
            self.chatbot_utils.conversation_manager.clear_conversation(update.effective_chat.id)
            await update.message.reply_text(
                "✅ Base de dados recarregada com sucesso!\n"
                "💬 Histórico da conversa foi limpo para começar uma nova interação."
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao recarregar a base de dados: {e}")
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Limpa o histórico da conversa atual."""
        self.chatbot_utils.conversation_manager.clear_conversation(update.effective_chat.id)
        await update.message.reply_text(
            "🗑 Histórico da conversa limpo!\n"
            "Você pode começar uma nova conversa agora."
        )
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Para o bot."""
        await update.message.reply_text("🛑 Parando o bot...")
        await self.application.stop()
        # await self.application.shutdown()
    
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Responde a mensagens de texto (perguntas)."""
        query = update.message.text
        chat_id = update.effective_chat.id
        
        # Mostrar que o bot está digitando
        await context.bot.send_chat_action(
            chat_id=chat_id, 
            action="typing"
        )
        
        # Buscar documentos relevantes
        docs = self.faiss_manager.similarity_search(query)
        
        # Gerar resposta considerando o histórico
        response = self.chatbot_utils.generate_response(query, docs, chat_id)
        
        # Enviar resposta
        await update.message.reply_text(response)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Trata erros no bot."""
        print(f"Erro: {context.error}")
        
        # Informar o usuário sobre o erro
        if update:
            await update.message.reply_text(
                "❌ Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente."
            )
    
    def start(self) -> None:
        """Inicia o bot."""
        print("Iniciando bot do Telegram...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)