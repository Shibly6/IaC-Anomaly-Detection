#!/usr/bin/env python3
"""
Custom Terraform Analyzer - Analyze arbitrary .tf files using pre-trained models
"""

import os
import pickle
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from src.feature_extraction.terraform_parser import parse_tf_file
from src.feature_extraction.feature_engineering import engineer_features_pipeline

logger = logging.getLogger("anomaly_detector.custom_analyzer")


class CustomTerraformAnalyzer:
    """
    Analyzes custom Terraform files using pre-trained anomaly detection models.
    """

    def __init__(self, models_dir: str = "data/output"):
        """
        Initialize the analyzer with pre-trained models.

        Args:
            models_dir: Directory containing trained models and features
        """
        self.models_dir = models_dir
        self.models = {}
        self.scaler = None
        self.feature_names = []
        self.loaded = False

    def load_models(self, model_names: Optional[List[str]] = None) -> bool:
        """
        Load pre-trained models and preprocessing artifacts.

        Args:
            model_names: List of model names to load. If None, loads all available.

        Returns:
            True if models loaded successfully, False otherwise
        """
        try:
            # Load scaler
            scaler_path = os.path.join(self.models_dir, "features", "scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("Loaded feature scaler")
            else:
                logger.warning(f"Scaler not found at {scaler_path}")
                return False

            # Load feature names
            feature_names_path = os.path.join(self.models_dir, "features", "feature_names.csv")
            if os.path.exists(feature_names_path):
                feature_df = pd.read_csv(feature_names_path)
                self.feature_names = feature_df['feature_name'].tolist()
                logger.info(f"Loaded {len(self.feature_names)} feature names")
            else:
                logger.warning(f"Feature names not found at {feature_names_path}")
                return False

            # Determine which models to load
            models_path = os.path.join(self.models_dir, "models")
            if not os.path.exists(models_path):
                logger.error(f"Models directory not found: {models_path}")
                return False

            available_models = {
                'isolation_forest': 'isolation_forest.pkl',
                'one_class_svm': 'one_class_svm.pkl',
                'autoencoder': 'autoencoder.pkl',
                'local_outlier_factor': 'local_outlier_factor.pkl'
            }

            if model_names is None:
                model_names = list(available_models.keys())

            # Load each model
            for model_name in model_names:
                if model_name not in available_models:
                    logger.warning(f"Unknown model: {model_name}")
                    continue

                model_file = available_models[model_name]
                model_path = os.path.join(models_path, model_file)

                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    logger.info(f"Loaded model: {model_name}")
                else:
                    logger.warning(f"Model file not found: {model_path}")

            if not self.models:
                logger.error("No models were loaded")
                return False

            self.loaded = True
            logger.info(f"Successfully loaded {len(self.models)} models")
            return True

        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False

    def extract_features_from_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Extract features from a single Terraform file.

        Args:
            file_path: Path to the .tf file

        Returns:
            DataFrame with extracted features, or None if extraction failed
        """
        try:
            # Parse the file
            bucket_features = parse_tf_file(file_path)

            if not bucket_features:
                logger.warning(f"No S3 bucket configurations found in {file_path}")
                return None

            # Convert to DataFrame
            features_df = pd.DataFrame(bucket_features)

            # Apply feature engineering
            from extract_features import create_strong_discriminative_features
            features_df = create_strong_discriminative_features(features_df)

            logger.info(f"Extracted features from {file_path}: {len(features_df)} configurations")
            return features_df

        except Exception as e:
            logger.error(f"Error extracting features from {file_path}: {str(e)}")
            return None

    def extract_features_from_directory(self, directory: str) -> Optional[pd.DataFrame]:
        """
        Extract features from all .tf files in a directory.

        Args:
            directory: Path to directory containing .tf files

        Returns:
            DataFrame with extracted features from all files
        """
        all_features = []

        # Find all .tf files
        tf_files = list(Path(directory).rglob("*.tf"))

        if not tf_files:
            logger.warning(f"No .tf files found in {directory}")
            return None

        logger.info(f"Found {len(tf_files)} Terraform files in {directory}")

        for tf_file in tf_files:
            features_df = self.extract_features_from_file(str(tf_file))
            if features_df is not None:
                all_features.append(features_df)

        if not all_features:
            logger.warning("No features extracted from any files")
            return None

        # Combine all features
        combined_df = pd.concat(all_features, ignore_index=True)
        logger.info(f"Extracted features from {len(all_features)} files: {len(combined_df)} total configurations")

        return combined_df

    def prepare_features(self, features_df: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Prepare features for model prediction (select and scale).

        Args:
            features_df: DataFrame with extracted features

        Returns:
            Scaled feature array ready for prediction
        """
        try:
            # Select only the features used during training
            available_features = [f for f in self.feature_names if f in features_df.columns]

            if len(available_features) != len(self.feature_names):
                missing = set(self.feature_names) - set(available_features)
                logger.warning(f"Missing features: {missing}")
                # Fill missing features with 0
                for feature in missing:
                    features_df[feature] = 0

            # Ensure correct order
            X = features_df[self.feature_names].values

            # Scale features
            X_scaled = self.scaler.transform(X)

            return X_scaled

        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            return None

    def predict_anomalies(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Run anomaly detection using all loaded models.

        Args:
            X: Scaled feature array

        Returns:
            Dictionary mapping model names to anomaly scores
        """
        predictions = {}

        for model_name, model in self.models.items():
            try:
                if model_name == 'autoencoder':
                    # Autoencoder uses reconstruction error
                    reconstructed = model.predict(X)
                    mse = np.mean(np.square(X - reconstructed), axis=1)
                    # Normalize to 0-1 range
                    scores = (mse - mse.min()) / (mse.max() - mse.min() + 1e-10)
                elif model_name == 'local_outlier_factor':
                    # LOF with novelty=True uses decision_function
                    # More negative scores = more anomalous
                    raw_scores = model.decision_function(X)
                    scores = -raw_scores  # Invert so higher = more anomalous
                    # Normalize to 0-1 range
                    scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
                else:
                    # Isolation Forest and One-Class SVM
                    scores = model.decision_function(X)
                    # Convert to anomaly scores (higher = more anomalous)
                    scores = -scores
                    # Normalize to 0-1 range
                    scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)

                predictions[model_name] = scores
                logger.info(f"Generated predictions using {model_name}")

            except Exception as e:
                logger.error(f"Error predicting with {model_name}: {str(e)}")

        return predictions

    def analyze(self, input_path: str) -> Optional[pd.DataFrame]:
        """
        Analyze Terraform file(s) and return results.

        Args:
            input_path: Path to .tf file or directory

        Returns:
            DataFrame with analysis results including anomaly scores
        """
        if not self.loaded:
            logger.error("Models not loaded. Call load_models() first.")
            return None

        # Extract features
        if os.path.isfile(input_path):
            features_df = self.extract_features_from_file(input_path)
        elif os.path.isdir(input_path):
            features_df = self.extract_features_from_directory(input_path)
        else:
            logger.error(f"Invalid path: {input_path}")
            return None

        if features_df is None or len(features_df) == 0:
            logger.error("No features extracted")
            return None

        # Prepare features for prediction
        X_scaled = self.prepare_features(features_df)
        if X_scaled is None:
            return None

        # Get predictions from all models
        predictions = self.predict_anomalies(X_scaled)

        # Add predictions to results DataFrame
        results_df = features_df.copy()

        for model_name, scores in predictions.items():
            results_df[f'{model_name}_score'] = scores

        # Calculate ensemble score (average of all models)
        if predictions:
            score_columns = [f'{model_name}_score' for model_name in predictions.keys()]
            results_df['ensemble_score'] = results_df[score_columns].mean(axis=1)

        # Add anomaly classification (threshold = 0.5)
        results_df['is_anomaly'] = (results_df['ensemble_score'] > 0.5).astype(int)

        logger.info(f"Analysis complete: {len(results_df)} configurations analyzed")
        anomaly_count = results_df['is_anomaly'].sum()
        logger.info(f"Detected {anomaly_count} potential anomalies")

        return results_df

    def get_summary(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a summary of analysis results.

        Args:
            results_df: DataFrame with analysis results

        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_configurations': len(results_df),
            'anomalies_detected': int(results_df['is_anomaly'].sum()),
            'anomaly_rate': float(results_df['is_anomaly'].mean()),
            'average_ensemble_score': float(results_df['ensemble_score'].mean()),
            'max_ensemble_score': float(results_df['ensemble_score'].max()),
            'models_used': list(self.models.keys()),
            'high_risk_configs': []
        }

        # Identify high-risk configurations (ensemble score > 0.7)
        high_risk = results_df[results_df['ensemble_score'] > 0.7]
        for _, row in high_risk.iterrows():
            summary['high_risk_configs'].append({
                'bucket_name': row.get('bucket_name', 'unknown'),
                'source_file': row.get('source_file', 'unknown'),
                'ensemble_score': float(row['ensemble_score']),
                'is_public_acl': int(row.get('is_public_acl', 0)),
                'has_public_policy': int(row.get('has_public_policy', 0))
            })

        return summary
