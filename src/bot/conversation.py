"""Gerenciador de conversas do chatbot."""
from typing import List, Dict
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """Representa uma mensagem na conversa."""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationManager:
    """Gerencia o histórico de conversas do chatbot."""
    
    def __init__(self, max_history: int = 5):
        self.conversations: Dict[int, List[Message]] = {}
        self.max_history = max_history
    
    def add_message(self, chat_id: int, role: str, content: str) -> None:
        """Adiciona uma mensagem ao histórico da conversa."""
        if chat_id not in self.conversations:
            self.conversations[chat_id] = []
            
        message = Message(role=role, content=content)
        self.conversations[chat_id].append(message)
        
        # Manter apenas as últimas max_history mensagens
        if len(self.conversations[chat_id]) > self.max_history:
            self.conversations[chat_id] = self.conversations[chat_id][-self.max_history:]
    
    def get_conversation_history(self, chat_id: int) -> List[Message]:
        """Retorna o histórico da conversa para um chat específico."""
        return self.conversations.get(chat_id, [])
    
    def clear_conversation(self, chat_id: int) -> None:
        """Limpa o histórico de conversa para um chat específico."""
        if chat_id in self.conversations:
            del self.conversations[chat_id]
    
    def format_history_for_prompt(self, chat_id: int) -> str:
        """Formata o histórico da conversa para uso no prompt."""
        history = self.get_conversation_history(chat_id)
        if not history:
            return ""
            
        formatted = "\nHistórico da conversa:\n"
        for msg in history:
            role = "Usuário" if msg.role == "user" else "Assistente"
            formatted += f"{role}: {msg.content}\n"
        return formatted
