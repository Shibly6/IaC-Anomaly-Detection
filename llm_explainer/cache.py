"""
Simple file-based cache for LLM responses

Avoids regenerating explanations for identical anomalies.
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from . import config

logger = logging.getLogger("anomaly_detector.llm_explainer")


class ExplanationCache:
    """Simple file-based cache for LLM explanations"""
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files (default: from config)
        """
        self.cache_dir = cache_dir or config.CACHE_DIR
        self.enabled = config.ENABLE_CACHE
        
        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, context: Dict[str, Any], prompt: str) -> str:
        """
        Generate cache key from context and prompt
        
        Args:
            context: Anomaly context dictionary
            prompt: The prompt used
            
        Returns:
            Cache key (hash)
        """
        # Create a stable string representation
        cache_data = {
            'bucket_name': context.get('bucket_name'),
            'acl': context.get('acl'),
            'is_public_acl': context.get('is_public_acl'),
            'encryption_enabled': context.get('encryption_enabled'),
            'versioning_enabled': context.get('versioning_enabled'),
            'logging_enabled': context.get('logging_enabled'),
            'prompt_hash': hashlib.md5(prompt.encode()).hexdigest()[:8]
        }
        
        # Create hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_str.encode()).hexdigest()
        
        return cache_hash
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get file path for cache key"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, context: Dict[str, Any], prompt: str) -> Optional[str]:
        """
        Get cached explanation if available and not expired
        
        Args:
            context: Anomaly context
            prompt: The prompt used
            
        Returns:
            Cached explanation or None
        """
        if not self.enabled:
            return None
        
        cache_key = self._get_cache_key(context, prompt)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check expiry
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            expiry_time = cached_time + timedelta(days=config.CACHE_EXPIRY_DAYS)
            
            if datetime.now() > expiry_time:
                logger.debug(f"Cache expired for key {cache_key}")
                os.remove(cache_path)
                return None
            
            logger.info(f"Cache hit for key {cache_key}")
            return cache_data['explanation']
            
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def set(self, context: Dict[str, Any], prompt: str, explanation: str):
        """
        Store explanation in cache
        
        Args:
            context: Anomaly context
            prompt: The prompt used
            explanation: The generated explanation
        """
        if not self.enabled:
            return
        
        cache_key = self._get_cache_key(context, prompt)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'context': {
                    'bucket_name': context.get('bucket_name'),
                    'anomaly_score': context.get('anomaly_score')
                },
                'explanation': explanation
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Cached explanation for key {cache_key}")
            
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")
    
    def clear(self):
        """Clear all cached explanations"""
        if not self.enabled or not os.path.exists(self.cache_dir):
            return
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not os.path.exists(self.cache_dir):
            return {'enabled': False}
        
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        total_size = sum(
            os.path.getsize(os.path.join(self.cache_dir, f)) 
            for f in cache_files
        )
        
        return {
            'enabled': True,
            'cached_items': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024)
        }
