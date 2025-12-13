#!/bin/bash
# Quick Test: Verify the custom analyzer works with your existing training data

echo "=========================================="
echo "Testing Custom Terraform File Analyzer"
echo "=========================================="
echo ""

# Test 1: Analyze the training data as "custom" files
echo "Test 1: Analyzing training data/terraform/misconfig/ as custom files..."
python analyze_custom_tf.py \
    --input data/terraform/misconfig/ \
    --output ./test_analysis/ \
    --verbose

echo ""
echo "✓ Test 1 complete. Check ./test_analysis/ for results."
echo ""

# Test 2: Show what was found
echo "Test 2: Displaying summary..."
if [ -f ./test_analysis/analysis_summary.json ]; then
    cat ./test_analysis/analysis_summary.json | python -m json.tool
else
    echo "Summary file not found. Check if models are trained."
fi

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review results in ./test_analysis/"
echo "2. Try with your own .tf files:"
echo "   python analyze_custom_tf.py --input /your/terraform/folder/"
echo ""
