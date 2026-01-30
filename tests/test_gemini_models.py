#!/usr/bin/env python3
"""
Tests for Gemini Pydantic model validation.
"""

import pytest
from pydantic import ValidationError

from modules.config.gemini_models import (
    GEMINI_EMBEDDING_DIMENSIONS,
    GEMINI_MODELS,
    GeminiAPIConfig,
    GeminiEmbeddingConfig,
    GeminiLLMConfig,
    validate_gemini_embedding_config,
    validate_gemini_llm_config,
)


class TestGeminiLLMConfig:
    """Test GeminiLLMConfig Pydantic model."""

    def test_valid_gemini_2_5_flash_config(self):
        """Test creating a valid Gemini 2.5 Flash configuration."""
        config = GeminiLLMConfig(
            model_id="gemini-2.5-flash",
            temperature=0.9,
            max_tokens=4096,
        )
        assert config.model_id == "gemini-2.5-flash"
        assert config.temperature == 0.9
        assert config.max_tokens == 4096
        assert config.top_p is None

    def test_valid_gemini_with_prefix(self):
        """Test that gemini/ prefix is handled correctly."""
        config = GeminiLLMConfig(
            model_id="gemini/gemini-2.5-flash",
            temperature=0.8,
            max_tokens=2048,
        )
        assert config.model_id == "gemini/gemini-2.5-flash"

    def test_valid_google_prefix(self):
        """Test that google/ prefix is handled correctly."""
        config = GeminiLLMConfig(
            model_id="google/gemini-2.5-flash",
            temperature=0.8,
            max_tokens=2048,
        )
        assert config.model_id == "google/gemini-2.5-flash"

    def test_invalid_model_id_raises_error(self):
        """Test that invalid model ID raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid Gemini model"):
            GeminiLLMConfig(
                model_id="invalid-model",
                temperature=0.9,
                max_tokens=2048,
            )

    def test_temperature_out_of_range_raises_error(self):
        """Test that temperature outside valid range raises ValidationError."""
        with pytest.raises(ValidationError):
            GeminiLLMConfig(
                model_id="gemini-2.5-flash",
                temperature=3.0,  # Too high
                max_tokens=2048,
            )

        with pytest.raises(ValidationError):
            GeminiLLMConfig(
                model_id="gemini-2.5-flash",
                temperature=-0.1,  # Too low
                max_tokens=2048,
            )

    def test_max_tokens_exceeds_limit_raises_error(self):
        """Test that max_tokens exceeding model limit raises ValidationError."""
        with pytest.raises(ValidationError, match="max_tokens.*exceeds maximum"):
            GeminiLLMConfig(
                model_id="gemini-2.5-flash",
                temperature=0.9,
                max_tokens=10000,  # Exceeds 8192 limit
            )

    def test_top_p_validation(self):
        """Test that top_p is properly validated."""
        # Valid top_p
        config = GeminiLLMConfig(
            model_id="gemini-2.5-flash",
            temperature=0.9,
            max_tokens=2048,
            top_p=0.95,
        )
        assert config.top_p == 0.95

        # Invalid top_p (too high)
        with pytest.raises(ValidationError):
            GeminiLLMConfig(
                model_id="gemini-2.5-flash",
                temperature=0.9,
                max_tokens=2048,
                top_p=1.5,
            )

    def test_top_k_validation(self):
        """Test that top_k is properly validated."""
        config = GeminiLLMConfig(
            model_id="gemini-2.5-flash",
            temperature=0.9,
            max_tokens=2048,
            top_k=40,
        )
        assert config.top_k == 40

        # Invalid top_k (non-positive)
        with pytest.raises(ValidationError):
            GeminiLLMConfig(
                model_id="gemini-2.5-flash",
                temperature=0.9,
                max_tokens=2048,
                top_k=0,
            )

    def test_candidate_count_validation(self):
        """Test that candidate_count is properly validated."""
        config = GeminiLLMConfig(
            model_id="gemini-2.5-flash",
            temperature=0.9,
            max_tokens=2048,
            candidate_count=3,
        )
        assert config.candidate_count == 3

        # Invalid candidate_count (less than 1)
        with pytest.raises(ValidationError):
            GeminiLLMConfig(
                model_id="gemini-2.5-flash",
                temperature=0.9,
                max_tokens=2048,
                candidate_count=0,
            )

    def test_stop_sequences(self):
        """Test that stop_sequences are properly handled."""
        config = GeminiLLMConfig(
            model_id="gemini-2.5-flash",
            temperature=0.9,
            max_tokens=2048,
            stop_sequences=["STOP", "END"],
        )
        assert config.stop_sequences == ["STOP", "END"]

    def test_to_dict_method(self):
        """Test that to_dict() method works correctly."""
        config = GeminiLLMConfig(
            model_id="gemini-2.5-flash",
            temperature=0.9,
            max_tokens=2048,
            top_p=0.95,
            top_k=40,
        )
        result = config.to_dict()
        
        assert result["model_id"] == "gemini-2.5-flash"
        assert result["temperature"] == 0.9
        assert result["max_tokens"] == 2048
        assert result["top_p"] == 0.95
        assert result["top_k"] == 40

    def test_to_dict_excludes_none_values(self):
        """Test that to_dict() excludes None values."""
        config = GeminiLLMConfig(
            model_id="gemini-2.5-flash",
            temperature=0.9,
            max_tokens=2048,
        )
        result = config.to_dict()
        
        assert "top_p" not in result
        assert "top_k" not in result

    def test_all_supported_models(self):
        """Test that all supported Gemini models can be validated."""
        for model in GEMINI_MODELS:
            config = GeminiLLMConfig(
                model_id=model,
                temperature=0.9,
                max_tokens=2048,
            )
            assert config.model_id == model

    def test_gemini_2_0_flash_thinking_model(self):
        """Test Gemini 2.0 Flash Thinking model configuration."""
        config = GeminiLLMConfig(
            model_id="gemini-2.0-flash-thinking-exp-1219",
            temperature=1.0,
            max_tokens=4096,
        )
        assert config.model_id == "gemini-2.0-flash-thinking-exp-1219"


class TestGeminiEmbeddingConfig:
    """Test GeminiEmbeddingConfig Pydantic model."""

    def test_valid_text_embedding_004(self):
        """Test creating a valid text-embedding-004 configuration."""
        config = GeminiEmbeddingConfig(
            model_id="models/text-embedding-004",
            dimensions=768,
        )
        assert config.model_id == "models/text-embedding-004"
        assert config.dimensions == 768

    def test_text_embedding_004_without_prefix(self):
        """Test text-embedding-004 without models/ prefix."""
        config = GeminiEmbeddingConfig(
            model_id="text-embedding-004",
            dimensions=768,
        )
        assert config.model_id == "text-embedding-004"
        assert config.dimensions == 768

    def test_invalid_embedding_model_raises_error(self):
        """Test that invalid embedding model raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid Gemini embedding model"):
            GeminiEmbeddingConfig(
                model_id="invalid-embedding-model",
                dimensions=768,
            )

    def test_incorrect_dimensions_raises_error(self):
        """Test that incorrect dimensions raise ValidationError."""
        with pytest.raises(ValidationError, match="Invalid dimensions"):
            GeminiEmbeddingConfig(
                model_id="models/text-embedding-004",
                dimensions=1536,  # Wrong, should be 768
            )

    def test_task_type_validation(self):
        """Test that task_type is properly validated."""
        config = GeminiEmbeddingConfig(
            model_id="models/text-embedding-004",
            dimensions=768,
            task_type="RETRIEVAL_QUERY",
        )
        assert config.task_type == "RETRIEVAL_QUERY"

        # Invalid task_type
        with pytest.raises(ValidationError):
            GeminiEmbeddingConfig(
                model_id="models/text-embedding-004",
                dimensions=768,
                task_type="INVALID_TASK",
            )

    def test_to_dict_method(self):
        """Test that to_dict() method works correctly."""
        config = GeminiEmbeddingConfig(
            model_id="models/text-embedding-004",
            dimensions=768,
            task_type="RETRIEVAL_DOCUMENT",
        )
        result = config.to_dict()
        
        assert result["model_id"] == "models/text-embedding-004"
        assert result["dimensions"] == 768
        assert result["task_type"] == "RETRIEVAL_DOCUMENT"

    def test_to_dict_excludes_none_task_type(self):
        """Test that to_dict() excludes None task_type."""
        config = GeminiEmbeddingConfig(
            model_id="models/text-embedding-004",
            dimensions=768,
        )
        result = config.to_dict()
        
        assert "task_type" not in result

    def test_all_embedding_dimensions(self):
        """Test that all embedding models have correct dimensions."""
        for model, dims in GEMINI_EMBEDDING_DIMENSIONS.items():
            config = GeminiEmbeddingConfig(
                model_id=model,
                dimensions=dims,
            )
            assert config.dimensions == dims


class TestGeminiAPIConfig:
    """Test GeminiAPIConfig Pydantic model."""

    def test_valid_api_config(self):
        """Test creating a valid Gemini API configuration."""
        config = GeminiAPIConfig(
            api_key="test_api_key_12345",
        )
        assert config.api_key == "test_api_key_12345"
        assert config.project_id is None
        assert config.location is None

    def test_empty_api_key_raises_error(self):
        """Test that empty API key raises ValidationError."""
        with pytest.raises(ValidationError, match="API key cannot be empty"):
            GeminiAPIConfig(api_key="")

        with pytest.raises(ValidationError, match="API key cannot be empty"):
            GeminiAPIConfig(api_key="   ")

    def test_with_project_id_and_location(self):
        """Test API config with project ID and location."""
        config = GeminiAPIConfig(
            api_key="test_api_key_12345",
            project_id="my-gcp-project",
            location="us-central1",
        )
        assert config.project_id == "my-gcp-project"
        assert config.location == "us-central1"


class TestHelperFunctions:
    """Test helper validation functions."""

    def test_validate_gemini_llm_config(self):
        """Test validate_gemini_llm_config helper function."""
        config = validate_gemini_llm_config(
            model_id="gemini-2.5-flash",
            temperature=0.8,
            max_tokens=4096,
        )
        assert isinstance(config, GeminiLLMConfig)
        assert config.model_id == "gemini-2.5-flash"
        assert config.temperature == 0.8
        assert config.max_tokens == 4096

    def test_validate_gemini_llm_config_with_kwargs(self):
        """Test validate_gemini_llm_config with additional kwargs."""
        config = validate_gemini_llm_config(
            model_id="gemini-2.5-flash",
            temperature=0.8,
            max_tokens=4096,
            top_p=0.95,
            top_k=40,
        )
        assert config.top_p == 0.95
        assert config.top_k == 40

    def test_validate_gemini_embedding_config(self):
        """Test validate_gemini_embedding_config helper function."""
        config = validate_gemini_embedding_config(
            model_id="models/text-embedding-004",
            dimensions=768,
        )
        assert isinstance(config, GeminiEmbeddingConfig)
        assert config.model_id == "models/text-embedding-004"
        assert config.dimensions == 768

    def test_validate_gemini_embedding_config_with_kwargs(self):
        """Test validate_gemini_embedding_config with additional kwargs."""
        config = validate_gemini_embedding_config(
            model_id="models/text-embedding-004",
            dimensions=768,
            task_type="SEMANTIC_SIMILARITY",
        )
        assert config.task_type == "SEMANTIC_SIMILARITY"

    def test_validate_gemini_llm_config_invalid_raises_error(self):
        """Test that invalid config raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_gemini_llm_config(
                model_id="invalid-model",
                temperature=0.8,
                max_tokens=4096,
            )

    def test_validate_gemini_embedding_config_invalid_raises_error(self):
        """Test that invalid embedding config raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_gemini_embedding_config(
                model_id="models/text-embedding-004",
                dimensions=1536,  # Wrong dimension
            )
