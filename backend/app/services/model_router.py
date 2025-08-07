"""Model Router Service - Centralized LLM integration service."""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel

import google.generativeai as genai
from app.config.settings import settings


class ModelProvider(str, Enum):
    """Supported model providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"
    LMSTUDIO = "lmstudio"


class ModelRole(str, Enum):
    """Message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ModelMessage:
    """Standardized message format."""
    role: ModelRole
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ModelResponse(BaseModel):
    """Standardized response from any LLM provider."""
    content: str
    model: str
    provider: ModelProvider
    tokens_used: Optional[int] = None
    response_time_ms: float
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ModelConfig(BaseModel):
    """Configuration for a specific model."""
    model_config = {"protected_namespaces": ()}
    
    provider: ModelProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # For self-hosted APIs like LMStudio
    max_tokens: Optional[int] = 4096
    temperature: float = 0.7
    timeout: int = 30
    enabled: bool = True


class BaseModelProvider(ABC):
    """Abstract base class for all model providers."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> ModelResponse:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    async def stream_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from the model."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        pass


class GeminiProvider(BaseModelProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if config.api_key:
            genai.configure(api_key=config.api_key)
        self._model = None
    
    def _get_model(self):
        """Lazy load the Gemini model."""
        if self._model is None:
            self._model = genai.GenerativeModel(self.config.model_name)
        return self._model
    
    def _convert_messages(self, messages: List[ModelMessage]) -> List[Dict[str, str]]:
        """Convert ModelMessage to Gemini format."""
        gemini_messages = []
        for msg in messages:
            if msg.role == ModelRole.SYSTEM:
                # Gemini doesn't have system role, prepend to first user message
                continue
            
            role = "user" if msg.role == ModelRole.USER else "model"
            gemini_messages.append({
                "role": role,
                "parts": [msg.content]
            })
        
        return gemini_messages
    
    async def generate_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> ModelResponse:
        """Generate response using Gemini."""
        start_time = time.time()
        
        try:
            model = self._get_model()
            
            # Handle system message by prepending to first user message
            system_prompt = ""
            filtered_messages = []
            
            for msg in messages:
                if msg.role == ModelRole.SYSTEM:
                    system_prompt = msg.content + "\n\n"
                else:
                    filtered_messages.append(msg)
            
            # If we have a system prompt, prepend it to the first user message
            if system_prompt and filtered_messages and filtered_messages[0].role == ModelRole.USER:
                filtered_messages[0].content = system_prompt + filtered_messages[0].content
            
            # Convert to Gemini chat format
            if len(filtered_messages) == 1 and filtered_messages[0].role == ModelRole.USER:
                # Single message - use generate_content
                response = await asyncio.to_thread(
                    model.generate_content,
                    filtered_messages[0].content,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.config.temperature,
                        max_output_tokens=self.config.max_tokens
                    )
                )
                content = response.text
                tokens_used = response.usage_metadata.total_token_count if response.usage_metadata else None
            else:
                # Multi-turn conversation - use chat
                gemini_messages = self._convert_messages(filtered_messages)
                chat = model.start_chat(history=gemini_messages[:-1])
                
                response = await asyncio.to_thread(
                    chat.send_message,
                    gemini_messages[-1]["parts"][0],
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.config.temperature,
                        max_output_tokens=self.config.max_tokens
                    )
                )
                content = response.text
                tokens_used = response.usage_metadata.total_token_count if response.usage_metadata else None
            
            response_time = (time.time() - start_time) * 1000
            
            return ModelResponse(
                content=content,
                model=self.config.model_name,
                provider=ModelProvider.GEMINI,
                tokens_used=tokens_used,
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ModelResponse(
                content="",
                model=self.config.model_name,
                provider=ModelProvider.GEMINI,
                response_time_ms=response_time,
                error=str(e)
            )
    
    async def stream_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from Gemini."""
        # TODO: Implement streaming for Gemini
        # For now, return the full response
        response = await self.generate_response(messages, **kwargs)
        if response.error:
            yield f"Error: {response.error}"
        else:
            yield response.content
    
    def validate_config(self) -> bool:
        """Validate Gemini configuration."""
        return bool(self.config.api_key)


class OpenAIProvider(BaseModelProvider):
    """OpenAI provider implementation (placeholder)."""
    
    async def generate_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> ModelResponse:
        """Generate response using OpenAI."""
        # TODO: Implement OpenAI integration
        return ModelResponse(
            content="OpenAI integration not implemented yet",
            model=self.config.model_name,
            provider=ModelProvider.OPENAI,
            response_time_ms=0.0,
            error="Not implemented"
        )
    
    async def stream_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI."""
        yield "OpenAI streaming not implemented yet"
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        return bool(self.config.api_key)


class ClaudeProvider(BaseModelProvider):
    """Anthropic Claude provider implementation (placeholder)."""
    
    async def generate_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> ModelResponse:
        """Generate response using Claude."""
        # TODO: Implement Claude integration
        return ModelResponse(
            content="Claude integration not implemented yet",
            model=self.config.model_name,
            provider=ModelProvider.CLAUDE,
            response_time_ms=0.0,
            error="Not implemented"
        )
    
    async def stream_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from Claude."""
        yield "Claude streaming not implemented yet"
    
    def validate_config(self) -> bool:
        """Validate Claude configuration."""
        return bool(self.config.api_key)


class LMStudioProvider(BaseModelProvider):
    """LMStudio local API provider implementation (placeholder)."""
    
    async def generate_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> ModelResponse:
        """Generate response using LMStudio."""
        # TODO: Implement LMStudio integration using HTTP requests
        return ModelResponse(
            content="LMStudio integration not implemented yet",
            model=self.config.model_name,
            provider=ModelProvider.LMSTUDIO,
            response_time_ms=0.0,
            error="Not implemented"
        )
    
    async def stream_response(
        self, 
        messages: List[ModelMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from LMStudio."""
        yield "LMStudio streaming not implemented yet"
    
    def validate_config(self) -> bool:
        """Validate LMStudio configuration."""
        return bool(self.config.base_url)


class ModelRouter:
    """Central router for managing multiple LLM providers."""
    
    def __init__(self):
        self._providers: Dict[str, BaseModelProvider] = {}
        self._default_model = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers."""
        # Gemini configuration
        if settings.GOOGLE_API_KEY:
            gemini_config = ModelConfig(
                provider=ModelProvider.GEMINI,
                model_name="gemini-1.5-flash",
                api_key=settings.GOOGLE_API_KEY,
                temperature=0.7,
                max_tokens=4096
            )
            self._providers["gemini-1.5-flash"] = GeminiProvider(gemini_config)
            self._default_model = "gemini-1.5-flash"
        
        # TODO: Add other providers based on environment variables
        # Example:
        # if settings.OPENAI_API_KEY:
        #     openai_config = ModelConfig(...)
        #     self._providers["gpt-4"] = OpenAIProvider(openai_config)
    
    def add_provider(self, model_name: str, provider: BaseModelProvider):
        """Add a custom provider."""
        self._providers[model_name] = provider
        if not self._default_model:
            self._default_model = model_name
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names."""
        return list(self._providers.keys())
    
    def get_provider(self, model_name: str) -> Optional[BaseModelProvider]:
        """Get provider for a specific model."""
        return self._providers.get(model_name)
    
    async def generate_response(
        self,
        messages: List[ModelMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate response using specified model or default."""
        model_name = model or self._default_model
        
        if not model_name:
            return ModelResponse(
                content="",
                model="unknown",
                provider=ModelProvider.GEMINI,
                response_time_ms=0.0,
                error="No models configured"
            )
        
        provider = self._providers.get(model_name)
        if not provider:
            return ModelResponse(
                content="",
                model=model_name,
                provider=ModelProvider.GEMINI,
                response_time_ms=0.0,
                error=f"Model {model_name} not available"
            )
        
        return await provider.generate_response(messages, **kwargs)
    
    async def stream_response(
        self,
        messages: List[ModelMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response using specified model or default."""
        model_name = model or self._default_model
        
        if not model_name:
            yield "Error: No models configured"
            return
        
        provider = self._providers.get(model_name)
        if not provider:
            yield f"Error: Model {model_name} not available"
            return
        
        async for chunk in provider.stream_response(messages, **kwargs):
            yield chunk


# Global model router instance
model_router = ModelRouter()