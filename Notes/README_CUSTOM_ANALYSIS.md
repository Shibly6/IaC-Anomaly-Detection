# Custom Terraform Analysis - Quick Commands

## 🚀 Automated Workflow (Recommended)

Use the automated script to do everything in one command:

```bash
# Make script executable (first time only)
chmod +x run_complete_workflow.sh

# Run complete workflow
./run_complete_workflow.sh /path/to/your/terraform/folder/
```

This will:
1. ✅ Clean old training data
2. ✅ Train all models from scratch
3. ✅ Analyze your custom Terraform files
4. ✅ Generate comprehensive reports

### Example

```bash
# Analyze your production infrastructure
./run_complete_workflow.sh ~/projects/production-terraform/ ./prod-audit/

# Analyze development files
./run_complete_workflow.sh ~/dev/terraform-configs/ ./dev-analysis/
```

---

## 📝 Manual Step-by-Step Commands

If you prefer to run each step manually:

### 1. Clean Old Data

```bash
rm -rf data/output/*
```

### 2. Train Models

```bash
python main.py
```

### 3. Analyze Custom Files

```bash
# Basic analysis
python analyze_custom_tf.py --input /path/to/your/terraform/

# With explanations
python analyze_custom_tf.py --input /path/to/your/terraform/ --explain
```

### 4. View Results

```bash
# Summary
cat data/output/custom_analysis/analysis_summary.json | python -m json.tool

# Report
cat data/output/custom_analysis/analysis_report.md
```

---

## 🎯 Common Use Cases

### Analyze Production Infrastructure

```bash
./run_complete_workflow.sh ~/production/terraform/ ./prod-security-audit/
```

### Analyze Multiple Projects

```bash
# All projects in one directory
./run_complete_workflow.sh ~/all-terraform-projects/ ./security-scan/
```

### Quick Security Check

```bash
python analyze_custom_tf.py --input ~/terraform/ --threshold 0.7
```

### Deep Analysis with AI Explanations

```bash
# Ensure Ollama is running first: ollama serve
python analyze_custom_tf.py \
    --input ~/terraform/ \
    --explain \
    --llm-model deepseek-r1:1.5b \
    --output ./detailed-analysis/
```

---

## 📂 Your Terraform Folder Structure

The analyzer works with **any folder structure**, including nested subdirectories:

```
/your-terraform-folder/
├── production/
│   ├── storage/
│   │   ├── s3-main.tf
│   │   └── s3-backup.tf
│   └── network/
│       └── vpc.tf
├── staging/
│   └── s3-staging.tf
└── development/
    ├── dev-s3.tf
    └── test.tf
```

**All .tf files will be found and analyzed automatically!**

---

## 📊 Output Files

After analysis, you'll find:

```
data/output/custom_analysis/  (or your custom output directory)
├── analysis_results.csv       # Detailed results for each configuration
├── analysis_summary.json      # Summary statistics
├── analysis_report.md         # Human-readable report
└── explanations/              # LLM explanations (if --explain used)
    ├── anomaly_report.md
    └── anomaly_report.html
```

---

## 🔧 Troubleshooting

### Models not found?
```bash
# Train models first
python main.py
```

### No .tf files found?
```bash
# Check your path has .tf files
find /path/to/folder -name "*.tf"
```

### Ollama connection error?
```bash
# Start Ollama (in separate terminal)
ollama serve

# Verify model exists
ollama list

# Pull if needed
ollama pull deepseek-r1:1.5b
```

---

## 📚 Full Documentation

- [`COMPLETE_WORKFLOW.md`](COMPLETE_WORKFLOW.md) - Detailed step-by-step guide
- [`CUSTOM_ANALYSIS_GUIDE.md`](CUSTOM_ANALYSIS_GUIDE.md) - Complete usage documentation
- [`BATCH_ANALYSIS.md`](BATCH_ANALYSIS.md) - Batch processing reference
- [`QUICKSTART.md`](QUICKSTART.md) - Quick start guide

---

## ⚡ TL;DR

```bash
# One command to rule them all:
./run_complete_workflow.sh /path/to/your/terraform/folder/
```

That's it! 🎉
