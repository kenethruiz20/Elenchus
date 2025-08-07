"""
Context Manager Service for LLM Conversations

Implements best practices for managing conversation context:
- Token-aware context window management
- Message prioritization and summarization
- Context compression and retrieval
- Integration with Langfuse for tracing
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import hashlib
from enum import Enum

from app.services.model_router import ModelMessage, ModelRole
from app.models.message import Message


class MessagePriority(Enum):
    """Message priority levels for context management."""
    CRITICAL = 1    # System messages, recent user queries
    HIGH = 2        # Recent assistant responses, important context
    MEDIUM = 3      # Older messages with relevant information
    LOW = 4         # Background information, can be compressed


@dataclass
class ConversationContext:
    """Represents the current conversation context."""
    session_id: str
    messages: List[ModelMessage] = field(default_factory=list)
    total_tokens: int = 0
    max_tokens: int = 8000  # Conservative limit for context window
    system_prompt: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ContextManager:
    """Manages conversation context with token-aware optimization."""
    
    def __init__(self, max_context_tokens: int = 8000, max_messages: int = 50):
        """
        Initialize context manager.
        
        Args:
            max_context_tokens: Maximum tokens to keep in context
            max_messages: Maximum number of messages to track
        """
        self.max_context_tokens = max_context_tokens
        self.max_messages = max_messages
        self.contexts: Dict[str, ConversationContext] = {}
        
        # Token estimation (rough approximation: 1 token ≈ 4 characters)
        self.chars_per_token = 4
    
    def create_session(
        self, 
        session_id: Optional[str] = None, 
        system_prompt: str = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new conversation session."""
        if not session_id:
            session_id = self._generate_session_id()
        
        if not system_prompt:
            system_prompt = self._get_default_system_prompt()
        
        context = ConversationContext(
            session_id=session_id,
            system_prompt=system_prompt,
            metadata=metadata or {},
            max_tokens=self.max_context_tokens
        )
        
        # Add system message
        system_message = ModelMessage(
            role=ModelRole.SYSTEM,
            content=system_prompt
        )
        context.messages.append(system_message)
        context.total_tokens = self._estimate_tokens(system_prompt)
        
        self.contexts[session_id] = context
        return session_id
    
    def add_message(
        self, 
        session_id: str, 
        content: str, 
        role: ModelRole,
        priority: MessagePriority = MessagePriority.HIGH,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a message to the conversation context."""
        if session_id not in self.contexts:
            self.create_session(session_id)
        
        context = self.contexts[session_id]
        message = ModelMessage(role=role, content=content)
        
        # Estimate tokens for the new message
        message_tokens = self._estimate_tokens(content)
        
        # Check if we need to compress context
        if context.total_tokens + message_tokens > context.max_tokens:
            self._compress_context(context, message_tokens)
        
        # Add the message
        context.messages.append(message)
        context.total_tokens += message_tokens
        context.updated_at = datetime.now(timezone.utc)
        
        # Store metadata if provided
        if metadata:
            context.metadata[f"msg_{len(context.messages)}"] = metadata
        
        return True
    
    def get_context_messages(self, session_id: str) -> List[ModelMessage]:
        """Get all messages for a session in the correct order."""
        if session_id not in self.contexts:
            return []
        
        return self.contexts[session_id].messages.copy()
    
    def get_context_for_llm(self, session_id: str, include_system: bool = True) -> List[ModelMessage]:
        """Get optimized context for LLM inference."""
        if session_id not in self.contexts:
            return []
        
        context = self.contexts[session_id]
        messages = context.messages.copy()
        
        if not include_system:
            messages = [msg for msg in messages if msg.role != ModelRole.SYSTEM]
        
        return messages
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information and statistics."""
        if session_id not in self.contexts:
            return None
        
        context = self.contexts[session_id]
        return {
            "session_id": session_id,
            "message_count": len(context.messages),
            "total_tokens": context.total_tokens,
            "max_tokens": context.max_tokens,
            "created_at": context.created_at,
            "updated_at": context.updated_at,
            "metadata": context.metadata,
            "token_utilization": context.total_tokens / context.max_tokens
        }
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a conversation session."""
        if session_id in self.contexts:
            del self.contexts[session_id]
            return True
        return False
    
    def _compress_context(self, context: ConversationContext, needed_tokens: int):
        """Compress context by removing or summarizing older messages."""
        target_tokens = context.max_tokens - needed_tokens - 1000  # Keep 1k buffer
        
        # Always keep system message and last few exchanges
        system_msg = context.messages[0] if context.messages and context.messages[0].role == ModelRole.SYSTEM else None
        recent_messages = context.messages[-6:]  # Keep last 3 exchanges
        
        # Calculate tokens for protected messages
        protected_tokens = 0
        if system_msg:
            protected_tokens += self._estimate_tokens(system_msg.content)
        
        for msg in recent_messages:
            protected_tokens += self._estimate_tokens(msg.content)
        
        if protected_tokens <= target_tokens:
            # We can keep recent messages, compress older ones
            if system_msg:
                new_messages = [system_msg]
            else:
                new_messages = []
            
            # Add a summary of removed messages
            if len(context.messages) > len(recent_messages) + (1 if system_msg else 0):
                summary = self._create_conversation_summary(context.messages[1:-6] if system_msg else context.messages[:-6])
                if summary:
                    summary_msg = ModelMessage(
                        role=ModelRole.SYSTEM,
                        content=f"[Previous conversation summary: {summary}]"
                    )
                    new_messages.append(summary_msg)
            
            # Add recent messages
            new_messages.extend(recent_messages)
            
            context.messages = new_messages
            context.total_tokens = sum(self._estimate_tokens(msg.content) for msg in new_messages)
        else:
            # Aggressive compression - keep only system and last exchange
            if system_msg:
                context.messages = [system_msg] + context.messages[-2:]
            else:
                context.messages = context.messages[-2:]
            
            context.total_tokens = sum(self._estimate_tokens(msg.content) for msg in context.messages)
    
    def _create_conversation_summary(self, messages: List[ModelMessage]) -> str:
        """Create a brief summary of conversation messages."""
        if not messages:
            return ""
        
        # Simple summarization - in production, you might use an LLM for this
        topics = []
        for msg in messages:
            if msg.role == ModelRole.USER:
                # Extract key topics from user messages
                content = msg.content.lower()
                if len(content) > 50:
                    topics.append(content[:50] + "...")
                else:
                    topics.append(content)
        
        if topics:
            return f"Discussed: {', '.join(topics[:3])}"
        return "Previous conversation context"
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return max(1, len(text) // self.chars_per_token)
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        hash_input = f"{timestamp}_{id(self)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for legal AI."""
        return """You are Elenchus, a professional legal AI assistant. You provide helpful, accurate legal analysis and research assistance. 

Key guidelines:
- Provide clear, well-structured legal analysis
- Cite relevant laws, cases, and precedents when applicable
- Always clarify that you're providing information, not legal advice
- Ask clarifying questions when the legal issue is unclear
- Be professional but approachable in your communication
- Maintain context of our ongoing conversation"""


# Global context manager instance
context_manager = ContextManager()