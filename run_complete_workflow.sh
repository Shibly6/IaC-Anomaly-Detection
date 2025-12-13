#!/bin/bash
# Complete Workflow Script
# This script cleans old data, trains models, and analyzes custom Terraform files

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     IaC Anomaly Detection - Complete Workflow                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
CUSTOM_TF_PATH="${1:-}"  # First argument is the path to custom .tf files
OUTPUT_DIR="${2:-./custom_analysis_results}"  # Second argument is output directory

if [ -z "$CUSTOM_TF_PATH" ]; then
    echo "❌ Error: Please provide the path to your Terraform files"
    echo ""
    echo "Usage: $0 /path/to/terraform/folder [output_directory]"
    echo ""
    echo "Example:"
    echo "  $0 ~/my-terraform-projects/ ./results/"
    echo ""
    exit 1
fi

if [ ! -d "$CUSTOM_TF_PATH" ] && [ ! -f "$CUSTOM_TF_PATH" ]; then
    echo "❌ Error: Path does not exist: $CUSTOM_TF_PATH"
    exit 1
fi

echo "📁 Custom Terraform Path: $CUSTOM_TF_PATH"
echo "📊 Output Directory: $OUTPUT_DIR"
echo ""

# Step 1: Clean old training data
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Cleaning old training data..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "data/output" ]; then
    echo "🗑️  Removing old output data..."
    rm -rf data/output/*
    echo "✅ Old data cleaned"
else
    echo "ℹ️  No old data to clean"
fi
echo ""

# Step 2: Train models
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Training models from scratch..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python main.py

if [ $? -ne 0 ]; then
    echo "❌ Model training failed!"
    exit 1
fi

echo ""
echo "✅ Models trained successfully"
echo ""

# Step 3: Verify models
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Verifying trained models..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "data/output/models" ]; then
    echo "📦 Trained models:"
    ls -lh data/output/models/*.pkl 2>/dev/null || echo "⚠️  No model files found"
    echo ""
else
    echo "❌ Models directory not found!"
    exit 1
fi

# Step 4: Analyze custom Terraform files
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Analyzing custom Terraform files..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Count .tf files
if [ -d "$CUSTOM_TF_PATH" ]; then
    TF_COUNT=$(find "$CUSTOM_TF_PATH" -name "*.tf" -type f | wc -l)
    echo "🔍 Found $TF_COUNT .tf files in $CUSTOM_TF_PATH"
else
    echo "📄 Analyzing single file: $CUSTOM_TF_PATH"
fi
echo ""

python analyze_custom_tf.py \
    --input "$CUSTOM_TF_PATH" \
    --output "$OUTPUT_DIR" \
    --verbose

if [ $? -ne 0 ]; then
    echo "❌ Analysis failed!"
    exit 1
fi

echo ""
echo "✅ Analysis completed successfully"
echo ""

# Step 5: Display results
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Results Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "$OUTPUT_DIR/analysis_summary.json" ]; then
    echo "📊 Analysis Summary:"
    echo ""
    python -m json.tool "$OUTPUT_DIR/analysis_summary.json"
    echo ""
else
    echo "⚠️  Summary file not found"
fi

# Final message
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Workflow Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Results saved to: $OUTPUT_DIR"
echo ""
echo "📄 Generated files:"
echo "   • $OUTPUT_DIR/analysis_results.csv"
echo "   • $OUTPUT_DIR/analysis_summary.json"
echo "   • $OUTPUT_DIR/analysis_report.md"
echo ""
echo "🔍 To view the report:"
echo "   cat $OUTPUT_DIR/analysis_report.md"
echo ""
echo "📊 To view detailed results:"
echo "   xdg-open $OUTPUT_DIR/analysis_results.csv"
echo ""
echo "💡 To add LLM explanations, run:"
echo "   python analyze_custom_tf.py --input $CUSTOM_TF_PATH --output $OUTPUT_DIR --explain"
echo ""
