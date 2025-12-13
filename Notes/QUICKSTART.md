# Quick Start Guide - Analyzing Custom Terraform Files

## ✅ Your Solution is Ready!

You can now analyze **bunches of .tf files from folders (including nested subdirectories)** using your pre-trained models.

## One Command Does It All

```bash
python analyze_custom_tf.py --input /path/to/your/terraform/projects/
```

This will:
- 🔍 **Recursively find** all `.tf` files in the directory tree
- 📊 **Analyze** each configuration
- 🚨 **Detect** anomalies using your trained models
- 📝 **Generate** comprehensive reports

## Example

```
Your directory structure:
/my-infrastructure/
├── production/
│   ├── storage/s3.tf
│   └── network/vpc.tf
├── staging/
│   └── s3-staging.tf
└── dev/
    ├── test-s3.tf
    └── experimental.tf

Command:
$ python analyze_custom_tf.py --input /my-infrastructure/ --explain

Output:
✓ Found 5 Terraform files
✓ Analyzed 15 S3 bucket configurations
✓ Detected 3 anomalies
✓ Generated LLM explanations
✓ Results saved to data/output/custom_analysis/
```

## Common Use Cases

### 1. Quick Security Scan
```bash
python analyze_custom_tf.py --input ~/projects/terraform/
```

### 2. Deep Analysis with Explanations
```bash
python analyze_custom_tf.py --input ~/projects/terraform/ --explain
```

### 3. High-Confidence Anomalies Only
```bash
python analyze_custom_tf.py --input ~/projects/ --threshold 0.7
```

### 4. Custom Output Location
```bash
python analyze_custom_tf.py --input ~/projects/ --output ./security-audit/
```

## Before First Use

Train your models once (if not already done):
```bash
python main.py
```

## Get Help

```bash
python analyze_custom_tf.py --help
```

## Full Documentation

- [`CUSTOM_ANALYSIS_GUIDE.md`](CUSTOM_ANALYSIS_GUIDE.md) - Complete usage guide
- [`BATCH_ANALYSIS.md`](BATCH_ANALYSIS.md) - Batch processing reference
- [`walkthrough.md`](.gemini/antigravity/brain/.../walkthrough.md) - Implementation details

---

**That's it!** The tool automatically handles nested directories, multiple files, and generates comprehensive reports. 🎉
