# Manual Usage Guide - IaC Anomaly Detection

## Overview

This guide shows you how to manually use the trained anomaly detection models to analyze your Terraform files for security anomalies.

## Prerequisites

✅ Models must be trained first (located in `data/output/models/`)
✅ Virtual environment activated
✅ All dependencies installed

---

## Quick Start

### 1. Activate Virtual Environment

```bash
cd /home/shibly/PycharmProjects/iac-anomaly-detection_v.1
source .venv/bin/activate
```

### 2. Basic Analysis

```bash
# Analyze a single .tf file
python analyze_custom_tf.py --input /path/to/file.tf

# Analyze an entire directory (recursive)
python analyze_custom_tf.py --input /path/to/terraform/directory/

# Example with the learn-terraform-modules folder
python analyze_custom_tf.py --input infrastructure/learn-terraform-modules/
```

---

## Command Options

### Basic Options

| Option | Description | Example |
|--------|-------------|---------|
| `--input` / `-i` | Path to .tf file or directory (required) | `--input ./my-terraform/` |
| `--output` / `-o` | Output directory for results | `--output ./results/` |
| `--verbose` / `-v` | Enable detailed logging | `--verbose` |

### Model Selection

```bash
# Use all models (default)
python analyze_custom_tf.py --input ./terraform/

# Use specific models only
python analyze_custom_tf.py --input ./terraform/ \
  --models isolation_forest,autoencoder

# Available models:
# - isolation_forest
# - one_class_svm
# - autoencoder
# - local_outlier_factor
```

### Threshold Configuration

```bash
# Set anomaly threshold (default: 0.5)
python analyze_custom_tf.py --input ./terraform/ --threshold 0.7

# Lower threshold = more sensitive (more anomalies detected)
# Higher threshold = less sensitive (fewer anomalies detected)
```

### LLM Explanations

```bash
# Generate AI-powered explanations for anomalies
python analyze_custom_tf.py --input ./terraform/ --explain

# Specify LLM model
python analyze_custom_tf.py --input ./terraform/ \
  --explain \
  --llm-model deepseek-r1:1.5b

# Set minimum score for LLM explanation
python analyze_custom_tf.py --input ./terraform/ \
  --explain \
  --min-anomaly-score 0.6
```

---

## Complete Examples

### Example 1: Quick Scan

```bash
source .venv/bin/activate
python analyze_custom_tf.py \
  --input infrastructure/learn-terraform-modules/
```

**Output:**
- `data/output/custom_analysis/analysis_results.csv`
- `data/output/custom_analysis/analysis_summary.json`
- `data/output/custom_analysis/analysis_report.md`

### Example 2: Detailed Analysis with Explanations

```bash
source .venv/bin/activate
python analyze_custom_tf.py \
  --input /path/to/production/terraform/ \
  --output ./security_audit_2025/ \
  --explain \
  --llm-model deepseek-r1:1.5b \
  --threshold 0.6 \
  --verbose
```

### Example 3: Specific Models Only

```bash
source .venv/bin/activate
python analyze_custom_tf.py \
  --input ./terraform/s3-buckets/ \
  --models isolation_forest,local_outlier_factor \
  --output ./s3_analysis/
```

---

## Understanding the Output

### 1. Analysis Results CSV

**Location:** `data/output/custom_analysis/analysis_results.csv`

Contains detailed information for each S3 bucket configuration:
- Bucket name and source file
- Security features (encryption, versioning, logging, etc.)
- Individual model scores
- Ensemble score (average of all models)
- Anomaly classification

### 2. Summary JSON

**Location:** `data/output/custom_analysis/analysis_summary.json`

```json
{
  "total_configurations": 10,
  "anomalies_detected": 3,
  "anomaly_rate": 0.3,
  "average_ensemble_score": 0.45,
  "max_ensemble_score": 0.87,
  "models_used": ["isolation_forest", "one_class_svm", "autoencoder", "local_outlier_factor"],
  "high_risk_configs": [...]
}
```

### 3. Markdown Report

**Location:** `data/output/custom_analysis/analysis_report.md`

Human-readable report with:
- Summary statistics
- High-risk configurations (score > 0.7)
- Detailed results table

### 4. LLM Explanations (if --explain used)

**Location:** `data/output/custom_analysis/explanations/`

- `anomaly_explanations.md` - Markdown report with AI explanations
- `anomaly_explanations.html` - HTML version

---

## Interpreting Anomaly Scores

| Score Range | Severity | Meaning |
|-------------|----------|---------|
| 0.0 - 0.3 | ✅ Low | Normal configuration |
| 0.3 - 0.5 | ⚠️ Medium | Slightly unusual, review recommended |
| 0.5 - 0.7 | 🔶 High | Anomalous, investigate |
| 0.7 - 1.0 | 🚨 Critical | Highly anomalous, immediate review |

---

## Step-by-Step Manual Process

### Step 1: Check Models Exist

```bash
ls -lh data/output/models/
```

You should see:
- `isolation_forest.pkl`
- `one_class_svm.pkl`
- `autoencoder.pkl`
- `local_outlier_factor.pkl`
- `scaler.pkl` (in `data/output/features/`)

### Step 2: Prepare Your Terraform Files

Organize your `.tf` files in a directory:
```
my-terraform/
├── main.tf
├── variables.tf
├── s3-buckets/
│   ├── bucket1.tf
│   └── bucket2.tf
└── modules/
    └── storage/
        └── main.tf
```

### Step 3: Run Analysis

```bash
source .venv/bin/activate
python analyze_custom_tf.py --input ./my-terraform/ --verbose
```

### Step 4: Review Results

```bash
# View summary
cat data/output/custom_analysis/analysis_report.md

# View detailed CSV
xdg-open data/output/custom_analysis/analysis_results.csv

# View JSON summary
cat data/output/custom_analysis/analysis_summary.json | jq
```

### Step 5: Generate Explanations (Optional)

```bash
python analyze_custom_tf.py \
  --input ./my-terraform/ \
  --output ./my_analysis/ \
  --explain
```

---

## Troubleshooting

### Error: "No module named 'pandas'"

**Solution:** Activate virtual environment
```bash
source .venv/bin/activate
```

### Error: "Models not found"

**Solution:** Train models first
```bash
python main.py
```

### Error: "No S3 bucket configurations found"

**Meaning:** Your `.tf` files don't contain S3 bucket resources. The tool currently only analyzes S3 buckets.

### Low/Zero Anomaly Scores

**Possible Reasons:**
1. Configurations are similar to training data (normal)
2. Models need retraining with more diverse data
3. Threshold too high

---

## Advanced Usage

### Custom Output Location

```bash
python analyze_custom_tf.py \
  --input ./terraform/ \
  --output /tmp/security_scan_$(date +%Y%m%d)/
```

### Batch Processing Multiple Directories

```bash
#!/bin/bash
for dir in project1 project2 project3; do
  python analyze_custom_tf.py \
    --input ./terraform/$dir/ \
    --output ./results/$dir/ \
    --explain
done
```

### Integration with CI/CD

```bash
# Exit with error if anomalies detected
python analyze_custom_tf.py --input ./terraform/ --threshold 0.5
if [ $? -ne 0 ]; then
  echo "Anomalies detected! Review required."
  exit 1
fi
```

---

## Using the Complete Workflow Script

For a full pipeline (clean → train → analyze):

```bash
./run_complete_workflow.sh /path/to/terraform/files/ ./output_dir/
```

This script:
1. Cleans old training data
2. Trains models from scratch
3. Analyzes your custom Terraform files
4. Displays results summary

---

## Model Information

### Trained Models

| Model | Type | Best For |
|-------|------|----------|
| **Isolation Forest** | Tree-based | Global anomalies, fast |
| **One-Class SVM** | Kernel-based | Complex boundaries |
| **Autoencoder** | Neural network | Pattern reconstruction |
| **Local Outlier Factor** | Density-based | Local anomalies |

### Ensemble Approach

The tool uses an **ensemble** of all 4 models:
- Each model generates an anomaly score (0-1)
- Scores are averaged to create ensemble score
- More robust than single model

---

## Next Steps

1. ✅ Analyze your Terraform files
2. 📊 Review anomaly scores
3. 🔍 Investigate high-risk configurations
4. 🤖 Use `--explain` for AI-powered insights
5. 🔒 Remediate security issues

---

## Support

For issues or questions:
- Check logs: `custom_analysis.log`
- Review documentation: `README_CUSTOM_ANALYSIS.md`
- Enable verbose mode: `--verbose`

---

## Quick Reference Card

```bash
# Basic scan
python analyze_custom_tf.py --input ./terraform/

# With explanations
python analyze_custom_tf.py --input ./terraform/ --explain

# Custom threshold
python analyze_custom_tf.py --input ./terraform/ --threshold 0.7

# Specific models
python analyze_custom_tf.py --input ./terraform/ --models isolation_forest,autoencoder

# Full options
python analyze_custom_tf.py \
  --input ./terraform/ \
  --output ./results/ \
  --models isolation_forest,one_class_svm,autoencoder,local_outlier_factor \
  --threshold 0.5 \
  --explain \
  --llm-model deepseek-r1:1.5b \
  --min-anomaly-score 0.5 \
  --verbose
```
