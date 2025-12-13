"""
Ollama Client - Interface to Ollama API for LLM inference
"""

import requests
import json
import logging
import time
from typing import Dict, List, Optional, Any
from . import config

logger = logging.getLogger("anomaly_detector.llm_explainer")


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, model_name: str = None, base_url: str = None):
        """
        Initialize Ollama client
        
        Args:
            model_name: Name of the Ollama model to use (default: from config)
            base_url: Base URL for Ollama API (default: from config)
        """
        self.model_name = model_name or config.DEFAULT_MODEL
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.chat_endpoint = f"{self.base_url}/api/chat"
        self.tags_endpoint = f"{self.base_url}/api/tags"
        
        # Validate model is available
        self._validate_model()
    
    def _validate_model(self) -> bool:
        """Check if the selected model is available in Ollama"""
        try:
            response = requests.get(self.tags_endpoint, timeout=5)
            response.raise_for_status()
            
            available_models = response.json().get('models', [])
            model_names = [m['name'] for m in available_models]
            
            if self.model_name not in model_names:
                logger.warning(
                    f"Model '{self.model_name}' not found. Available models: {model_names}"
                )
                # Try to use first available model
                if model_names:
                    self.model_name = model_names[0]
                    logger.info(f"Falling back to model: {self.model_name}")
                else:
                    raise ValueError("No Ollama models available")
            
            logger.info(f"Using Ollama model: {self.model_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Ollama API at {self.base_url}: {e}")
            raise ConnectionError(
                f"Cannot connect to Ollama. Make sure Ollama is running at {self.base_url}"
            )
    
    def generate(
        self, 
        prompt: str, 
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate text using Ollama API
        
        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature (default: from config)
            max_tokens: Maximum tokens to generate (default: from config)
            stream: Whether to stream the response
            
        Returns:
            Dictionary with 'response' and 'metadata'
        """
        temperature = temperature or config.TEMPERATURE
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": config.TOP_P,
                "top_k": config.TOP_K
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        for attempt in range(config.MAX_RETRIES):
            try:
                logger.info(f"Sending request to Ollama (model: {self.model_name}, attempt {attempt + 1}/{config.MAX_RETRIES})...")
                start_time = time.time()
                
                response = requests.post(
                    self.generate_endpoint,
                    json=payload,
                    timeout=config.API_TIMEOUT
                )
                response.raise_for_status()
                
                elapsed = time.time() - start_time
                logger.info(f"✓ Received response in {elapsed:.1f}s")
                
                result = response.json()
                
                return {
                    "response": result.get("response", ""),
                    "metadata": {
                        "model": result.get("model"),
                        "created_at": result.get("created_at"),
                        "done": result.get("done"),
                        "total_duration": result.get("total_duration"),
                        "load_duration": result.get("load_duration"),
                        "prompt_eval_count": result.get("prompt_eval_count"),
                        "eval_count": result.get("eval_count"),
                        "elapsed_seconds": elapsed
                    }
                }
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{config.MAX_RETRIES})")
                if attempt < config.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {config.RETRY_DELAY} seconds...")
                    time.sleep(config.RETRY_DELAY)
                else:
                    raise
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                if attempt < config.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {config.RETRY_DELAY} seconds...")
                    time.sleep(config.RETRY_DELAY)
                else:
                    raise
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Chat completion using Ollama API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            Dictionary with 'message' and 'metadata'
        """
        temperature = temperature or config.TEMPERATURE
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": config.TOP_P,
                "top_k": config.TOP_K
            }
        }
        
        try:
            response = requests.post(
                self.chat_endpoint,
                json=payload,
                timeout=config.API_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "message": result.get("message", {}),
                "metadata": {
                    "model": result.get("model"),
                    "created_at": result.get("created_at"),
                    "done": result.get("done")
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Chat API request failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test if Ollama is accessible and responding"""
        try:
            test_prompt = "Hello, respond with 'OK' if you can read this."
            result = self.generate(test_prompt, max_tokens=10)
            return bool(result.get("response"))
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


if __name__ == "__main__":
    # Test the client
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        client = OllamaClient()
        print(f"✓ Connected to Ollama")
        print(f"✓ Using model: {client.model_name}")
        
        if "--test" in sys.argv:
            print("\nTesting generation...")
            result = client.generate("Explain what Infrastructure as Code means in one sentence.")
            print(f"Response: {result['response']}")
            print(f"✓ Generation test passed")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
