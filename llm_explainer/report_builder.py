"""
Report Builder - Generate enhanced reports with LLM insights

Creates markdown and HTML reports with anomaly explanations.
"""

import os
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("anomaly_detector.llm_explainer")


class ReportBuilder:
    """Build comprehensive reports with LLM explanations"""
    
    def __init__(self, output_dir: str = "data/output/explanations"):
        """
        Initialize report builder
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_markdown_report(
        self,
        explanations: List[Dict[str, Any]],
        executive_summary: str = None,
        filename: str = "detailed_report.md"
    ) -> str:
        """
        Generate detailed markdown report
        
        Args:
            explanations: List of explanation dictionaries
            executive_summary: Optional executive summary
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w') as f:
            # Header
            f.write("# IaC Anomaly Detection Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Anomalies:** {len(explanations)}\n\n")
            f.write("---\n\n")
            
            # Executive Summary
            if executive_summary:
                f.write("## Executive Summary\n\n")
                f.write(executive_summary)
                f.write("\n\n---\n\n")
            
            # Severity Distribution
            severity_counts = self._count_by_severity(explanations)
            f.write("## Severity Distribution\n\n")
            for severity, count in sorted(severity_counts.items(), 
                                         key=lambda x: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].index(x[0]) 
                                         if x[0] in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] else 999):
                emoji = self._get_severity_emoji(severity)
                f.write(f"- {emoji} **{severity}**: {count}\n")
            f.write("\n---\n\n")
            
            # Detailed Findings
            f.write("## Detailed Findings\n\n")
            
            for i, exp in enumerate(explanations, 1):
                context = exp.get('context', {})
                explanation = exp.get('explanation', 'No explanation available')
                remediation_code = exp.get('remediation_code')
                
                severity = context.get('severity', 'UNKNOWN')
                bucket_name = context.get('bucket_name', 'unknown')
                score = context.get('anomaly_score', 0)
                
                emoji = self._get_severity_emoji(severity)
                
                f.write(f"### {emoji} Finding #{i}: {bucket_name}\n\n")
                f.write(f"**Severity:** {severity}  \n")
                f.write(f"**Anomaly Score:** {score:.3f}  \n")
                f.write(f"**Source:** `{context.get('source_file', 'unknown')}`\n\n")
                
                # Configuration Details
                f.write("**Configuration:**\n")
                f.write(f"- ACL: `{context.get('acl', 'unknown')}`\n")
                f.write(f"- Encryption: {'✓ Enabled' if context.get('encryption_enabled') else '✗ Disabled'}\n")
                f.write(f"- Versioning: {'✓ Enabled' if context.get('versioning_enabled') else '✗ Disabled'}\n")
                f.write(f"- Logging: {'✓ Enabled' if context.get('logging_enabled') else '✗ Disabled'}\n")
                f.write("\n")
                
                # LLM Explanation
                f.write("**Analysis:**\n\n")
                f.write(explanation)
                f.write("\n\n")
                
                # Remediation Code
                if remediation_code:
                    f.write("**Remediation Code:**\n\n")
                    f.write("```hcl\n")
                    f.write(remediation_code)
                    f.write("\n```\n\n")
                
                f.write("---\n\n")
        
        logger.info(f"Generated markdown report: {output_path}")
        return output_path
    
    def generate_html_report(
        self,
        explanations: List[Dict[str, Any]],
        executive_summary: str = None,
        filename: str = "detailed_report.html"
    ) -> str:
        """
        Generate HTML report with styling
        
        Args:
            explanations: List of explanation dictionaries
            executive_summary: Optional executive summary
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w') as f:
            # HTML Header with CSS
            f.write(self._get_html_header())
            
            # Title
            f.write('<div class="container">\n')
            f.write('<h1>🔍 IaC Anomaly Detection Report</h1>\n')
            f.write(f'<p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>\n')
            
            # Summary Stats
            f.write('<div class="summary-box">\n')
            f.write(f'<h2>Summary</h2>\n')
            f.write(f'<p><strong>Total Anomalies:</strong> {len(explanations)}</p>\n')
            
            severity_counts = self._count_by_severity(explanations)
            f.write('<div class="severity-grid">\n')
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    f.write(f'<div class="severity-badge severity-{severity.lower()}">\n')
                    f.write(f'<div class="severity-label">{severity}</div>\n')
                    f.write(f'<div class="severity-count">{count}</div>\n')
                    f.write('</div>\n')
            f.write('</div>\n')
            f.write('</div>\n')
            
            # Executive Summary
            if executive_summary:
                f.write('<div class="executive-summary">\n')
                f.write('<h2>📊 Executive Summary</h2>\n')
                f.write(f'<p>{executive_summary.replace(chr(10), "</p><p>")}</p>\n')
                f.write('</div>\n')
            
            # Detailed Findings
            f.write('<h2>📋 Detailed Findings</h2>\n')
            
            for i, exp in enumerate(explanations, 1):
                context = exp.get('context', {})
                explanation = exp.get('explanation', 'No explanation available')
                remediation_code = exp.get('remediation_code')
                
                severity = context.get('severity', 'UNKNOWN')
                bucket_name = context.get('bucket_name', 'unknown')
                score = context.get('anomaly_score', 0)
                
                f.write(f'<div class="finding finding-{severity.lower()}">\n')
                f.write(f'<h3>Finding #{i}: {bucket_name}</h3>\n')
                
                f.write('<div class="finding-header">\n')
                f.write(f'<span class="badge badge-{severity.lower()}">{severity}</span>\n')
                f.write(f'<span class="score">Score: {score:.3f}</span>\n')
                f.write('</div>\n')
                
                # Configuration table
                f.write('<table class="config-table">\n')
                f.write('<tr><th>Property</th><th>Value</th></tr>\n')
                f.write(f'<tr><td>Source File</td><td><code>{context.get("source_file", "unknown")}</code></td></tr>\n')
                f.write(f'<tr><td>ACL</td><td><code>{context.get("acl", "unknown")}</code></td></tr>\n')
                f.write(f'<tr><td>Encryption</td><td>{"✓ Enabled" if context.get("encryption_enabled") else "✗ Disabled"}</td></tr>\n')
                f.write(f'<tr><td>Versioning</td><td>{"✓ Enabled" if context.get("versioning_enabled") else "✗ Disabled"}</td></tr>\n')
                f.write(f'<tr><td>Logging</td><td>{"✓ Enabled" if context.get("logging_enabled") else "✗ Disabled"}</td></tr>\n')
                f.write('</table>\n')
                
                # Explanation
                f.write('<div class="explanation">\n')
                f.write('<h4>🔍 Analysis</h4>\n')
                f.write(f'<p>{explanation.replace(chr(10), "</p><p>")}</p>\n')
                f.write('</div>\n')
                
                # Remediation code
                if remediation_code:
                    f.write('<div class="remediation">\n')
                    f.write('<h4>🔧 Remediation Code</h4>\n')
                    f.write('<pre><code class="language-hcl">')
                    f.write(remediation_code)
                    f.write('</code></pre>\n')
                    f.write('</div>\n')
                
                f.write('</div>\n')  # Close finding
            
            f.write('</div>\n')  # Close container
            f.write('</body></html>\n')
        
        logger.info(f"Generated HTML report: {output_path}")
        return output_path
    
    def _count_by_severity(self, explanations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count anomalies by severity"""
        counts = {}
        for exp in explanations:
            severity = exp.get('context', {}).get('severity', 'UNKNOWN')
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity level"""
        emojis = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢',
            'INFO': 'ℹ️'
        }
        return emojis.get(severity, '⚪')
    
    def _get_html_header(self) -> str:
        """Get HTML header with embedded CSS"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IaC Anomaly Detection Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        h4 {
            color: #555;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        .timestamp {
            color: #7f8c8d;
            margin-bottom: 30px;
        }
        .summary-box {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .severity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .severity-badge {
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }
        .severity-critical { background: #e74c3c; color: white; }
        .severity-high { background: #e67e22; color: white; }
        .severity-medium { background: #f39c12; color: white; }
        .severity-low { background: #27ae60; color: white; }
        .severity-label {
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .severity-count {
            font-size: 2em;
        }
        .executive-summary {
            background: #d5e8f7;
            padding: 20px;
            border-left: 4px solid #3498db;
            margin-bottom: 30px;
            border-radius: 4px;
        }
        .finding {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .finding-critical { border-left: 5px solid #e74c3c; }
        .finding-high { border-left: 5px solid #e67e22; }
        .finding-medium { border-left: 5px solid #f39c12; }
        .finding-low { border-left: 5px solid #27ae60; }
        .finding-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
        }
        .badge-critical { background: #e74c3c; }
        .badge-high { background: #e67e22; }
        .badge-medium { background: #f39c12; }
        .badge-low { background: #27ae60; }
        .score {
            background: #34495e;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
        }
        .config-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .config-table th, .config-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .config-table th {
            background: #34495e;
            color: white;
            font-weight: bold;
        }
        .config-table tr:hover {
            background: #f8f9fa;
        }
        .explanation {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        .remediation {
            background: #e8f5e9;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
        }
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            margin-top: 10px;
        }
        code {
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
'''


if __name__ == "__main__":
    # Test report generation
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    # Load sample explanations
    explanations_file = "data/output/explanations/anomaly_explanations.json"
    if os.path.exists(explanations_file):
        with open(explanations_file, 'r') as f:
            explanations = json.load(f)
        
        builder = ReportBuilder()
        
        # Generate reports
        md_path = builder.generate_markdown_report(explanations)
        html_path = builder.generate_html_report(explanations)
        
        print(f"Generated reports:")
        print(f"  Markdown: {md_path}")
        print(f"  HTML: {html_path}")
    else:
        print(f"No explanations found at {explanations_file}")
