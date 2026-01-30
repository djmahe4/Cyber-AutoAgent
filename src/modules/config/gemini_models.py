#!/usr/bin/env python3
"""
Pydantic models for Gemini 2.5 Flash configuration validation.

This module provides type-safe validation for Gemini model configurations,
ensuring that model IDs, parameters, and API keys are properly validated.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# Supported Gemini models
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-preview",
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-thinking-exp-1219",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-pro",
]

# Supported Gemini embedding models
GEMINI_EMBEDDING_MODELS = [
    "models/text-embedding-004",
    "text-embedding-004",
    "models/embedding-001",
    "embedding-001",
]

# Model-specific configurations
GEMINI_MODEL_CONFIGS = {
    "gemini-2.5-flash": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 2.0),
        "context_window": 1048576,  # 1M tokens
        "supports_thinking": False,
    },
    "gemini-2.5-flash-preview": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 2.0),
        "context_window": 1048576,
        "supports_thinking": False,
    },
    "gemini-2.0-flash-exp": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 2.0),
        "context_window": 1048576,
        "supports_thinking": False,
    },
    "gemini-2.0-flash-thinking-exp-1219": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 2.0),
        "context_window": 32768,
        "supports_thinking": True,
    },
    "gemini-1.5-flash": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 2.0),
        "context_window": 1048576,
        "supports_thinking": False,
    },
    "gemini-1.5-flash-8b": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 2.0),
        "context_window": 1048576,
        "supports_thinking": False,
    },
    "gemini-1.5-pro": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 2.0),
        "context_window": 2097152,  # 2M tokens
        "supports_thinking": False,
    },
}

# Embedding dimensions by model
GEMINI_EMBEDDING_DIMENSIONS = {
    "models/text-embedding-004": 768,
    "text-embedding-004": 768,
    "models/embedding-001": 768,
    "embedding-001": 768,
}


class GeminiLLMConfig(BaseModel):
    """Pydantic model for Gemini LLM configuration with validation.
    
    Validates model ID, temperature, max_tokens, and other parameters
    according to Gemini API specifications.
    """
    
    model_id: str = Field(
        description="Gemini model identifier (e.g., gemini-2.5-flash)"
    )
    temperature: float = Field(
        default=0.95,
        ge=0.0,
        le=2.0,
        description="Sampling temperature between 0.0 and 2.0"
    )
    max_tokens: int = Field(
        default=8192,
        gt=0,
        le=8192,
        description="Maximum number of tokens to generate"
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter (0.0 to 1.0)"
    )
    top_k: Optional[int] = Field(
        default=None,
        gt=0,
        description="Top-k sampling parameter"
    )
    candidate_count: Optional[int] = Field(
        default=1,
        ge=1,
        description="Number of response candidates to generate"
    )
    stop_sequences: Optional[List[str]] = Field(
        default=None,
        description="List of sequences that will stop generation"
    )
    
    @field_validator("model_id")
    @classmethod
    def validate_model_id(cls, v: str) -> str:
        """Validate that the model ID is a supported Gemini model."""
        # Extract model name without provider prefix
        model_name = v.replace("gemini/", "").replace("google/", "")
        
        if model_name not in GEMINI_MODELS:
            raise ValueError(
                f"Invalid Gemini model: {v}. "
                f"Supported models: {', '.join(GEMINI_MODELS)}"
            )
        return v
    
    @model_validator(mode="after")
    def validate_model_specific_params(self) -> "GeminiLLMConfig":
        """Validate parameters are within model-specific limits."""
        model_name = self.model_id.replace("gemini/", "").replace("google/", "")
        
        if model_name in GEMINI_MODEL_CONFIGS:
            config = GEMINI_MODEL_CONFIGS[model_name]
            
            # Validate temperature range
            temp_min, temp_max = config["temperature_range"]
            if not temp_min <= self.temperature <= temp_max:
                raise ValueError(
                    f"Temperature {self.temperature} outside valid range "
                    f"[{temp_min}, {temp_max}] for {model_name}"
                )
            
            # Validate max_tokens
            if self.max_tokens > config["max_tokens"]:
                raise ValueError(
                    f"max_tokens {self.max_tokens} exceeds maximum "
                    f"{config['max_tokens']} for {model_name}"
                )
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for use in configuration."""
        result = {
            "model_id": self.model_id,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if self.top_p is not None:
            result["top_p"] = self.top_p
        if self.top_k is not None:
            result["top_k"] = self.top_k
        if self.candidate_count is not None and self.candidate_count != 1:
            result["candidate_count"] = self.candidate_count
        if self.stop_sequences:
            result["stop_sequences"] = self.stop_sequences
        
        return result


class GeminiEmbeddingConfig(BaseModel):
    """Pydantic model for Gemini embedding configuration with validation.
    
    Validates embedding model ID and dimensions according to Gemini specifications.
    """
    
    model_id: str = Field(
        description="Gemini embedding model identifier"
    )
    dimensions: int = Field(
        default=768,
        description="Embedding dimension size"
    )
    task_type: Optional[Literal[
        "RETRIEVAL_QUERY",
        "RETRIEVAL_DOCUMENT",
        "SEMANTIC_SIMILARITY",
        "CLASSIFICATION",
        "CLUSTERING"
    ]] = Field(
        default=None,
        description="Task type for embedding optimization"
    )
    
    @field_validator("model_id")
    @classmethod
    def validate_embedding_model_id(cls, v: str) -> str:
        """Validate that the model ID is a supported Gemini embedding model."""
        # Extract model name without provider prefix
        model_name = v.replace("gemini/", "").replace("google/", "")
        
        if model_name not in GEMINI_EMBEDDING_MODELS:
            raise ValueError(
                f"Invalid Gemini embedding model: {v}. "
                f"Supported models: {', '.join(GEMINI_EMBEDDING_MODELS)}"
            )
        return v
    
    @model_validator(mode="after")
    def validate_dimensions(self) -> "GeminiEmbeddingConfig":
        """Validate that dimensions match the model's specification."""
        model_name = self.model_id.replace("gemini/", "").replace("google/", "")
        
        if model_name in GEMINI_EMBEDDING_DIMENSIONS:
            expected_dims = GEMINI_EMBEDDING_DIMENSIONS[model_name]
            if self.dimensions != expected_dims:
                raise ValueError(
                    f"Invalid dimensions {self.dimensions} for {model_name}. "
                    f"Expected: {expected_dims}"
                )
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for use in configuration."""
        result = {
            "model_id": self.model_id,
            "dimensions": self.dimensions,
        }
        
        if self.task_type is not None:
            result["task_type"] = self.task_type
        
        return result


class GeminiAPIConfig(BaseModel):
    """Pydantic model for Gemini API configuration.
    
    Validates API key and other Gemini-specific settings.
    """
    
    api_key: str = Field(
        description="Gemini API key",
        min_length=1
    )
    project_id: Optional[str] = Field(
        default=None,
        description="Google Cloud project ID (optional)"
    )
    location: Optional[str] = Field(
        default=None,
        description="Google Cloud location (optional)"
    )
    
    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or v.isspace():
            raise ValueError("API key cannot be empty")
        return v


def validate_gemini_llm_config(
    model_id: str,
    temperature: float = 0.95,
    max_tokens: int = 8192,
    **kwargs
) -> GeminiLLMConfig:
    """Helper function to validate Gemini LLM configuration.
    
    Args:
        model_id: Gemini model identifier
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        **kwargs: Additional configuration parameters
    
    Returns:
        Validated GeminiLLMConfig instance
    
    Raises:
        ValidationError: If configuration is invalid
    """
    return GeminiLLMConfig(
        model_id=model_id,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def validate_gemini_embedding_config(
    model_id: str,
    dimensions: int = 768,
    **kwargs
) -> GeminiEmbeddingConfig:
    """Helper function to validate Gemini embedding configuration.
    
    Args:
        model_id: Gemini embedding model identifier
        dimensions: Embedding dimensions
        **kwargs: Additional configuration parameters
    
    Returns:
        Validated GeminiEmbeddingConfig instance
    
    Raises:
        ValidationError: If configuration is invalid
    """
    return GeminiEmbeddingConfig(
        model_id=model_id,
        dimensions=dimensions,
        **kwargs
    )
