# Quick Start Guide - LLM Explainer for IaC Anomaly Detection

## 🚀 Quick Start (5 minutes)

### Step 1: Ensure Ollama is Running

```bash
# Check if Ollama is installed
ollama --version

# Start Ollama (in a separate terminal)
ollama serve

# Verify models are available
ollama list
# Should show: gemma3:1b and deepseek-r1:1.5b
```

### Step 2: Install Dependencies

```bash
cd /home/shibly/PycharmProjects/iac-anomaly-detection_v.1

# Install/update requirements
pip install -r requirements.txt
```

### Step 3: Test the Module

```bash
# Test Ollama connection
python -m llm_explainer.ollama_client --test

# Expected output:
# ✓ Connected to Ollama
# ✓ Using model: deepseek-r1:1.5b
# ✓ Generation test passed
```

### Step 4: Run the Full Pipeline

```bash
# Run anomaly detection WITH LLM explanations
python main.py --explain-anomalies

# This will:
# 1. Extract features from Terraform files
# 2. Train anomaly detection models
# 3. Generate visualizations
# 4. Generate LLM-powered explanations ← NEW!
# 5. Create HTML and Markdown reports
```

### Step 5: View Results

```bash
# Open the HTML report in your browser
xdg-open data/output/explanations/detailed_report.html

# Or view the Markdown report
cat data/output/explanations/detailed_report.md

# Check the executive summary
cat data/output/explanations/executive_summary.txt
```

---

## 📊 Example Commands

### Use Faster Model
```bash
python main.py --explain-anomalies --llm-model gemma3:1b
```

### Only Explain High-Severity Issues
```bash
python main.py --explain-anomalies --min-anomaly-score 0.7
```

### Skip Other Phases (Only Generate Explanations)
```bash
python main.py --skip-extraction --skip-training --skip-visualization --explain-anomalies
```

### Run Without Explanations (Original Behavior)
```bash
python main.py --skip-explanation
```

---

## 🔍 Verify Installation

```bash
# Check module structure
ls -la llm_explainer/

# Should show:
# __init__.py
# cache.py
# config.py
# context_builder.py
# example_usage.py
# explanation_generator.py
# ollama_client.py
# prompt_templates.py
# report_builder.py
# README.md

# Run example usage
python llm_explainer/example_usage.py
```

---

## 🐛 Troubleshooting

### "Cannot connect to Ollama"
```bash
# Make sure Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### "Model not found"
```bash
# Pull the model
ollama pull deepseek-r1:1.5b

# Or use the faster model
ollama pull gemma3:1b
```

### "No anomalies found"
```bash
# Run the full pipeline first
python main.py

# Then generate explanations
python main.py --skip-extraction --skip-training --skip-visualization --explain-anomalies
```

---

## 📁 Output Structure

After running with `--explain-anomalies`, you'll find:

```
data/output/explanations/
├── anomaly_explanations.json    # Structured data
├── detailed_report.md            # Markdown report
├── detailed_report.html          # Styled HTML report ← Open this!
├── executive_summary.txt         # Management summary
└── cache/                        # Cached responses
```

---

## ⚡ Performance Tips

1. **Use gemma3:1b for speed** (~2-3 sec per explanation)
2. **Use deepseek-r1:1.5b for quality** (~4-6 sec per explanation)
3. **Enable caching** (enabled by default) - reduces repeat calls to <0.1 sec
4. **Limit anomalies** with `--min-anomaly-score` to focus on critical issues

---

## 📚 Learn More

- Full documentation: `llm_explainer/README.md`
- Example usage: `llm_explainer/example_usage.py`
- Configuration: `llm_explainer/config.py`

---

## ✅ Success Checklist

- [ ] Ollama is running (`ollama serve`)
- [ ] Models are available (`ollama list`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Connection test passed (`python -m llm_explainer.ollama_client --test`)
- [ ] Pipeline runs successfully (`python main.py --explain-anomalies`)
- [ ] Reports generated in `data/output/explanations/`

**You're ready to go! 🎉**
