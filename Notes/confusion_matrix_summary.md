# Confusion Matrix Summary for Test Set

This table summarizes the performance of different models on the test set based on their confusion matrix values.

| Model                  | True Negatives (TN) | True Positives (TP) | False Positives (FP) | False Negatives (FN) | Interpretation                                                                      |
|------------------------|---------------------|---------------------|----------------------|----------------------|-------------------------------------------------------------------------------------|
| **autoencoder**        | 16                  | 10                  | 2                    | 2                    | A balanced performance with an equal, low number of false positives and negatives.    |
| **isolation_forest**   | 17                  | 11                  | 1                    | 1                    | The best performing model in this set, with the lowest overall error count.         |
| **local_outlier_factor** | 15                  | 3                   | 3                    | 9                    | Struggles to identify true positives, resulting in a high number of false negatives. |
| **one_class_svm**      | 17                  | 9                   | 1                    | 3                    | Strong at identifying true negatives, but misses some positive cases.               |
| **ensemble**           | 17                  | 10                  | 1                    | 2                    | A strong performer with very few errors, close to the best model.                   |

**Note on Interpretation:**
*   **True Negatives (TN):** Correctly identified non-anomalies.
*   **True Positives (TP):** Correctly identified anomalies.
*   **False Positives (FP):** Non-anomalies incorrectly flagged as anomalies (Type I Error).
*   **False Negatives (FN):** Anomalies that were missed (Type II Error).
