# Custom Terraform File Analysis

This guide explains how to analyze Terraform files from any directory using the pre-trained anomaly detection models.

## Quick Start

### Analyze a Single File

```bash
python analyze_custom_tf.py --input /path/to/your/file.tf
```

### Analyze a Directory

```bash
python analyze_custom_tf.py --input /path/to/your/terraform/directory/
```

### With LLM Explanations

```bash
python analyze_custom_tf.py --input /path/to/file.tf --explain
```

## Prerequisites

1. **Train Models First**: Before analyzing custom files, you need to train the models:
   ```bash
   python main.py
   ```

2. **Ollama (Optional)**: For LLM explanations, ensure Ollama is running:
   ```bash
   ollama serve
   ```

## Usage Examples

### Basic Analysis

Analyze a single Terraform file:
```bash
python analyze_custom_tf.py --input ~/projects/infrastructure/s3.tf
```

### Directory Analysis with Explanations

Analyze all `.tf` files in a directory with LLM-powered explanations:
```bash
python analyze_custom_tf.py \
  --input ~/projects/infrastructure/ \
  --explain \
  --llm-model deepseek-r1:1.5b
```

### Using Specific Models

Use only specific anomaly detection models:
```bash
python analyze_custom_tf.py \
  --input /path/to/file.tf \
  --models isolation_forest,autoencoder
```

### Custom Output Location

Save results to a custom directory:
```bash
python analyze_custom_tf.py \
  --input /path/to/file.tf \
  --output ./my_analysis_results/
```

### Adjust Anomaly Threshold

Change the anomaly classification threshold (default is 0.5):
```bash
python analyze_custom_tf.py \
  --input /path/to/file.tf \
  --threshold 0.7
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input`, `-i` | Path to .tf file or directory (required) | - |
| `--output`, `-o` | Output directory for results | `data/output/custom_analysis` |
| `--models-dir` | Directory containing trained models | `data/output` |
| `--models` | Comma-separated list of models to use | All available |
| `--threshold` | Anomaly score threshold (0.0-1.0) | 0.5 |
| `--explain` | Generate LLM explanations | False |
| `--llm-model` | Ollama model for explanations | `deepseek-r1:1.5b` |
| `--min-anomaly-score` | Minimum score for LLM explanation | 0.5 |
| `--verbose`, `-v` | Enable verbose logging | False |

## Output Files

The analysis generates the following files in the output directory:

### 1. `analysis_results.csv`
Detailed results for each configuration with:
- Bucket name and source file
- Individual model scores
- Ensemble score
- Anomaly classification
- Configuration features

### 2. `analysis_summary.json`
Summary statistics including:
- Total configurations analyzed
- Number of anomalies detected
- Anomaly rate
- High-risk configurations
- Models used

### 3. `analysis_report.md`
Human-readable Markdown report with:
- Executive summary
- High-risk configurations
- Detailed results table

### 4. `explanations/` (if `--explain` is used)
LLM-generated explanations including:
- Detailed analysis of each anomaly
- Security implications
- Remediation recommendations
- HTML and Markdown reports

## Understanding Results

### Anomaly Scores

Each configuration receives an **ensemble score** (0.0 to 1.0):
- **0.0 - 0.3**: Low risk, likely normal configuration
- **0.3 - 0.5**: Medium risk, review recommended
- **0.5 - 0.7**: High risk, likely anomaly
- **0.7 - 1.0**: Very high risk, immediate attention required

### Model Scores

Individual scores from each model:
- `isolation_forest_score`: Isolation-based anomaly detection
- `one_class_svm_score`: SVM-based outlier detection
- `autoencoder_score`: Reconstruction error-based detection
- `local_outlier_factor_score`: Density-based local outlier detection

## Integration with Main Pipeline

You can also use the main script for custom analysis:

```bash
python main.py --analyze-custom /path/to/file.tf --explain-anomalies
```

This approach:
- Uses the main pipeline infrastructure
- Automatically loads trained models
- Integrates with existing LLM explainer
- Saves results to standard output directory

## Example Workflow

### 1. Train Models (One-time)
```bash
# Train on your categorized data
python main.py
```

### 2. Analyze Production Files
```bash
# Analyze your production Terraform files
python analyze_custom_tf.py \
  --input ~/production/terraform/ \
  --explain \
  --output ./production_analysis/
```

### 3. Review Results
```bash
# View the report
cat ./production_analysis/analysis_report.md

# Check high-risk configurations
cat ./production_analysis/analysis_summary.json | jq '.high_risk_configs'
```

### 4. Review LLM Explanations
```bash
# Open HTML report in browser
xdg-open ./production_analysis/explanations/anomaly_report.html
```

## Troubleshooting

### "Failed to load models"
- Ensure you've trained models first: `python main.py`
- Check that `data/output/models/` contains `.pkl` files

### "No S3 bucket configurations found"
- Verify your .tf files contain `aws_s3_bucket` resources
- Check file syntax is valid Terraform

### "Cannot connect to Ollama"
- Start Ollama: `ollama serve`
- Verify the model is available: `ollama list`
- Pull the model if needed: `ollama pull deepseek-r1:1.5b`

### "Missing features" warning
- This is normal for files with different configurations
- Missing features are automatically filled with default values

## Best Practices

1. **Regular Scans**: Analyze your infrastructure code regularly
2. **Version Control**: Track analysis results over time
3. **Threshold Tuning**: Adjust threshold based on your risk tolerance
4. **Review Explanations**: Use LLM explanations to understand why configurations are flagged
5. **Continuous Training**: Retrain models periodically with new data

## Advanced Usage

### Batch Analysis Script

Create a script to analyze multiple projects:

```bash
#!/bin/bash
for project in ~/projects/*/terraform/; do
    echo "Analyzing $project"
    python analyze_custom_tf.py \
        --input "$project" \
        --output "./analysis/$(basename $(dirname $project))" \
        --explain
done
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/terraform-security.yml
- name: Analyze Terraform Security
  run: |
    python analyze_custom_tf.py \
      --input ./terraform/ \
      --threshold 0.6 \
      --output ./security-analysis/
    
    # Fail if high-risk anomalies found
    if [ $(jq '.anomalies_detected' ./security-analysis/analysis_summary.json) -gt 0 ]; then
      exit 1
    fi
```

## Support

For issues or questions:
1. Check the logs: `custom_analysis.log`
2. Enable verbose mode: `--verbose`
3. Review the main project documentation
