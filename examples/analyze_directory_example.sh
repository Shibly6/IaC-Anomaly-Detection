#!/bin/bash
# Example: Analyze multiple Terraform projects at once

# Analyze a complex directory structure with multiple projects
python analyze_custom_tf.py \
  --input /path/to/your/terraform/projects/ \
  --explain \
  --output ./security-analysis/ \
  --verbose

# The script will:
# 1. Recursively find ALL .tf files in the directory tree
# 2. Extract features from each file
# 3. Run anomaly detection on all configurations
# 4. Generate a single comprehensive report
# 5. Create LLM explanations for detected anomalies

# Example output:
# Found 47 Terraform files in /path/to/your/terraform/projects/
# Extracted features from 47 files: 152 total configurations
# Analysis complete: 12 anomalies detected
# Results saved to ./security-analysis/
