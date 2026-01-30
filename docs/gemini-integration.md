# Gemini 2.5 Flash Integration Guide

This guide covers the integration of Google's Gemini 2.5 Flash and other Gemini models into Cyber-AutoAgent.

## Overview

Gemini 2.5 Flash provides:
- **Fast response times** with efficient token usage
- **Large context windows** (up to 1M tokens for 2.5 Flash, 2M for 1.5 Pro)
- **Cost-effective** compared to other frontier models
- **Multi-modal capabilities** (text, images, etc.)
- **High-quality reasoning** across various tasks

## Supported Gemini Models

### LLM Models

| Model | Context Window | Max Output | Best For |
|-------|---------------|------------|----------|
| `gemini-2.5-flash` | 1M tokens | 8,192 | Fast, efficient general use (Recommended) |
| `gemini-2.5-flash-preview` | 1M tokens | 8,192 | Preview of latest features |
| `gemini-2.0-flash-exp` | 1M tokens | 8,192 | Experimental 2.0 version |
| `gemini-1.5-flash` | 1M tokens | 8,192 | Proven, stable 1.5 version |
| `gemini-1.5-flash-8b` | 1M tokens | 8,192 | Smaller, faster variant |
| `gemini-1.5-pro` | 2M tokens | 8,192 | Highest quality, largest context |

### Embedding Models

| Model | Dimensions | Use Case |
|-------|-----------|----------|
| `text-embedding-004` | 768 | Latest embedding model (Recommended) |
| `embedding-001` | 768 | Legacy embedding model |

## Quick Start

### 1. Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key for use below

### 2. Configure Environment

Add to your `.env` file:

```bash
# Use Gemini 2.5 Flash via LiteLLM
CYBER_AGENT_PROVIDER=litellm
CYBER_AGENT_LLM_MODEL=gemini/gemini-2.5-flash
CYBER_AGENT_EMBEDDING_MODEL=gemini/text-embedding-004
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Install Dependencies

Gemini requires the `google-genai` package:

```bash
pip install google-genai
# or
uv add google-genai
```

### 4. Run Agent

```bash
python src/cyberautoagent.py \
  --target "http://testphp.vulnweb.com" \
  --objective "Security assessment"
```

## Configuration Options

### Basic Configuration

```bash
# Minimal setup
CYBER_AGENT_PROVIDER=litellm
CYBER_AGENT_LLM_MODEL=gemini/gemini-2.5-flash
GEMINI_API_KEY=your_key
```

### Advanced Configuration

```bash
# Full configuration with all options
CYBER_AGENT_PROVIDER=litellm

# Main LLM Model
CYBER_AGENT_LLM_MODEL=gemini/gemini-2.5-flash
CYBER_AGENT_TEMPERATURE=0.95
CYBER_AGENT_MAX_TOKENS=8192

# Embedding Model
CYBER_AGENT_EMBEDDING_MODEL=gemini/text-embedding-004

# Memory/Evaluation Models (optional, defaults to main model)
CYBER_AGENT_EVALUATION_MODEL=gemini/gemini-1.5-flash
CYBER_AGENT_SWARM_MODEL=gemini/gemini-2.5-flash

# Gemini API Configuration
GEMINI_API_KEY=your_key
# GOOGLE_CLOUD_PROJECT=your-project-id  # Optional for Vertex AI
# GOOGLE_CLOUD_LOCATION=us-central1     # Optional for Vertex AI
```

### Hybrid Configurations

Combine Gemini with other providers for optimal cost/performance:

#### Gemini LLM + AWS Bedrock Embeddings

```bash
CYBER_AGENT_PROVIDER=litellm
CYBER_AGENT_LLM_MODEL=gemini/gemini-2.5-flash
CYBER_AGENT_EMBEDDING_MODEL=bedrock/amazon.titan-embed-text-v2:0
GEMINI_API_KEY=your_gemini_key
AWS_BEARER_TOKEN_BEDROCK=your_aws_token
AWS_REGION=us-east-1
```

#### Gemini LLM + OpenAI Embeddings

```bash
CYBER_AGENT_PROVIDER=litellm
CYBER_AGENT_LLM_MODEL=gemini/gemini-2.5-flash
CYBER_AGENT_EMBEDDING_MODEL=openai/text-embedding-3-small
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
```

## Model Selection Guide

### When to Use Gemini 2.5 Flash

✅ **Best for:**
- General security assessments
- Fast iteration and testing
- Cost-sensitive deployments
- Tasks requiring quick responses
- Projects with large context needs (1M tokens)

### When to Use Gemini 1.5 Pro

✅ **Best for:**
- Complex reasoning tasks
- Maximum context window needs (2M tokens)
- High-quality analysis requirements
- Deep code review scenarios

### When to Use Gemini 1.5 Flash

✅ **Best for:**
- Production stability (proven model)
- Lower-risk deployments
- Balanced cost/performance

## Pydantic Validation

The integration includes Pydantic models for type-safe configuration:

### Python API

```python
from modules.config.gemini_models import (
    GeminiLLMConfig,
    GeminiEmbeddingConfig,
    validate_gemini_llm_config,
    validate_gemini_embedding_config,
)

# Validate LLM configuration
llm_config = validate_gemini_llm_config(
    model_id="gemini/gemini-2.5-flash",
    temperature=0.9,
    max_tokens=4096,
    top_p=0.95,
)

# Validate embedding configuration
embed_config = validate_gemini_embedding_config(
    model_id="gemini/text-embedding-004",
    dimensions=768,
    task_type="RETRIEVAL_QUERY",
)

# Access configuration as dict
config_dict = llm_config.to_dict()
```

### Validation Features

- ✅ Model ID validation against supported models
- ✅ Parameter range validation (temperature, max_tokens)
- ✅ Embedding dimension validation
- ✅ Task type validation for embeddings
- ✅ Comprehensive error messages

## Performance Considerations

### Token Limits

| Model | Input Context | Output Tokens |
|-------|--------------|---------------|
| Gemini 2.5 Flash | 1,048,576 | 8,192 |
| Gemini 1.5 Pro | 2,097,152 | 8,192 |
| Gemini 1.5 Flash | 1,048,576 | 8,192 |

### Cost Optimization

1. **Use 2.5 Flash by default** - Best price/performance ratio
2. **Cache prompts** - Gemini supports prompt caching for repeated contexts
3. **Batch operations** - Process multiple targets in one session
4. **Monitor usage** - Track API usage via Google Cloud Console

### Rate Limits

- Free tier: 15 requests/minute, 1,500 requests/day
- Paid tier: 1,000+ requests/minute (varies by plan)
- Consider retry logic for rate limit errors

## Troubleshooting

### Common Issues

#### Missing google-genai Package

**Error:**
```
ModuleNotFoundError: No module named 'google.genai'
```

**Solution:**
```bash
pip install google-genai
```

#### Invalid API Key

**Error:**
```
AuthenticationError: Invalid API key
```

**Solution:**
1. Verify API key at https://aistudio.google.com/app/apikey
2. Check for whitespace in `.env` file
3. Ensure no quotes around the key value

#### Model Not Found

**Error:**
```
ValidationError: Invalid Gemini model: gemini-2.5-flash-exp
```

**Solution:**
Use one of the supported model names from the list above.

#### Rate Limit Exceeded

**Error:**
```
RateLimitError: Resource has been exhausted
```

**Solution:**
1. Implement exponential backoff
2. Reduce concurrent requests
3. Upgrade to paid tier
4. Add `CYBER_AGENT_MAX_RETRIES=5` to `.env`

## Testing

Run Gemini-specific tests:

```bash
# Test Pydantic validation
pytest tests/test_gemini_models.py -v

# Test configuration integration
pytest tests/test_config.py::TestConfigManager::test_litellm_gemini_2_5_flash_configuration -v

# Run all config tests
pytest tests/test_config.py -v -k gemini
```

## Migration Guide

### From OpenAI

```bash
# Before (OpenAI)
CYBER_AGENT_PROVIDER=litellm
CYBER_AGENT_LLM_MODEL=openai/gpt-4o
OPENAI_API_KEY=your_key

# After (Gemini)
CYBER_AGENT_PROVIDER=litellm
CYBER_AGENT_LLM_MODEL=gemini/gemini-2.5-flash
GEMINI_API_KEY=your_key
```

### From AWS Bedrock

```bash
# Before (Bedrock)
CYBER_AGENT_PROVIDER=bedrock
CYBER_AGENT_LLM_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0
AWS_BEARER_TOKEN_BEDROCK=your_token
AWS_REGION=us-east-1

# After (Gemini)
CYBER_AGENT_PROVIDER=litellm
CYBER_AGENT_LLM_MODEL=gemini/gemini-2.5-flash
GEMINI_API_KEY=your_key
```

### From Ollama

```bash
# Before (Ollama)
CYBER_AGENT_PROVIDER=ollama
CYBER_AGENT_LLM_MODEL=llama3.2:3b
OLLAMA_HOST=http://localhost:11434

# After (Gemini)
CYBER_AGENT_PROVIDER=litellm
CYBER_AGENT_LLM_MODEL=gemini/gemini-2.5-flash
GEMINI_API_KEY=your_key
```

## Best Practices

1. **Start with 2.5 Flash** - Best balance of speed/cost/quality
2. **Use Pydantic validation** - Catch configuration errors early
3. **Monitor costs** - Track usage via Google Cloud Console
4. **Implement retries** - Handle transient errors gracefully
5. **Test thoroughly** - Validate on test targets before production
6. **Keep context focused** - Larger contexts = higher costs
7. **Use hybrid configs** - Mix providers for optimal results

## Additional Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Gemini Pricing](https://ai.google.dev/pricing)
- [LiteLLM Gemini Integration](https://docs.litellm.ai/docs/providers/gemini)
- [Model Comparison](https://ai.google.dev/gemini-api/docs/models/gemini)

## Support

For issues or questions:
1. Check this documentation
2. Review test examples in `tests/test_gemini_models.py`
3. Check configuration examples in `.env.example`
4. Open an issue on GitHub
