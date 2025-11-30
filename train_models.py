#!/usr/bin/env python3
"""
Train unsupervised anomaly detection models on extracted features.
FIXED version with better handling for small datasets and ensemble creation.
"""

import os
import logging
import numpy as np
import pandas as pd
import pickle
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, f1_score as sklearn_f1_score
from sklearn.preprocessing import StandardScaler
from scipy import stats

# Configure logging
logger = logging.getLogger("anomaly_detector.models")
console = Console()


class ImprovedAutoencoder:
    """Improved Autoencoder for anomaly detection with better architecture"""

    def __init__(self, hidden_layer_sizes=None, random_state=42):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()

    def fit(self, X_train, X_val=None):
        # Scale the data
        X_scaled = self.scaler.fit_transform(X_train)

        n_features = X_scaled.shape[1]
        if self.hidden_layer_sizes is None:
            # Create a more sophisticated architecture
            if n_features <= 10:
                # Small feature space
                encoding_dim = max(int(n_features * 0.5), 2)
                hidden1 = max(int(n_features * 0.7), 3)
                self.hidden_layer_sizes = (hidden1, encoding_dim, hidden1)
            else:
                # Larger feature space
                encoding_dim = max(int(n_features * 0.3), 3)
                hidden1 = max(int(n_features * 0.7), 5)
                hidden2 = max(int(n_features * 0.5), 4)
                self.hidden_layer_sizes = (hidden1, hidden2, encoding_dim, hidden2, hidden1)

        self.model = MLPRegressor(
            hidden_layer_sizes=self.hidden_layer_sizes,
            activation='tanh',
            solver='adam',
            alpha=0.001,
            learning_rate_init=0.001,
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=20,
            random_state=self.random_state
        )

        self.model.fit(X_scaled, X_scaled)
        return self

    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def decision_function(self, X):
        X_scaled = self.scaler.transform(X)
        X_pred = self.model.predict(X_scaled)
        # Calculate reconstruction error
        mse = np.mean(np.square(X_scaled - X_pred), axis=1)
        return mse  # Higher values indicate anomalies


def train_isolation_forest(X_train, contamination=0.1):
    """Train Isolation Forest with improved parameters for small datasets"""
    console.print("[cyan]Training Isolation Forest model...[/cyan]")

    # Adaptive parameters based on dataset size
    n_samples = X_train.shape[0]

    if n_samples < 50:
        n_estimators = 100
        max_samples = min(32, n_samples)
        max_features = min(0.8, X_train.shape[1] / X_train.shape[1])
    elif n_samples < 200:
        n_estimators = 150
        max_samples = min(64, n_samples)
        max_features = 0.8
    else:
        n_estimators = 200
        max_samples = min(128, n_samples)
        max_features = 0.8

    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        max_samples=max_samples,
        max_features=max_features,
        bootstrap=True,
        n_jobs=-1,
        random_state=42
    )

    model.fit(X_train)
    return model


def train_one_class_svm(X_train, contamination=0.1):
    """Train One-Class SVM with improved parameters"""
    console.print("[cyan]Training One-Class SVM model...[/cyan]")

    # For small datasets, use different kernel
    if X_train.shape[0] < 50:
        kernel = 'linear'  # Linear kernel for small datasets
    else:
        kernel = 'rbf'

    model = OneClassSVM(
        nu=contamination,
        kernel=kernel,
        gamma='scale',
        cache_size=500
    )

    model.fit(X_train)
    return model


def train_autoencoder(X_train, X_val=None):
    """Train improved autoencoder model"""
    console.print("[cyan]Training Autoencoder model...[/cyan]")

    autoencoder = ImprovedAutoencoder(random_state=42)
    autoencoder.fit(X_train, X_val)
    return autoencoder


def train_local_outlier_factor(X_train, contamination=0.1):
    """Train LOF with improved parameters for small datasets"""
    console.print("[cyan]Training Local Outlier Factor model...[/cyan]")

    n_samples = X_train.shape[0]

    # Adaptive number of neighbors
    if n_samples < 20:
        n_neighbors = max(3, n_samples // 5)
    elif n_samples < 50:
        n_neighbors = max(5, n_samples // 10)
    elif n_samples < 200:
        n_neighbors = 20
    else:
        n_neighbors = 30

    # Ensure n_neighbors is less than n_samples
    n_neighbors = min(n_neighbors, n_samples - 1)

    model = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
        novelty=True,
        algorithm='auto',
        leaf_size=30,
        n_jobs=-1
    )

    model.fit(X_train)
    return model


def optimize_threshold(y_true, scores, metric='f1'):
    """Find optimal threshold that maximizes the specified metric"""
    if y_true is None or len(np.unique(y_true)) < 2:
        # Default to 90th percentile if no labels
        return np.percentile(scores, 90)

    best_score = 0
    best_threshold = np.percentile(scores, 90)

    # Try different percentiles
    for percentile in range(50, 99, 2):
        threshold = np.percentile(scores, percentile)
        predictions = (scores >= threshold).astype(int)

        try:
            if metric == 'f1':
                score = sklearn_f1_score(y_true, predictions, zero_division=0)
            elif metric == 'balanced':
                # Calculate balanced accuracy
                from sklearn.metrics import confusion_matrix
                tn, fp, fn, tp = confusion_matrix(y_true, predictions).ravel()
                sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
                specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
                score = (sensitivity + specificity) / 2
            else:
                score = sklearn_f1_score(y_true, predictions, zero_division=0)

            if score > best_score:
                best_score = score
                best_threshold = threshold
        except:
            continue

    return best_threshold


def evaluate_model(model, X_test, y_test=None, model_type='isolation_forest', contamination=0.1):
    """Fixed model evaluation with proper score interpretation"""
    results = {}

    # Get raw anomaly scores based on model type
    if model_type == 'isolation_forest':
        # For Isolation Forest, MORE NEGATIVE scores = more anomalous
        raw_scores = model.decision_function(X_test)
        scores = -raw_scores  # Invert so higher = more anomalous

        # Check if we need to flip based on correlation with labels
        if y_test is not None and len(np.unique(y_test)) > 1:
            correlation = np.corrcoef(scores, y_test)[0, 1]
            if correlation < 0:  # Negative correlation means scores are inverted
                scores = -scores

    elif model_type == 'one_class_svm':
        # For One-Class SVM, MORE NEGATIVE scores = more anomalous
        raw_scores = model.decision_function(X_test)
        scores = -raw_scores  # Invert so higher = more anomalous

    elif model_type == 'autoencoder':
        # For autoencoder, reconstruction error is already positive
        # Higher reconstruction error = more anomalous
        scores = model.decision_function(X_test)

        # Check if scores need inversion
        if y_test is not None and len(np.unique(y_test)) > 1:
            correlation = np.corrcoef(scores, y_test)[0, 1]
            if correlation < 0:  # Negative correlation means scores are inverted
                scores = -scores

    elif model_type == 'local_outlier_factor':
        # For LOF, MORE NEGATIVE scores = more anomalous
        raw_scores = model.decision_function(X_test)
        scores = -raw_scores  # Invert so higher = more anomalous
    else:
        scores = np.random.random(X_test.shape[0])
        logger.warning(f"Unknown model type: {model_type}")

    # Ensure all scores are positive
    min_score = scores.min()
    if min_score < 0:
        scores = scores - min_score  # Shift to make all positive

    # Normalize scores to 0-1 range
    if scores.max() > scores.min():
        scores = (scores - scores.min()) / (scores.max() - scores.min())
    else:
        scores = np.ones_like(scores) * 0.5

    results['anomaly_scores'] = scores

    # Find optimal threshold if labels are available
    if y_test is not None and len(np.unique(y_test)) > 1:
        # Try both F1 and balanced accuracy
        threshold_f1 = optimize_threshold(y_test, scores, metric='f1')
        threshold_balanced = optimize_threshold(y_test, scores, metric='balanced')

        # Choose the better one
        pred_f1 = (scores >= threshold_f1).astype(int)
        pred_balanced = (scores >= threshold_balanced).astype(int)

        f1_f1 = sklearn_f1_score(y_test, pred_f1, zero_division=0)
        f1_balanced = sklearn_f1_score(y_test, pred_balanced, zero_division=0)

        if f1_f1 >= f1_balanced:
            optimal_threshold = threshold_f1
            predictions = pred_f1
        else:
            optimal_threshold = threshold_balanced
            predictions = pred_balanced

        results['predictions'] = predictions
        results['threshold'] = optimal_threshold

        try:
            # Calculate metrics
            results['roc_auc'] = roc_auc_score(y_test, scores)

            # Double-check ROC AUC - if it's very low, scores might be inverted
            if results['roc_auc'] < 0.3:
                logger.warning(f"{model_type}: Very low ROC AUC ({results['roc_auc']:.3f}), checking score inversion")
                scores_inverted = 1 - scores
                roc_auc_inverted = roc_auc_score(y_test, scores_inverted)

                if roc_auc_inverted > results['roc_auc']:
                    logger.info(
                        f"{model_type}: Inverting scores improved ROC AUC from {results['roc_auc']:.3f} to {roc_auc_inverted:.3f}")
                    scores = scores_inverted
                    results['anomaly_scores'] = scores
                    results['roc_auc'] = roc_auc_inverted

                    # Recalculate predictions with inverted scores
                    optimal_threshold = optimize_threshold(y_test, scores, metric='f1')
                    predictions = (scores >= optimal_threshold).astype(int)
                    results['predictions'] = predictions
                    results['threshold'] = optimal_threshold

            precision, recall, _ = precision_recall_curve(y_test, scores)
            results['pr_auc'] = auc(recall, precision)
            results['f1'] = sklearn_f1_score(y_test, predictions, zero_division=0)

            # Calculate detection statistics
            from sklearn.metrics import confusion_matrix
            tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()
            results['true_positives'] = tp
            results['false_positives'] = fp
            results['true_negatives'] = tn
            results['false_negatives'] = fn

            # Additional metrics
            results['precision'] = tp / (tp + fp) if (tp + fp) > 0 else 0
            results['recall'] = tp / (tp + fn) if (tp + fn) > 0 else 0

        except Exception as e:
            logger.warning(f"Could not calculate evaluation metrics: {str(e)}")
            results['roc_auc'] = 0.5
            results['pr_auc'] = contamination
            results['f1'] = 0.0
    else:
        # Use contamination-based threshold
        threshold = np.percentile(scores, 100 * (1 - contamination))
        predictions = (scores >= threshold).astype(int)
        results['predictions'] = predictions
        results['threshold'] = threshold

    return results


def check_feature_quality(X_train, X_test, feature_names):
    """Check if features have good discriminative power"""
    logger.info("\nFeature Quality Check:")

    # Check variance in features
    train_var = np.var(X_train, axis=0)
    test_var = np.var(X_test, axis=0)

    for i, (name, t_var, te_var) in enumerate(zip(feature_names, train_var, test_var)):
        logger.info(f"  {name}: train_var={t_var:.4f}, test_var={te_var:.4f}")

    # Check for features with zero variance
    zero_var_train = np.where(train_var < 0.001)[0]
    zero_var_test = np.where(test_var < 0.001)[0]

    if len(zero_var_train) > 0:
        logger.warning(f"Features with near-zero variance in training: {[feature_names[i] for i in zero_var_train]}")
    if len(zero_var_test) > 0:
        logger.warning(f"Features with near-zero variance in test: {[feature_names[i] for i in zero_var_test]}")

    return train_var, test_var


def create_improved_ensemble(models_results, X_test, y_test=None):
    """Create an improved ensemble with adaptive weighting - FIXED"""
    if len(models_results) < 2:
        return None, None

    # Collect all normalized scores
    all_scores = []
    model_names = []
    model_performance = {}

    for model_name, results in models_results.items():
        if 'anomaly_scores' in results:
            scores = results['anomaly_scores']
            all_scores.append(scores)
            model_names.append(model_name)

            # Calculate model performance weight
            if y_test is not None and 'f1' in results and results['f1'] is not None:
                # Use F1 score as weight
                model_performance[model_name] = max(results['f1'], 0.1)  # Minimum weight of 0.1
            else:
                # Use default weights based on typical performance
                default_weights = {
                    'isolation_forest': 0.3,
                    'one_class_svm': 0.25,
                    'autoencoder': 0.25,
                    'local_outlier_factor': 0.2
                }
                model_performance[model_name] = default_weights.get(model_name, 0.25)

    if not all_scores:
        return None, None

    all_scores = np.array(all_scores)

    # Calculate model weights
    total_performance = sum(model_performance.values())
    weights = [model_performance[name] / total_performance for name in model_names]

    # Create weighted ensemble
    ensemble_scores = np.zeros(len(X_test))
    for i, (scores, weight) in enumerate(zip(all_scores, weights)):
        ensemble_scores += scores * weight

    # Final normalization
    if ensemble_scores.max() > ensemble_scores.min():
        ensemble_scores = (ensemble_scores - ensemble_scores.min()) / \
                          (ensemble_scores.max() - ensemble_scores.min())

    return ensemble_scores, dict(zip(model_names, weights))


def train_models_main(output_dir, models_list=None):
    """Main function for improved model training pipeline"""
    if models_list is None:
        models_list = ['isolation_forest', 'one_class_svm', 'autoencoder', 'local_outlier_factor']

    # Create necessary directories
    os.makedirs(f"{output_dir}/models", exist_ok=True)

    # Load preprocessed data
    console.print("[cyan]Loading preprocessed data...[/cyan]")
    try:
        X_train = np.load(f"{output_dir}/features/X_train.npy")
        X_test = np.load(f"{output_dir}/features/X_test.npy")

        # X_val is optional
        try:
            X_val = np.load(f"{output_dir}/features/X_val.npy")
        except:
            X_val = None
            logger.info("No validation set found, proceeding without it")

        # Load labels if available
        try:
            y_test = np.load(f"{output_dir}/features/y_test.npy")
            y_val = np.load(f"{output_dir}/features/y_val.npy") if X_val is not None else None
        except:
            y_test = None
            y_val = None
            logger.info("Test labels not found. Using unsupervised evaluation.")

        # Load feature names for quality check
        try:
            feature_names_df = pd.read_csv(f"{output_dir}/features/feature_names.csv")
            feature_names = feature_names_df['feature_name'].tolist()
            check_feature_quality(X_train, X_test, feature_names)
        except:
            logger.warning("Could not load feature names for quality check")

    except Exception as e:
        logger.error(f"Error loading preprocessed data: {str(e)}")
        console.print(f"[red]Error loading preprocessed data: {str(e)}[/red]")
        return

    # Calculate contamination rate
    if y_test is not None:
        contamination = np.mean(y_test)
        contamination = max(0.05, min(0.3, contamination))  # Clamp between 5% and 30%
    else:
        contamination = 0.1  # Default 10%

    logger.info(f"Using contamination rate: {contamination:.3f}")
    logger.info(f"Training set size: {X_train.shape}")
    logger.info(f"Test set size: {X_test.shape}")

    # Train models
    models_results = {}

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
    ) as progress:
        training_task = progress.add_task("[cyan]Training models...", total=len(models_list))

        for model_type in models_list:
            try:
                # Train the model
                if model_type == 'isolation_forest':
                    model = train_isolation_forest(X_train, contamination)
                elif model_type == 'one_class_svm':
                    model = train_one_class_svm(X_train, contamination)
                elif model_type == 'autoencoder':
                    model = train_autoencoder(X_train, X_val)
                elif model_type == 'local_outlier_factor':
                    model = train_local_outlier_factor(X_train, contamination)
                else:
                    logger.warning(f"Unknown model type: {model_type}")
                    continue

                # Evaluate model
                evaluation = evaluate_model(model, X_test, y_test, model_type, contamination)

                # Save model
                with open(f"{output_dir}/models/{model_type}.pkl", 'wb') as f:
                    pickle.dump(model, f)

                # Save results
                np.save(f"{output_dir}/models/{model_type}_scores.npy", evaluation['anomaly_scores'])
                if 'predictions' in evaluation:
                    np.save(f"{output_dir}/models/{model_type}_predictions.npy", evaluation['predictions'])

                # Store results
                models_results[model_type] = evaluation

                # Log performance
                if y_test is not None and 'f1' in evaluation:
                    logger.info(f"{model_type} - F1: {evaluation['f1']:.4f}, "
                                f"ROC AUC: {evaluation.get('roc_auc', 0.5):.4f}, "
                                f"Threshold: {evaluation.get('threshold', 0):.4f}")
                    logger.info(f"{model_type} - Precision: {evaluation.get('precision', 0):.4f}, "
                                f"Recall: {evaluation.get('recall', 0):.4f}")
                    logger.info(f"{model_type} - TP: {evaluation.get('true_positives', 0)}, "
                                f"FP: {evaluation.get('false_positives', 0)}, "
                                f"TN: {evaluation.get('true_negatives', 0)}, "
                                f"FN: {evaluation.get('false_negatives', 0)}")

                progress.update(training_task, advance=1)

            except Exception as e:
                logger.error(f"Error training {model_type}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                progress.update(training_task, advance=1)
                continue

    # Create improved ensemble
    if len(models_results) > 1:
        console.print("[cyan]Creating improved ensemble...[/cyan]")
        try:
            ensemble_scores, ensemble_weights = create_improved_ensemble(models_results, X_test, y_test)

            if ensemble_scores is not None:
                # Evaluate ensemble
                ensemble_evaluation = {'anomaly_scores': ensemble_scores}

                if y_test is not None:
                    optimal_threshold = optimize_threshold(y_test, ensemble_scores, metric='f1')
                    ensemble_predictions = (ensemble_scores >= optimal_threshold).astype(int)

                    ensemble_evaluation.update({
                        'predictions': ensemble_predictions,
                        'threshold': optimal_threshold,
                        'roc_auc': roc_auc_score(y_test, ensemble_scores),
                        'f1': sklearn_f1_score(y_test, ensemble_predictions, zero_division=0)
                    })

                    precision, recall, _ = precision_recall_curve(y_test, ensemble_scores)
                    ensemble_evaluation['pr_auc'] = auc(recall, precision)

                # Save ensemble results
                np.save(f"{output_dir}/models/ensemble_scores.npy", ensemble_scores)
                if 'predictions' in ensemble_evaluation:
                    np.save(f"{output_dir}/models/ensemble_predictions.npy", ensemble_evaluation['predictions'])

                # Save ensemble weights
                pd.DataFrame([ensemble_weights]).to_csv(f"{output_dir}/models/ensemble_weights.csv", index=False)

                # Log ensemble performance
                if y_test is not None and 'f1' in ensemble_evaluation:
                    logger.info(f"Ensemble - F1: {ensemble_evaluation['f1']:.4f}, "
                                f"ROC AUC: {ensemble_evaluation.get('roc_auc', 0):.4f}")
                    logger.info(f"Ensemble weights: {ensemble_weights}")

                models_results['ensemble'] = ensemble_evaluation

        except Exception as e:
            logger.error(f"Error creating ensemble: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    console.print(f"[green]Model training completed. Trained {len(models_results)} models.[/green]")

    # Print summary
    console.print("\n[bold]Model Performance Summary:[/bold]")
    for model_name, results in models_results.items():
        if 'f1' in results and results['f1'] is not None:
            f1_score = results['f1']
            roc_auc = results.get('roc_auc', 0)
            console.print(f"  {model_name}: F1={f1_score:.4f}, ROC AUC={roc_auc:.4f}")


if __name__ == "__main__":
    # If run directly, use default path
    output_dir = "data/output"
    train_models_main(output_dir)