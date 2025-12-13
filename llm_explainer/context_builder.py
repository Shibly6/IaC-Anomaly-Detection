"""
Context Builder - Extract and format anomaly context for LLM prompts

This module extracts relevant information about detected anomalies
and formats it for use in LLM prompts.
"""

import pandas as pd
import numpy as np
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("anomaly_detector.llm_explainer")


class ContextBuilder:
    """Build context for anomaly explanations"""
    
    def __init__(self, output_dir: str = "data/output"):
        """
        Initialize context builder
        
        Args:
            output_dir: Directory containing anomaly detection outputs
        """
        self.output_dir = output_dir
        self.features_df = None
        self.predictions = {}
        self.scores = {}
        self.feature_names = []
        
        self._load_data()
    
    def _load_data(self):
        """Load all necessary data from output directory"""
        try:
            # Load raw features
            features_path = os.path.join(self.output_dir, "features", "raw_features.csv")
            if os.path.exists(features_path):
                self.features_df = pd.read_csv(features_path)
                logger.info(f"Loaded {len(self.features_df)} configurations from features")
            else:
                logger.warning(f"Features file not found: {features_path}")
                return
            
            # Load feature names
            feature_names_path = os.path.join(self.output_dir, "features", "feature_names.csv")
            if os.path.exists(feature_names_path):
                fn_df = pd.read_csv(feature_names_path)
                self.feature_names = fn_df['feature_name'].tolist()
            
            # Load model predictions and scores
            models_dir = os.path.join(self.output_dir, "models")
            if os.path.exists(models_dir):
                for model_name in ['isolation_forest', 'one_class_svm', 'autoencoder', 
                                   'local_outlier_factor', 'ensemble']:
                    pred_path = os.path.join(models_dir, f"{model_name}_predictions.npy")
                    score_path = os.path.join(models_dir, f"{model_name}_scores.npy")
                    
                    if os.path.exists(pred_path):
                        self.predictions[model_name] = np.load(pred_path)
                    if os.path.exists(score_path):
                        self.scores[model_name] = np.load(score_path)
                
                logger.info(f"Loaded predictions from {len(self.predictions)} models")
        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def get_anomalies(self, model_name: str = 'ensemble', min_score: float = 0.5) -> List[int]:
        """
        Get indices of anomalous configurations
        
        Args:
            model_name: Which model's predictions to use
            min_score: Minimum anomaly score threshold
            
        Returns:
            List of indices for anomalous configurations
        """
        if model_name not in self.predictions:
            # Fallback to first available model
            if self.predictions:
                model_name = list(self.predictions.keys())[0]
                logger.warning(f"Model '{model_name}' not found, using '{model_name}'")
            else:
                logger.error("No model predictions available")
                return []
        
        predictions = self.predictions[model_name]
        
        # If we have scores, use them for filtering
        if model_name in self.scores:
            scores = self.scores[model_name]
            anomaly_indices = np.where((predictions == 1) & (scores >= min_score))[0]
        else:
            anomaly_indices = np.where(predictions == 1)[0]
        
        return anomaly_indices.tolist()
    
    def build_context(self, index: int, model_name: str = 'ensemble') -> Dict[str, Any]:
        """
        Build context dictionary for a specific anomaly
        
        Args:
            index: Index of the anomaly in the dataset
            model_name: Which model's scores to include
            
        Returns:
            Dictionary with all relevant context
        """
        if self.features_df is None or index >= len(self.features_df):
            logger.error(f"Invalid index {index}")
            return {}
        
        row = self.features_df.iloc[index]
        
        # Build base context from features
        context = {
            'bucket_name': row.get('bucket_name', 'unknown'),
            'source_file': row.get('source_file', 'unknown'),
            'acl': row.get('acl', 'unknown')
        }
        
        # Add key security features
        security_features = [
            'is_public_acl', 'has_public_policy', 'versioning_enabled',
            'logging_enabled', 'encryption_enabled', 'secure_transport',
            'cors_enabled', 'website_enabled', 'public_access_blocks'
        ]
        
        for feature in security_features:
            if feature in row:
                context[feature] = row[feature]
        
        # Add discriminative features if available
        discriminative_features = [
            'main_discriminator', 'security_level', 'public_access_score',
            'risk_multiplier', 'anomaly_signal'
        ]
        
        for feature in discriminative_features:
            if feature in row:
                context[feature] = row[feature]
        
        # Add anomaly score from specified model
        if model_name in self.scores and index < len(self.scores[model_name]):
            context['anomaly_score'] = float(self.scores[model_name][index])
        else:
            context['anomaly_score'] = 0.5
        
        # Add scores from all models for comparison
        context['model_scores'] = {}
        for m_name, scores in self.scores.items():
            if index < len(scores):
                context['model_scores'][m_name] = float(scores[index])
        
        # Add severity assessment
        context['severity'] = self._assess_severity(context['anomaly_score'])
        
        return context
    
    def _assess_severity(self, score: float) -> str:
        """Assess severity based on anomaly score"""
        if score >= 0.9:
            return "CRITICAL"
        elif score >= 0.7:
            return "HIGH"
        elif score >= 0.5:
            return "MEDIUM"
        elif score >= 0.3:
            return "LOW"
        else:
            return "INFO"
    
    def get_terraform_code(self, index: int) -> Optional[str]:
        """
        Try to retrieve original Terraform code for the configuration
        
        Args:
            index: Index of the configuration
            
        Returns:
            Terraform code string or None
        """
        if self.features_df is None or index >= len(self.features_df):
            return None
        
        row = self.features_df.iloc[index]
        source_file = row.get('source_file', '')
        
        if not source_file or source_file == 'unknown':
            return None
        
        # Try to find and read the source file
        terraform_dir = "data/terraform"
        possible_paths = [
            source_file,
            os.path.join(terraform_dir, source_file),
            os.path.join(terraform_dir, "correct", source_file),
            os.path.join(terraform_dir, "misconfig", source_file)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        return f.read()
                except Exception as e:
                    logger.warning(f"Could not read {path}: {e}")
        
        return None
    
    def get_batch_context(
        self, 
        indices: List[int], 
        model_name: str = 'ensemble'
    ) -> List[Dict[str, Any]]:
        """
        Build context for multiple anomalies
        
        Args:
            indices: List of anomaly indices
            model_name: Which model's scores to use
            
        Returns:
            List of context dictionaries
        """
        contexts = []
        for idx in indices:
            context = self.build_context(idx, model_name)
            if context:
                contexts.append(context)
        
        return contexts
    
    def get_summary_stats(self, indices: List[int]) -> Dict[str, Any]:
        """
        Get summary statistics for a set of anomalies
        
        Args:
            indices: List of anomaly indices
            
        Returns:
            Dictionary with summary statistics
        """
        if not indices:
            return {}
        
        contexts = self.get_batch_context(indices)
        
        # Count by severity
        severity_counts = {}
        for ctx in contexts:
            sev = ctx.get('severity', 'UNKNOWN')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        # Count public access issues
        public_count = sum(1 for ctx in contexts 
                          if ctx.get('is_public_acl', 0) or ctx.get('has_public_policy', 0))
        
        # Count missing security features
        missing_encryption = sum(1 for ctx in contexts if not ctx.get('encryption_enabled', 0))
        missing_versioning = sum(1 for ctx in contexts if not ctx.get('versioning_enabled', 0))
        missing_logging = sum(1 for ctx in contexts if not ctx.get('logging_enabled', 0))
        
        # Average anomaly score
        avg_score = np.mean([ctx.get('anomaly_score', 0) for ctx in contexts])
        
        return {
            'total_anomalies': len(indices),
            'severity_distribution': severity_counts,
            'public_access_issues': public_count,
            'missing_encryption': missing_encryption,
            'missing_versioning': missing_versioning,
            'missing_logging': missing_logging,
            'average_anomaly_score': float(avg_score)
        }


if __name__ == "__main__":
    # Test the context builder
    logging.basicConfig(level=logging.INFO)
    
    builder = ContextBuilder()
    anomalies = builder.get_anomalies()
    
    print(f"Found {len(anomalies)} anomalies")
    
    if anomalies:
        # Show first anomaly context
        context = builder.build_context(anomalies[0])
        print(f"\nFirst anomaly context:")
        for key, value in context.items():
            print(f"  {key}: {value}")
        
        # Show summary stats
        stats = builder.get_summary_stats(anomalies)
        print(f"\nSummary statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
