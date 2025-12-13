
import numpy as np
import sys
import os
# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from utils.evaluation import evaluate_anomaly_detector

def generate_confusion_matrix_data():
    """
    Loads test data and model predictions, and prints confusion matrix values.
    """
    try:
        y_true = np.load('data/output/features/y_test.npy', allow_pickle=True)
    except FileNotFoundError:
        print("Error: y_test.npy not found. Please run the feature extraction first.", file=sys.stderr)
        sys.exit(1)

    models = [
        "autoencoder",
        "isolation_forest",
        "local_outlier_factor",
        "one_class_svm",
        "ensemble"
    ]

    print("Model,TN,TP,FP,FN")

    for model_name in models:
        try:
            predictions_path = f'data/output/models/{model_name}_predictions.npy'
            anomaly_predictions = np.load(predictions_path, allow_pickle=True)
            
            # We need anomaly_scores to run the evaluation function. 
            # Since we are passing predictions directly, we can pass an empty array for scores.
            dummy_scores = np.zeros_like(y_true)

            results = evaluate_anomaly_detector(
                y_true=y_true,
                anomaly_scores=dummy_scores,
                anomaly_predictions=anomaly_predictions,
                model_name=model_name
            )

            if results:
                tn = results.get('true_negatives', 'N/A')
                tp = results.get('true_positives', 'N/A')
                fp = results.get('false_positives', 'N/A')
                fn = results.get('false_negatives', 'N/A')
                print(f"{model_name},{tn},{tp},{fp},{fn}")

        except FileNotFoundError:
            print(f"Warning: {model_name}_predictions.npy not found. Skipping model.", file=sys.stderr)
        except Exception as e:
            print(f"Error processing {model_name}: {e}", file=sys.stderr)

if __name__ == "__main__":
    generate_confusion_matrix_data()
