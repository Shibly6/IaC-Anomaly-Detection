# LLM Explainer Module

## Overview

The **LLM Explainer Module** enhances the IaC Anomaly Detection tool by providing **human-readable explanations** for detected misconfigurations using local Ollama models. Instead of just showing anomaly scores, it explains:

- **WHY** a configuration is flagged as anomalous
- **WHAT** the security implications are
- **HOW** to fix the issues with Terraform code examples
- **WHICH** compliance frameworks are affected

## Features

✅ **Offline LLM Integration** - Uses local Ollama models (no cloud API costs)  
✅ **Detailed Explanations** - Root cause analysis and security implications  
✅ **Remediation Guidance** - Step-by-step fixes with Terraform code snippets  
✅ **Professional Reports** - Markdown and HTML reports with styling  
✅ **Smart Caching** - Avoids redundant LLM calls for identical anomalies  
✅ **Batch Processing** - Handles multiple anomalies efficiently  
✅ **Executive Summaries** - High-level overview for management  

## Prerequisites

1. **Ollama installed and running**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Start Ollama service
   ollama serve
   ```

2. **Pull required models**
   ```bash
   # Option 1: Fast, lightweight model
   ollama pull gemma3:1b
   
   # Option 2: More capable model (recommended)
   ollama pull deepseek-r1:1.5b
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the full pipeline with LLM explanations:

```bash
python main.py --explain-anomalies
```

### Advanced Options

```bash
# Use specific Ollama model
python main.py --explain-anomalies --llm-model gemma3:1b

# Set minimum anomaly score threshold
python main.py --explain-anomalies --min-anomaly-score 0.7

# Skip other phases and only generate explanations
python main.py --skip-extraction --skip-training --skip-visualization --explain-anomalies

# Run without explanations
python main.py --skip-explanation
```

### Standalone Usage

You can also run the explainer module independently:

```bash
# Generate explanations for existing anomaly detection results
python -m llm_explainer.explanation_generator

# With custom options
python -m llm_explainer.explanation_generator \
    --output-dir data/output \
    --model deepseek-r1:1.5b \
    --min-score 0.6 \
    --max-anomalies 10
```

### Test Ollama Connection

```bash
# Test if Ollama is accessible
python -m llm_explainer.ollama_client --test
```

## Output

The module generates the following outputs in `data/output/explanations/`:

- **`anomaly_explanations.json`** - Structured explanations in JSON format
- **`detailed_report.md`** - Human-readable Markdown report
- **`detailed_report.html`** - Professional HTML report with styling
- **`executive_summary.txt`** - High-level summary for management
- **`cache/`** - Cached LLM responses (optional)

## Example Output

### Before (Without LLM Explanation)
```
Anomaly detected in bucket: my-data-bucket
Anomaly Score: 0.87
Prediction: Anomalous (1)
```

### After (With LLM Explanation)
```
🔴 CRITICAL: Public Access Misconfiguration Detected

Bucket: my-data-bucket
Anomaly Score: 0.87 (High Risk)

WHY THIS IS FLAGGED:
The S3 bucket is configured with 'public-read' ACL, making all objects 
publicly accessible on the internet. This violates AWS security best 
practices and exposes sensitive data to unauthorized access.

SECURITY IMPLICATIONS:
- Data Exposure: Anyone can read bucket contents
- Compliance Violation: Fails CIS AWS Benchmark 2.1.5
- Attack Vector: Potential for data exfiltration

HOW TO FIX:
1. Change ACL to 'private'
2. Enable S3 Block Public Access
3. Add bucket encryption
4. Enable versioning and logging

REMEDIATION CODE:
```hcl
resource "aws_s3_bucket" "my-data-bucket" {
  bucket = "my-data-bucket"
  acl    = "private"  # Changed from public-read
  
  versioning {
    enabled = true
  }
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
```
```

## Configuration

Edit `llm_explainer/config.py` to customize:

- **Ollama endpoint** (default: `http://localhost:11434`)
- **Model preferences** (gemma3:1b vs deepseek-r1:1.5b)
- **Temperature and sampling parameters**
- **Cache settings** (enable/disable, expiry time)
- **Severity thresholds**

## Architecture

```
llm_explainer/
├── __init__.py              # Package initialization
├── config.py                # Configuration settings
├── ollama_client.py         # Ollama API wrapper
├── prompt_templates.py      # Structured prompts for different anomaly types
├── context_builder.py       # Extract anomaly context from detection results
├── cache.py                 # File-based caching system
├── explanation_generator.py # Main orchestrator
└── report_builder.py        # Generate Markdown/HTML reports
```

## Workflow

1. **Context Extraction** - Loads anomaly detection results and extracts relevant features
2. **Prompt Generation** - Creates structured prompts based on anomaly type
3. **LLM Inference** - Calls Ollama API for explanation generation
4. **Caching** - Stores results to avoid redundant API calls
5. **Report Building** - Generates professional Markdown and HTML reports

## Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check if Ollama is accessible: `curl http://localhost:11434/api/tags`

### "Model not found"
- Pull the model: `ollama pull deepseek-r1:1.5b`
- List available models: `ollama list`

### "No anomalies found to explain"
- Run the full pipeline first: `python main.py`
- Check if anomalies were detected in previous phases
- Lower the `--min-anomaly-score` threshold

### Slow performance
- Use the faster model: `--llm-model gemma3:1b`
- Limit number of anomalies: `--max-anomalies 5`
- Enable caching (enabled by default)

## Performance

- **gemma3:1b**: ~2-3 seconds per explanation (faster, lighter)
- **deepseek-r1:1.5b**: ~4-6 seconds per explanation (more detailed)
- Caching reduces repeated explanations to <0.1 seconds

## Benefits

1. **Increased Developer Trust** - Clear explanations build confidence in the tool
2. **Faster Remediation** - Direct code examples speed up fixes
3. **Learning Tool** - Educates developers on security best practices
4. **Compliance Mapping** - Links findings to compliance frameworks
5. **Offline Operation** - No cloud API costs or data privacy concerns

## License

Same as parent project.
