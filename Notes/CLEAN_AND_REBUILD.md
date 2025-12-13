# How to Clean and Rebuild the Project

This document provides instructions on how to clean old results and rebuild the anomaly detection project from scratch.

## 1. Setup the Environment

Before running the project, ensure you have all the required Python dependencies installed. It is recommended to use a virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

## 2. Clean Old Results

The cleaning process involves removing the directory where all generated files are stored and the main log file.

```bash
# Remove the output directory
rm -rf data/output

# Remove the log file
rm -f anomaly_detection.log
```

This will delete all previously generated features, models, plots, and reports.

## 3. Rebuild the Project

To run the entire pipeline and regenerate all results, execute the main script.

```bash
python main.py
```

This command will:
1.  Extract features from the Terraform files.
2.  Train the anomaly detection models.
3.  Generate visualizations and save them in `data/output/plots`.

### Optional: Generate LLM Explanations

If you want to generate LLM-powered explanations for the detected anomalies, you need to have [Ollama](https://ollama.com/) installed and running.

First, start the Ollama server in a separate terminal:
```bash
ollama serve
```

Then, run the main script with the `--explain-anomalies` flag:
```bash
python main.py --explain-anomalies
```

This will generate detailed explanations and reports in the `data/output/explanations` directory.
