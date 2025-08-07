# ModelRouter Service Usage Guide

## Overview

The ModelRouter service provides a unified interface for interacting with multiple LLM providers in the Elenchus backend. It supports Google Gemini out of the box and is designed to easily integrate additional providers like OpenAI, Claude, and LMStudio.

## Architecture

### Core Components

1. **ModelRouter** - Central service that routes requests to appropriate providers
2. **BaseModelProvider** - Abstract base class for all LLM providers
3. **Provider Implementations** - Concrete implementations for each LLM service
4. **ModelConfig** - Configuration class for each model
5. **Standardized Message/Response Format** - Consistent data structures across providers

### Supported Providers

- ✅ **Google Gemini** - Fully implemented with 1.5-flash model
- 🚧 **OpenAI** - Placeholder implementation (ready for development)
- 🚧 **Claude** - Placeholder implementation (ready for development)
- 🚧 **LMStudio** - Placeholder implementation (ready for development)

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Google Gemini
GOOGLE_API_KEY=your_gemini_api_key_here

# OpenAI (future)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude (future)
ANTHROPIC_API_KEY=your_claude_api_key_here

# LMStudio Local (future)
LMSTUDIO_BASE_URL=http://localhost:1234
```

### Automatic Provider Discovery

The ModelRouter automatically initializes providers based on available API keys:

- If `GOOGLE_API_KEY` is set → Gemini provider is enabled
- If `OPENAI_API_KEY` is set → OpenAI provider will be enabled (when implemented)
- And so on...

## Usage Examples

### 1. Basic Message Generation

```python
from app.services.model_router import model_router, ModelMessage, ModelRole

# Create conversation messages
messages = [
    ModelMessage(
        role=ModelRole.SYSTEM,
        content="You are a helpful legal assistant."
    ),
    ModelMessage(
        role=ModelRole.USER,
        content="Explain the difference between civil and criminal law."
    )
]

# Generate response
response = await model_router.generate_response(
    messages=messages,
    model="gemini-1.5-flash"  # Optional - uses default if not specified
)

# Handle response
if response.error:
    print(f"Error: {response.error}")
else:
    print(f"Response: {response.content}")
    print(f"Model: {response.model}")
    print(f"Provider: {response.provider}")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Response time: {response.response_time_ms}ms")
```

### 2. Multi-turn Conversation

```python
# Build conversation context
conversation = [
    ModelMessage(role=ModelRole.SYSTEM, content="You are Elenchus, a legal AI assistant."),
    ModelMessage(role=ModelRole.USER, content="What is a contract?"),
    ModelMessage(role=ModelRole.ASSISTANT, content="A contract is a legally binding agreement..."),
    ModelMessage(role=ModelRole.USER, content="What makes a contract valid?")
]

response = await model_router.generate_response(messages=conversation)
```

### 3. Streaming Responses (Future Feature)

```python
# Stream response as it's generated
async for chunk in model_router.stream_response(
    messages=messages,
    model="gemini-1.5-flash"
):
    print(chunk, end="", flush=True)
```

### 4. Model Management

```python
# Get available models
available_models = model_router.get_available_models()
print(f"Available models: {available_models}")

# Get specific provider
provider = model_router.get_provider("gemini-1.5-flash")
if provider:
    is_healthy = provider.validate_config()
    print(f"Provider healthy: {is_healthy}")
```

## API Endpoints

### List Available Models
```http
GET /api/v1/models/
```

### Get Model Information
```http
GET /api/v1/models/info
```

### Test a Model
```http
POST /api/v1/models/test
Content-Type: application/json

{
  "message": "Hello, world!",
  "model": "gemini-1.5-flash"
}
```

### Check Models Health
```http
GET /api/v1/models/health
```

## Integration with Messages API

The `/api/v1/messages/research/{research_id}/send` endpoint now uses the ModelRouter:

1. **Context Building** - Fetches conversation history and builds context
2. **Model Selection** - Uses the model specified in the Research document
3. **Response Generation** - Calls ModelRouter to generate response
4. **Error Handling** - Properly handles and logs any errors
5. **Message Storage** - Saves both user and assistant messages to database

### Example Message Flow

```python
# User sends message
{
  "message": "Analyze this contract clause",
  "context": {
    "use_sources": true,
    "use_notes": false
  }
}

# System:
# 1. Creates user message in database
# 2. Builds conversation context with system prompt + history
# 3. Calls ModelRouter.generate_response()
# 4. Creates assistant message with response
# 5. Returns both messages to client
```

## Adding New Providers

### 1. Create Provider Class

```python
class NewProviderProvider(BaseModelProvider):
    async def generate_response(self, messages: List[ModelMessage], **kwargs) -> ModelResponse:
        # Implement provider-specific logic
        pass
    
    async def stream_response(self, messages: List[ModelMessage], **kwargs) -> AsyncGenerator[str, None]:
        # Implement streaming if supported
        pass
    
    def validate_config(self) -> bool:
        # Validate API keys/configuration
        pass
```

### 2. Register with ModelRouter

```python
# In ModelRouter._initialize_providers()
if settings.NEW_PROVIDER_API_KEY:
    config = ModelConfig(
        provider=ModelProvider.NEW_PROVIDER,
        model_name="new-provider-model",
        api_key=settings.NEW_PROVIDER_API_KEY
    )
    self._providers["new-provider-model"] = NewProviderProvider(config)
```

### 3. Add Environment Variable Support

```python
# In settings.py
NEW_PROVIDER_API_KEY: Optional[str] = Field(None, env="NEW_PROVIDER_API_KEY")
```

## Error Handling

The ModelRouter provides comprehensive error handling:

- **Configuration Errors** - Invalid API keys, missing settings
- **Network Errors** - Connection timeouts, API unavailability  
- **Rate Limiting** - Provider-specific rate limit handling
- **Content Filtering** - Provider content policy violations
- **Token Limits** - Exceeding model context/output limits

All errors are captured in the `ModelResponse.error` field and logged appropriately.

## Performance Considerations

- **Async/Await** - All operations are fully asynchronous
- **Connection Pooling** - Providers should implement connection reuse
- **Context Management** - Automatic conversation history trimming
- **Caching** - Future enhancement for response caching
- **Load Balancing** - Future enhancement for multi-instance deployments

## Security

- **API Key Management** - Secure environment variable storage
- **Input Sanitization** - Message content validation
- **Rate Limiting** - Provider-specific rate limit compliance
- **Audit Logging** - All model interactions are logged
- **PII Protection** - Content filtering for sensitive data

## Monitoring & Observability

Each model interaction captures:

- Response time metrics
- Token usage statistics
- Error rates and types
- Provider availability
- Model performance metrics

These metrics can be integrated with monitoring systems for operational insights.

## Future Enhancements

1. **Response Caching** - Cache responses for identical inputs
2. **Load Balancing** - Distribute requests across multiple providers
3. **Fallback Logic** - Automatic fallback to alternative providers
4. **Cost Optimization** - Route requests to most cost-effective provider
5. **A/B Testing** - Compare responses across different models
6. **Fine-tuning** - Support for custom model training
7. **Batch Processing** - Process multiple requests efficiently