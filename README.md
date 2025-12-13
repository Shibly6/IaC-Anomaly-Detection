# IaC Anomaly Detection

> **Detecting Cloud Misconfigurations Using Unsupervised Machine Learning**

A comprehensive anomaly detection system for Infrastructure as Code (IaC) scripts, specifically designed to identify security misconfigurations in AWS S3 bucket Terraform configurations using unsupervised learning techniques.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0%2B-orange.svg)](https://scikit-learn.org/)

## 🎯 Overview

This project implements a machine learning pipeline that automatically detects anomalies and security misconfigurations in Terraform IaC scripts. It uses multiple unsupervised learning algorithms to identify potentially risky configurations such as public S3 buckets, missing encryption, disabled logging, and other security vulnerabilities.

### Key Features

- **🔍 Multi-Model Approach**: Implements 4 different anomaly detection algorithms
  - Isolation Forest
  - One-Class SVM
  - Autoencoder (Neural Network)
  - Local Outlier Factor (LOF)
- **🎨 Rich Visualizations**: Generates comprehensive plots and analysis charts
- **🔧 Automated Feature Engineering**: Extracts and engineers discriminative features from Terraform files
- **📊 Ensemble Learning**: Combines multiple models for improved detection accuracy
- **🚀 Easy to Use**: Simple command-line interface with sensible defaults
- **📈 Synthetic Data Generation**: Can generate training data when real configurations are limited

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IaC Anomaly Detection Pipeline            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   Phase 1: Feature Extraction           │
        │   • Parse Terraform files (.tf)         │
        │   • Extract S3 bucket configurations    │
        │   • Engineer discriminative features    │
        │   • Generate synthetic data (optional)  │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   Phase 2: Model Training               │
        │   • Train multiple ML models            │
        │   • Optimize thresholds                 │
        │   • Create ensemble model               │
        │   • Evaluate performance                │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   Phase 3: Visualization                │
        │   • Feature distributions               │
        │   • PCA & t-SNE plots                   │
        │   • ROC & PR curves                     │
        │   • Model comparisons                   │
        └─────────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.10 (recommended for full compatibility)
- pip package manager

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone -b stable-v1 https://github.com/Shibly6/IaC-Anomaly-Detection.git
   cd IaC-Anomaly-Detection
   ```

2. **Create and activate a Python 3.10 virtual environment**

> ⚠️ **Requirement Note:** Make sure Python 3.10.x is installed and that it is added to your system **PATH**.

   **Windows (PowerShell):**
   ```powershell
   py -3.10 -m venv venv_p310
   .\venv_p310\Scripts\Activate.ps1
   ```

   **Linux/macOS:**
   ```bash
   python3.10 -m venv venv_p310
   source venv_p310/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   > **Note**: All libraries are tested and compatible with Python 3.10.

## 💻 Usage

### Basic Usage

Run the complete pipeline with default settings:

```bash
python main.py
```

This will:
1. Parse Terraform files from `data/terraform/`
2. Extract and engineer features
3. Train all 4 anomaly detection models
4. Generate visualizations in `data/output/plots/`

### Advanced Usage

#### Skip Specific Phases

```bash
# Skip feature extraction (use existing features)
python main.py --skip-extraction

# Skip model training
python main.py --skip-training

# Skip visualization generation
python main.py --skip-visualization
```

#### Train Specific Models

```bash
# Train only Isolation Forest and Autoencoder
python main.py --models isolation_forest,autoencoder

# Train only One-Class SVM
python main.py --models one_class_svm
```

#### Custom Directories

```bash
# Use custom input/output directories
python main.py --terraform-dir /path/to/terraform --output-dir /path/to/output
```

#### Fix Data Issues

```bash
# Run NaN fix before starting the pipeline
python main.py --fix-nan
```

#### Verbose Logging

```bash
# Enable detailed logging
python main.py --verbose
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--terraform-dir` | Directory containing Terraform files | `data/terraform` |
| `--output-dir` | Directory to store output files | `data/output` |
| `--skip-extraction` | Skip feature extraction phase | `False` |
| `--skip-training` | Skip model training phase | `False` |
| `--skip-visualization` | Skip visualization generation phase | `False` |
| `--models` | Comma-separated list of models to train | All models |
| `--fix-nan` | Run NaN fix before starting the pipeline | `False` |
| `--verbose`, `-v` | Enable verbose logging | `False` |

## 📁 Project Structure

```
iac-anomaly-detection_v.1/
├── main.py                          # Main orchestration script
├── extract_features.py              # Feature extraction pipeline
├── train_models.py                  # Model training pipeline
├── generate_visualizations.py       # Visualization generation
├── fix_nan_data.py                  # Data cleaning utility
├── requirements.txt                 # Python dependencies
├── anomaly_detection.log           # Application logs
│
├── src/                            # Source code modules
│   ├── feature_extraction/
│   │   ├── terraform_parser.py     # Parse Terraform files
│   │   ├── feature_engineering.py  # Engineer features
│   │   └── synthetic_data.py       # Generate synthetic data
│   │
│   ├── models/
│   │   ├── isolation_forest.py     # Isolation Forest model
│   │   ├── one_class_svm.py        # One-Class SVM model
│   │   ├── autoencoder.py          # Autoencoder model
│   │   └── local_outlier_factor.py # LOF model (placeholder)
│   │
│   ├── utils/
│   │   ├── data_preprocessing.py   # Data preprocessing utilities
│   │   └── evaluation.py           # Model evaluation metrics
│   │
│   └── visualization/
│       ├── feature_visualizer.py   # Feature visualization
│       ├── anomaly_visualizer.py   # Anomaly visualization
│       ├── plotly_visualizer.py    # Interactive plots
│       └── marker_utils.py         # Visualization utilities
│
└── data/
    ├── terraform/                  # Input Terraform files
    │   ├── correct/               # Correct configurations
    │   └── misconfig/             # Misconfigured examples
    │
    └── output/                    # Generated outputs
        ├── features/              # Extracted features
        ├── models/                # Trained models
        └── plots/                 # Visualizations
            ├── features/
            ├── anomaly_scores/
            ├── anomaly_detection/
            ├── dimension_reduction/
            └── model_comparison/
```

## 🔍 Detected Anomalies

The system detects various security misconfigurations including:

### High-Risk Configurations
- ✅ Public ACL settings (`public-read`, `public-read-write`)
- ✅ Public bucket policies
- ✅ Missing public access blocks
- ✅ Disabled encryption
- ✅ Disabled versioning
- ✅ Disabled logging

### Security Features
- ✅ Secure transport enforcement
- ✅ CORS configuration
- ✅ Website hosting settings
- ✅ Replication configuration
- ✅ Object lock settings
- ✅ Lifecycle policies

## 📊 Output Files

After running the pipeline, you'll find:

### Features (`data/output/features/`)
- `raw_features.csv` - Extracted features with metadata
- `X_train.npy`, `X_test.npy`, `X_val.npy` - Processed datasets
- `y_test.npy`, `y_val.npy` - Labels (if available)
- `feature_names.csv` - List of feature names
- `scaler.pkl` - Fitted scaler for preprocessing

### Models (`data/output/models/`)
- `{model_name}.pkl` - Trained model files
- `{model_name}_scores.npy` - Anomaly scores
- `{model_name}_predictions.npy` - Binary predictions
- `ensemble_scores.npy` - Ensemble model scores
- `ensemble_weights.csv` - Model weights in ensemble

### Visualizations (`data/output/plots/`)
- **Feature Analysis**: Distribution plots, correlation matrices
- **Dimensionality Reduction**: PCA and t-SNE visualizations
- **Model Performance**: ROC curves, Precision-Recall curves
- **Anomaly Detection**: Detected anomalies in 2D space
- **Model Comparison**: Side-by-side model comparisons

## 🧪 Example Terraform Files

### Correct Configuration
```hcl
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.secure_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.secure_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

### Misconfiguration (Detected as Anomaly)
```hcl
resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-bucket"
  acl    = "public-read"  # ⚠️ Public access!
}

# ⚠️ No encryption
# ⚠️ No versioning
# ⚠️ No logging
```

## 🎨 Visualization Examples

The system generates various visualizations to help understand the data and model performance:

- **Feature Distributions**: Histograms showing the distribution of security features
- **PCA Plots**: 2D visualization of high-dimensional feature space
- **ROC Curves**: Model performance comparison
- **Anomaly Detection**: Visual identification of detected anomalies
- **Model Comparison**: Side-by-side comparison of all models

## 🔧 Customization

### Adding Custom Features

Edit `src/feature_extraction/feature_engineering.py` to add custom features:

```python
def create_custom_feature(df):
    # Your custom feature logic
    df['custom_feature'] = ...
    return df
```

### Adding New Models

1. Create a new model file in `src/models/`
2. Implement the model training function
3. Add the model to `train_models.py`

### Adjusting Contamination Rate

The contamination rate (expected proportion of anomalies) can be adjusted in the code:

```python
# In train_models.py
contamination = 0.1  # 10% expected anomalies
```

## 📈 Performance Metrics

The system evaluates models using:

- **ROC AUC**: Area Under the Receiver Operating Characteristic curve
- **PR AUC**: Area Under the Precision-Recall curve
- **F1 Score**: Harmonic mean of precision and recall
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)

## 🐛 Troubleshooting

### No Terraform files found
- Ensure `.tf` files are placed in `data/terraform/correct/` or `data/terraform/misconfig/`
- The system will generate synthetic data if no files are found

### NaN values in features
- Run with `--fix-nan` flag: `python main.py --fix-nan`

### Low model performance
- Ensure you have enough diverse training samples
- Check that features have good variance
- Try adjusting the contamination rate

### Visualization errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that model training completed successfully

## 📝 Logging

All operations are logged to `anomaly_detection.log` with timestamps and severity levels. Use `--verbose` flag for detailed debugging information.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [scikit-learn](https://scikit-learn.org/)
- Visualizations powered by [matplotlib](https://matplotlib.org/), [seaborn](https://seaborn.pydata.org/), and [plotly](https://plotly.com/)
- Terraform parsing using [python-hcl2](https://github.com/amplify-education/python-hcl2)
- Rich console output with [rich](https://github.com/Textualize/rich)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This is a research/educational project. Always validate detected anomalies manually before taking action on production infrastructure.
