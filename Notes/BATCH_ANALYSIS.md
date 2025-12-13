# Batch Directory Analysis - Quick Reference

## ✅ Already Implemented!

The `analyze_custom_tf.py` script **already supports** analyzing bunches of .tf files from folders with multiple subdirectories.

## How to Use

### Basic Directory Analysis
```bash
python analyze_custom_tf.py --input /path/to/terraform/folder/
```

### With All Features
```bash
python analyze_custom_tf.py \
  --input /path/to/terraform/projects/ \
  --explain \
  --output ./analysis-results/ \
  --threshold 0.6 \
  --verbose
```

## What Happens

1. **Recursive Search**: Finds ALL `.tf` files in the directory tree (including subdirectories)
2. **Batch Processing**: Processes each file individually
3. **Combined Analysis**: Merges all results into a single report
4. **Comprehensive Output**: One report covering all files

## Example Directory Structure

```
/my-terraform-projects/
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
    └── test-buckets.tf
```

**Command:**
```bash
python analyze_custom_tf.py --input /my-terraform-projects/ --explain
```

**Result:**
- Finds and analyzes **all 6 .tf files**
- Generates one comprehensive report
- Includes LLM explanations for anomalies

## Output Example

```
Found 6 Terraform files in /my-terraform-projects/
Extracted features from 6 files: 18 total configurations

┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Bucket Name   ┃ Source File     ┃ Ensemble Score ┃ Status   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ prod-data     │ s3-main.tf      │ 0.234          │ ✓ Normal │
│ public-web    │ s3-backup.tf    │ 0.876          │ 🚨 ANOMALY│
│ staging-app   │ s3-staging.tf   │ 0.123          │ ✓ Normal │
└───────────────┴─────────────────┴────────────────┴──────────┘

Analysis complete: 3 anomalies detected
Results saved to ./analysis-results/
```

## Files Generated

- `analysis_results.csv` - All configurations with scores
- `analysis_summary.json` - Summary statistics
- `analysis_report.md` - Human-readable report
- `explanations/` - LLM explanations (if --explain used)

## Pro Tips

### 1. Analyze Multiple Project Roots
```bash
# Create a wrapper script
for project in ~/terraform-projects/*/; do
    python analyze_custom_tf.py \
        --input "$project" \
        --output "./analysis/$(basename $project)"
done
```

### 2. Filter by Anomaly Threshold
```bash
# Only flag high-confidence anomalies
python analyze_custom_tf.py \
    --input /path/to/projects/ \
    --threshold 0.7
```

### 3. Quick Scan (No Explanations)
```bash
# Fast analysis without LLM
python analyze_custom_tf.py --input /path/to/projects/
```

### 4. Deep Analysis (With Explanations)
```bash
# Detailed analysis with LLM insights
python analyze_custom_tf.py \
    --input /path/to/projects/ \
    --explain \
    --llm-model deepseek-r1:1.5b
```

## The Code That Makes It Work

From `src/utils/custom_analyzer.py`:

```python
# Recursively find ALL .tf files
tf_files = list(Path(directory).rglob("*.tf"))

# Process each file
for tf_file in tf_files:
    features_df = self.extract_features_from_file(str(tf_file))
    all_features.append(features_df)

# Combine into single report
combined_df = pd.concat(all_features, ignore_index=True)
```

The `.rglob("*.tf")` pattern recursively searches through **all subdirectories** automatically!
