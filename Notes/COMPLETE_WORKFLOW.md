# Complete Workflow - From Clean Install to Custom Analysis

This guide provides the complete command sequence to clean old training data, retrain models, and analyze custom Terraform files.

## Step-by-Step Commands

### Step 1: Clean Old Training Data

```bash
# Navigate to project directory
cd /home/shibly/PycharmProjects/iac-anomaly-detection_v.1

# Remove old output data
rm -rf data/output/*

# Verify cleanup
ls -la data/output/
```

### Step 2: Train Models from Scratch

```bash
# Run the full training pipeline
python main.py

# This will:
# - Extract features from data/terraform/correct/ and data/terraform/misconfig/
# - Train all 4 models (Isolation Forest, One-Class SVM, Autoencoder, LOF)
# - Generate visualizations
# - Save models to data/output/models/
```

**Expected output:**
```
✓ Feature extraction completed successfully
✓ Model training completed successfully
✓ Visualization generation completed successfully
```

### Step 3: Verify Models Are Trained

```bash
# Check that model files exist
ls -lh data/output/models/

# You should see:
# - isolation_forest_model.pkl
# - one_class_svm_model.pkl
# - autoencoder_model.pkl
# - local_outlier_factor_model.pkl
```

### Step 4: Analyze Custom Folder with Multiple Subdirectories

```bash
# Basic analysis (replace /path/to/your/terraform/ with your actual path)
python analyze_custom_tf.py --input /path/to/your/terraform/

# Example with real path:
python analyze_custom_tf.py --input ~/projects/infrastructure/terraform/

# With verbose output to see what's happening:
python analyze_custom_tf.py --input /path/to/your/terraform/ --verbose
```

### Step 5: Advanced Analysis with LLM Explanations

```bash
# First, ensure Ollama is running (in a separate terminal)
ollama serve

# Then run analysis with explanations
python analyze_custom_tf.py \
    --input /path/to/your/terraform/ \
    --explain \
    --llm-model deepseek-r1:1.5b \
    --output ./my_analysis_results/ \
    --verbose
```

### Step 6: Review Results

```bash
# View the summary
cat data/output/custom_analysis/analysis_summary.json | python -m json.tool

# View the report
cat data/output/custom_analysis/analysis_report.md

# Open detailed results
xdg-open data/output/custom_analysis/analysis_results.csv

# If you used --explain, view LLM explanations
xdg-open data/output/custom_analysis/explanations/anomaly_report.html
```

## Example: Complete Workflow

```bash
# 1. Clean everything
cd /home/shibly/PycharmProjects/iac-anomaly-detection_v.1
rm -rf data/output/*

# 2. Train models
python main.py

# 3. Analyze your custom Terraform files
python analyze_custom_tf.py \
    --input ~/my-terraform-projects/ \
    --explain \
    --output ./security-audit/ \
    --threshold 0.6 \
    --verbose

# 4. Review results
cat ./security-audit/analysis_summary.json | python -m json.tool
```

## Directory Structure Example

Your custom Terraform folder can have any structure:

```
/my-terraform-projects/
├── production/
│   ├── networking/
│   │   ├── vpc.tf
│   │   └── subnets.tf
│   ├── storage/
│   │   ├── s3-main.tf
│   │   ├── s3-backup.tf
│   │   └── s3-logs.tf
│   └── compute/
│       └── ec2.tf
├── staging/
│   ├── s3-staging.tf
│   └── vpc-staging.tf
└── development/
    ├── dev-resources/
    │   └── s3-dev.tf
    └── test-buckets.tf
```

**Command:**
```bash
python analyze_custom_tf.py --input /my-terraform-projects/ --explain
```

**Result:**
- Finds ALL 10 .tf files across all subdirectories
- Analyzes all S3 bucket configurations
- Detects anomalies
- Generates comprehensive report

## Quick Reference

### Clean and Retrain
```bash
rm -rf data/output/* && python main.py
```

### Analyze Custom Files (Simple)
```bash
python analyze_custom_tf.py --input /path/to/terraform/
```

### Analyze Custom Files (Full Featured)
```bash
python analyze_custom_tf.py \
    --input /path/to/terraform/ \
    --explain \
    --output ./results/ \
    --threshold 0.6 \
    --verbose
```

### Use Specific Models Only
```bash
python analyze_custom_tf.py \
    --input /path/to/terraform/ \
    --models isolation_forest,autoencoder
```

## Troubleshooting

### "Failed to load models"
```bash
# Solution: Train models first
python main.py
```

### "No S3 bucket configurations found"
```bash
# Check your .tf files contain aws_s3_bucket resources
grep -r "aws_s3_bucket" /path/to/terraform/
```

### "Cannot connect to Ollama" (for --explain)
```bash
# Start Ollama in a separate terminal
ollama serve

# Verify model is available
ollama list

# Pull model if needed
ollama pull deepseek-r1:1.5b
```

## All Available Options

```bash
python analyze_custom_tf.py --help
```

**Key options:**
- `--input`, `-i` - Path to file or directory (required)
- `--output`, `-o` - Output directory (default: data/output/custom_analysis)
- `--models` - Comma-separated model names (default: all)
- `--threshold` - Anomaly threshold 0.0-1.0 (default: 0.5)
- `--explain` - Generate LLM explanations
- `--llm-model` - Ollama model name (default: deepseek-r1:1.5b)
- `--verbose`, `-v` - Verbose output

## Integration with Main Pipeline

You can also use the main script:

```bash
# Clean and analyze in one go
rm -rf data/output/*
python main.py --analyze-custom /path/to/terraform/ --explain-anomalies
```

This approach trains models first, then analyzes your custom files automatically.
