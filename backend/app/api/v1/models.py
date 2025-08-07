"""Models API endpoints for managing available LLM models."""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.model_router import model_router, ModelMessage, ModelRole, ModelProvider


class ModelInfo(BaseModel):
    """Information about an available model."""
    name: str
    provider: ModelProvider
    enabled: bool


class ModelTestRequest(BaseModel):
    """Request for testing a model."""
    message: str
    model: str


class ModelTestResponse(BaseModel):
    """Response from model test."""
    message: str
    response: str
    model: str
    provider: str
    tokens_used: int = None
    response_time_ms: float
    error: str = None


router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", response_model=List[str])
async def list_available_models() -> List[str]:
    """Get list of available models."""
    try:
        models = model_router.get_available_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")


@router.get("/info")
async def get_models_info() -> Dict[str, Any]:
    """Get detailed information about available models."""
    try:
        available_models = model_router.get_available_models()
        
        models_info = []
        for model_name in available_models:
            provider = model_router.get_provider(model_name)
            if provider:
                models_info.append({
                    "name": model_name,
                    "provider": provider.config.provider.value,
                    "enabled": provider.config.enabled,
                    "max_tokens": provider.config.max_tokens,
                    "temperature": provider.config.temperature
                })
        
        return {
            "total_models": len(models_info),
            "models": models_info,
            "default_model": model_router._default_model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models info: {str(e)}")


@router.post("/test", response_model=ModelTestResponse)
async def test_model(request: ModelTestRequest) -> ModelTestResponse:
    """Test a model with a simple message."""
    try:
        # Create test message
        test_messages = [
            ModelMessage(
                role=ModelRole.SYSTEM,
                content="You are a helpful assistant. Respond briefly and clearly."
            ),
            ModelMessage(
                role=ModelRole.USER,
                content=request.message
            )
        ]
        
        # Generate response
        response = await model_router.generate_response(
            messages=test_messages,
            model=request.model
        )
        
        return ModelTestResponse(
            message=request.message,
            response=response.content,
            model=response.model,
            provider=response.provider.value,
            tokens_used=response.tokens_used,
            response_time_ms=response.response_time_ms,
            error=response.error
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test model: {str(e)}")


@router.get("/health")
async def check_models_health() -> Dict[str, Any]:
    """Check the health status of all configured models."""
    try:
        available_models = model_router.get_available_models()
        health_status = {}
        
        for model_name in available_models:
            provider = model_router.get_provider(model_name)
            if provider:
                try:
                    # Quick validation check
                    is_valid = provider.validate_config()
                    health_status[model_name] = {
                        "status": "healthy" if is_valid else "configuration_error",
                        "provider": provider.config.provider.value,
                        "enabled": provider.config.enabled
                    }
                except Exception as e:
                    health_status[model_name] = {
                        "status": "error",
                        "provider": provider.config.provider.value if provider.config else "unknown",
                        "error": str(e)
                    }
        
        overall_status = "healthy" if all(
            status["status"] == "healthy" 
            for status in health_status.values()
        ) else "degraded"
        
        return {
            "overall_status": overall_status,
            "models": health_status,
            "total_models": len(health_status)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check models health: {str(e)}")