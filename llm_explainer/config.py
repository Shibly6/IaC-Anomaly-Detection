"""
Configuration for LLM Explainer Module
"""

import os

# Ollama API Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_API_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"

# Available models (from user's ollama list)
AVAILABLE_MODELS = {
    "gemma3:1b": {
        "name": "gemma3:1b",
        "size": "815 MB",
        "description": "Fast, lightweight model for quick explanations",
        "max_tokens": 1024,  # Reduced for faster processing
        "temperature": 0.7
    },
    "deepseek-r1:1.5b": {
        "name": "deepseek-r1:1.5b", 
        "size": "1.1 GB",
        "description": "More capable model for detailed analysis",
        "max_tokens": 2048,  # Reduced for faster processing
        "temperature": 0.7
    }
}

# Default model preference - using lighter model for weak hardware
DEFAULT_MODEL = "gemma3:1b"

# Prompt Engineering Parameters
MAX_CONTEXT_LENGTH = 1000  # Reduced to speed up processing on weak hardware
TEMPERATURE = 0.7  # Balance between creativity and consistency
TOP_P = 0.9
TOP_K = 40

# Cache Configuration
ENABLE_CACHE = True
CACHE_DIR = "data/output/explanations/cache"
CACHE_EXPIRY_DAYS = 7

# Report Configuration
REPORT_OUTPUT_DIR = "data/output/explanations"
REPORT_FORMATS = ["markdown", "html", "json"]

# Anomaly Severity Thresholds
SEVERITY_THRESHOLDS = {
    "critical": 0.9,  # Anomaly score >= 0.9
    "high": 0.7,      # Anomaly score >= 0.7
    "medium": 0.5,    # Anomaly score >= 0.5
    "low": 0.3        # Anomaly score >= 0.3
}

# Timeout settings
API_TIMEOUT = 1000  # seconds for LLM processing (very generous for weak hardware)
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Performance settings for weak hardware
BATCH_SIZE = 5  # Process anomalies in small batches to show progress
SHOW_PROGRESS = True  # Show detailed progress for each LLM call
