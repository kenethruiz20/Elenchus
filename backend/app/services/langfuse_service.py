"""
Langfuse Integration Service

Provides comprehensive tracing, logging, and evaluation for LLM conversations.
Integrates with the context manager for session tracking and conversation analysis.
"""

from typing import Dict, Any, List, Optional, Union
import json
import logging
from datetime import datetime, timezone
from dataclasses import asdict
import asyncio
from functools import wraps

try:
    from langfuse import Langfuse
    from langfuse.decorators import langfuse_context, observe
    from langfuse.model import CreateTrace, CreateSpan, CreateGeneration
    LANGFUSE_AVAILABLE = True
except ImportError:
    logging.warning("Langfuse not available. Install with: pip install langfuse")
    LANGFUSE_AVAILABLE = False
    # Mock decorators for when Langfuse is not available
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class langfuse_context:
        @staticmethod
        def update_current_trace(**kwargs):
            pass
        
        @staticmethod
        def update_current_observation(**kwargs):
            pass

from app.config.settings import settings
from app.services.model_router import ModelMessage, ModelRole


class LangfuseService:
    """Service for integrating Langfuse tracing and evaluation."""
    
    def __init__(self):
        """Initialize Langfuse client if available."""
        self.client = None
        self.enabled = LANGFUSE_AVAILABLE and hasattr(settings, 'LANGFUSE_SECRET_KEY')
        
        if self.enabled:
            try:
                self.client = Langfuse(
                    secret_key=getattr(settings, 'LANGFUSE_SECRET_KEY', ''),
                    public_key=getattr(settings, 'LANGFUSE_PUBLIC_KEY', ''),
                    host=getattr(settings, 'LANGFUSE_HOST', 'https://cloud.langfuse.com')
                )
                logging.info("✅ Langfuse initialized successfully")
            except Exception as e:
                logging.warning(f"⚠️ Langfuse initialization failed: {e}")
                self.enabled = False
        else:
            logging.info("📝 Langfuse tracing disabled (not configured)")
    
    def is_enabled(self) -> bool:
        """Check if Langfuse is enabled and available."""
        return self.enabled and self.client is not None
    
    @observe(name="legal_ai_chat")
    async def trace_conversation(
        self,
        session_id: str,
        messages: List[ModelMessage],
        model_response: str,
        model_name: str = "gemini-1.5-flash",
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Trace a complete conversation exchange.
        
        Args:
            session_id: Unique session identifier
            messages: List of conversation messages
            model_response: LLM response
            model_name: Name of the model used
            metadata: Additional metadata to log
            tags: Tags for categorizing the conversation
        
        Returns:
            Trace ID if successful, None otherwise
        """
        if not self.is_enabled():
            return None
        
        try:
            # Update current trace with session info
            langfuse_context.update_current_trace(
                session_id=session_id,
                user_id=metadata.get('user_id') if metadata else None,
                metadata={
                    "model": model_name,
                    "session_id": session_id,
                    "message_count": len(messages),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **(metadata or {})
                },
                tags=tags or ["legal-ai", "chat"],
                version=getattr(settings, 'APP_VERSION', '1.0.0')
            )
            
            # Create generation span for the LLM call
            await self._trace_llm_generation(
                messages=messages,
                response=model_response,
                model=model_name,
                metadata=metadata
            )
            
            # Log conversation metrics
            await self._log_conversation_metrics(session_id, messages, model_response)
            
            return session_id  # Use session_id as trace_id for consistency
            
        except Exception as e:
            logging.error(f"Failed to trace conversation: {e}")
            return None
    
    async def _trace_llm_generation(
        self,
        messages: List[ModelMessage],
        response: str,
        model: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Trace the LLM generation process."""
        if not self.is_enabled():
            return
        
        try:
            # Convert messages to Langfuse format
            langfuse_messages = []
            for msg in messages:
                langfuse_messages.append({
                    "role": msg.role.value.lower(),
                    "content": msg.content
                })
            
            # Create generation observation
            langfuse_context.update_current_observation(
                type="generation",
                name="legal_ai_response",
                input=langfuse_messages,
                output=response,
                model=model,
                metadata={
                    "input_tokens": sum(len(msg.content.split()) for msg in messages),
                    "output_tokens": len(response.split()),
                    "legal_domain": self._detect_legal_domain(messages),
                    **(metadata or {})
                },
                tags=["generation", "legal-analysis"]
            )
            
        except Exception as e:
            logging.error(f"Failed to trace LLM generation: {e}")
    
    async def log_user_feedback(
        self,
        session_id: str,
        message_id: str,
        feedback_type: str,  # "thumbs_up", "thumbs_down", "correction"
        feedback_value: Union[bool, str, Dict],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log user feedback for a specific response.
        
        Args:
            session_id: Session identifier
            message_id: Specific message ID
            feedback_type: Type of feedback
            feedback_value: Feedback value (bool for thumbs, text for correction)
            metadata: Additional context
        
        Returns:
            True if logged successfully
        """
        if not self.is_enabled():
            return False
        
        try:
            score_name = f"user_feedback_{feedback_type}"
            
            # Convert feedback to numeric score for analytics
            if feedback_type in ["thumbs_up", "thumbs_down"]:
                score_value = 1.0 if feedback_value else 0.0
            else:
                score_value = None
            
            # Create score in Langfuse
            self.client.score(
                trace_id=session_id,
                name=score_name,
                value=score_value,
                comment=str(feedback_value) if feedback_type == "correction" else None,
                metadata={
                    "message_id": message_id,
                    "feedback_type": feedback_type,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **(metadata or {})
                }
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to log user feedback: {e}")
            return False
    
    async def _log_conversation_metrics(
        self,
        session_id: str,
        messages: List[ModelMessage],
        response: str
    ):
        """Log conversation-level metrics for analysis."""
        if not self.is_enabled():
            return
        
        try:
            # Calculate metrics
            user_messages = [msg for msg in messages if msg.role == ModelRole.USER]
            assistant_messages = [msg for msg in messages if msg.role == ModelRole.ASSISTANT]
            
            total_user_chars = sum(len(msg.content) for msg in user_messages)
            total_assistant_chars = sum(len(msg.content) for msg in assistant_messages) + len(response)
            
            # Detect conversation topics
            legal_domain = self._detect_legal_domain(messages)
            complexity_score = self._assess_query_complexity(user_messages)
            
            # Log as events
            self.client.event(
                trace_id=session_id,
                name="conversation_metrics",
                metadata={
                    "user_message_count": len(user_messages),
                    "assistant_message_count": len(assistant_messages) + 1,
                    "total_user_characters": total_user_chars,
                    "total_assistant_characters": total_assistant_chars,
                    "legal_domain": legal_domain,
                    "complexity_score": complexity_score,
                    "session_length": len(messages) + 1
                }
            )
            
        except Exception as e:
            logging.error(f"Failed to log conversation metrics: {e}")
    
    def _detect_legal_domain(self, messages: List[ModelMessage]) -> str:
        """Detect the primary legal domain from conversation content."""
        user_content = " ".join([
            msg.content.lower() for msg in messages 
            if msg.role == ModelRole.USER
        ])
        
        # Simple keyword-based domain detection
        domains = {
            "contract_law": ["contract", "agreement", "breach", "terms", "clause"],
            "criminal_law": ["criminal", "crime", "defendant", "prosecution", "guilty"],
            "corporate_law": ["corporation", "company", "merger", "securities", "board"],
            "family_law": ["divorce", "custody", "marriage", "family", "child"],
            "intellectual_property": ["patent", "trademark", "copyright", "ip", "infringement"],
            "employment_law": ["employment", "worker", "wage", "discrimination", "workplace"],
            "real_estate": ["property", "real estate", "lease", "landlord", "tenant"],
            "tax_law": ["tax", "irs", "deduction", "revenue", "audit"]
        }
        
        for domain, keywords in domains.items():
            if any(keyword in user_content for keyword in keywords):
                return domain
        
        return "general_legal"
    
    def _assess_query_complexity(self, user_messages: List[ModelMessage]) -> float:
        """Assess the complexity of user queries (0-1 scale)."""
        if not user_messages:
            return 0.0
        
        total_complexity = 0.0
        for msg in user_messages:
            content = msg.content.lower()
            
            # Length-based complexity
            length_score = min(len(content) / 1000, 1.0)
            
            # Legal complexity indicators
            complex_terms = [
                "precedent", "jurisdiction", "statute", "regulation", "amendment",
                "constitutional", "federal", "appellate", "circuit", "supreme"
            ]
            complex_score = sum(1 for term in complex_terms if term in content) / len(complex_terms)
            
            # Question complexity
            question_words = ["how", "why", "what if", "explain", "analyze", "compare"]
            question_score = sum(1 for word in question_words if word in content) / len(question_words)
            
            msg_complexity = (length_score + complex_score + question_score) / 3
            total_complexity += msg_complexity
        
        return total_complexity / len(user_messages)
    
    async def flush(self):
        """Flush any pending Langfuse data."""
        if self.is_enabled():
            try:
                self.client.flush()
            except Exception as e:
                logging.error(f"Failed to flush Langfuse data: {e}")


# Global Langfuse service instance
langfuse_service = LangfuseService()