#!/usr/bin/env python3
"""
Analyze Custom Terraform Files

This script analyzes arbitrary Terraform (.tf) files using pre-trained anomaly detection models.
It can process single files or entire directories and generate detailed reports with LLM explanations.

Usage:
    python analyze_custom_tf.py --input /path/to/file.tf
    python analyze_custom_tf.py --input /path/to/directory/ --explain
    python analyze_custom_tf.py --input /path/to/file.tf --models isolation_forest,autoencoder
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.custom_analyzer import CustomTerraformAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("custom_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("custom_analyzer")
console = Console()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze custom Terraform files for security anomalies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single file
  python analyze_custom_tf.py --input /path/to/file.tf

  # Analyze a directory with LLM explanations
  python analyze_custom_tf.py --input /path/to/directory/ --explain

  # Use specific models only
  python analyze_custom_tf.py --input /path/to/file.tf --models isolation_forest,autoencoder

  # Custom output location and threshold
  python analyze_custom_tf.py --input /path/to/file.tf --output ./results/ --threshold 0.6
        """
    )

    parser.add_argument(
        "--input", "-i", type=str, required=True,
        help="Path to Terraform file or directory to analyze"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="data/output/custom_analysis",
        help="Directory to save analysis results (default: data/output/custom_analysis)"
    )
    parser.add_argument(
        "--models-dir", type=str, default="data/output",
        help="Directory containing trained models (default: data/output)"
    )
    parser.add_argument(
        "--models", type=str, default=None,
        help="Comma-separated list of models to use (default: all available)"
    )
    parser.add_argument(
        "--threshold", type=float, default=0.5,
        help="Anomaly score threshold for classification (default: 0.5)"
    )
    parser.add_argument(
        "--explain", action="store_true",
        help="Generate LLM-powered explanations for detected anomalies"
    )
    parser.add_argument(
        "--llm-model", type=str, default="deepseek-r1:1.5b",
        help="Ollama model to use for explanations (default: deepseek-r1:1.5b)"
    )
    parser.add_argument(
        "--min-anomaly-score", type=float, default=0.5,
        help="Minimum anomaly score for LLM explanation (default: 0.5)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def display_results_table(results_df, threshold=0.5):
    """Display analysis results in a formatted table."""
    table = Table(title="Anomaly Detection Results", show_header=True, header_style="bold magenta")

    table.add_column("Bucket Name", style="cyan")
    table.add_column("Source File", style="blue")
    table.add_column("Ensemble Score", justify="right", style="yellow")
    table.add_column("Status", justify="center")
    table.add_column("Public ACL", justify="center")
    table.add_column("Public Policy", justify="center")

    for _, row in results_df.iterrows():
        ensemble_score = row.get('ensemble_score', 0)
        is_anomaly = ensemble_score > threshold

        status = "🚨 ANOMALY" if is_anomaly else "✓ Normal"
        status_style = "bold red" if is_anomaly else "green"

        public_acl = "Yes" if row.get('is_public_acl', 0) == 1 else "No"
        public_policy = "Yes" if row.get('has_public_policy', 0) == 1 else "No"

        table.add_row(
            row.get('bucket_name', 'unknown'),
            str(Path(row.get('source_file', 'unknown')).name),
            f"{ensemble_score:.3f}",
            f"[{status_style}]{status}[/{status_style}]",
            public_acl,
            public_policy
        )

    console.print(table)


def save_results(results_df, summary, output_dir):
    """Save analysis results to files."""
    os.makedirs(output_dir, exist_ok=True)

    # Save detailed results as CSV
    csv_path = os.path.join(output_dir, "analysis_results.csv")
    results_df.to_csv(csv_path, index=False)
    console.print(f"[green]✓ Saved detailed results to {csv_path}[/green]")

    # Save summary as JSON
    json_path = os.path.join(output_dir, "analysis_summary.json")
    with open(json_path, 'w') as f:
        json.dump(summary, indent=2, fp=f)
    console.print(f"[green]✓ Saved summary to {json_path}[/green]")

    # Generate Markdown report
    md_path = os.path.join(output_dir, "analysis_report.md")
    generate_markdown_report(results_df, summary, md_path)
    console.print(f"[green]✓ Saved report to {md_path}[/green]")


def generate_markdown_report(results_df, summary, output_path):
    """Generate a Markdown report of the analysis."""
    with open(output_path, 'w') as f:
        f.write("# Terraform Security Analysis Report\n\n")

        # Summary section
        f.write("## Summary\n\n")
        f.write(f"- **Total Configurations Analyzed**: {summary['total_configurations']}\n")
        f.write(f"- **Anomalies Detected**: {summary['anomalies_detected']}\n")
        f.write(f"- **Anomaly Rate**: {summary['anomaly_rate']:.1%}\n")
        f.write(f"- **Average Ensemble Score**: {summary['average_ensemble_score']:.3f}\n")
        f.write(f"- **Models Used**: {', '.join(summary['models_used'])}\n\n")

        # High-risk configurations
        if summary['high_risk_configs']:
            f.write("## High-Risk Configurations\n\n")
            f.write("The following configurations have high anomaly scores (>0.7):\n\n")

            for config in summary['high_risk_configs']:
                f.write(f"### {config['bucket_name']}\n\n")
                f.write(f"- **Source File**: `{config['source_file']}`\n")
                f.write(f"- **Ensemble Score**: {config['ensemble_score']:.3f}\n")
                f.write(f"- **Public ACL**: {'Yes' if config['is_public_acl'] else 'No'}\n")
                f.write(f"- **Public Policy**: {'Yes' if config['has_public_policy'] else 'No'}\n\n")

        # Detailed results
        f.write("## Detailed Results\n\n")
        f.write("| Bucket Name | Source File | Ensemble Score | Status | Public ACL | Public Policy |\n")
        f.write("|-------------|-------------|----------------|--------|------------|---------------|\n")

        for _, row in results_df.iterrows():
            ensemble_score = row.get('ensemble_score', 0)
            is_anomaly = ensemble_score > 0.5
            status = "🚨 ANOMALY" if is_anomaly else "✓ Normal"
            public_acl = "Yes" if row.get('is_public_acl', 0) == 1 else "No"
            public_policy = "Yes" if row.get('has_public_policy', 0) == 1 else "No"

            f.write(f"| {row.get('bucket_name', 'unknown')} | ")
            f.write(f"`{Path(row.get('source_file', 'unknown')).name}` | ")
            f.write(f"{ensemble_score:.3f} | {status} | {public_acl} | {public_policy} |\n")


def generate_llm_explanations(results_df, output_dir, llm_model, min_score):
    """Generate LLM explanations for detected anomalies."""
    try:
        from llm_explainer.explanation_generator import ExplanationGenerator
        from llm_explainer.report_builder import ReportBuilder

        console.print("[cyan]Generating LLM explanations...[/cyan]")

        # Filter anomalies above threshold
        anomalies = results_df[results_df['ensemble_score'] >= min_score]

        if len(anomalies) == 0:
            console.print("[yellow]No anomalies above threshold for explanation[/yellow]")
            return

        # Create temporary directory structure for explanation generator
        temp_output_dir = os.path.join(output_dir, "temp")
        temp_features_dir = os.path.join(temp_output_dir, "features")
        os.makedirs(temp_features_dir, exist_ok=True)

        # Save features and results for explanation generator
        results_df.to_csv(os.path.join(temp_features_dir, "raw_features.csv"), index=False)

        # Initialize generator (disable caching to avoid JSON serialization issues)
        generator = ExplanationGenerator(
            output_dir=temp_output_dir,
            model_name=llm_model,
            use_cache=False
        )

        explanations = []
        for idx, row in anomalies.iterrows():
            try:
                # ExplanationGenerator builds its own context from the index
                explanation = generator.explain_anomaly(idx, model_name='ensemble', include_code=True)
                if explanation and 'error' not in explanation:
                    explanations.append(explanation)
                elif 'error' in explanation:
                    logger.error(f"Error in explanation for index {idx}: {explanation['error']}")

            except Exception as e:
                logger.error(f"Error generating explanation for index {idx}: {str(e)}")

        if explanations:
            # Build reports
            report_builder = ReportBuilder(output_dir=os.path.join(output_dir, "explanations"))
            summary = f"Analyzed {len(results_df)} configurations, found {len(anomalies)} anomalies"
            report_builder.generate_markdown_report(explanations, summary)
            report_builder.generate_html_report(explanations, summary)

            console.print(f"[green]✓ Generated {len(explanations)} LLM explanations[/green]")
            console.print(f"[green]✓ Explanation reports saved to {output_dir}/explanations/[/green]")

    except ImportError as e:
        console.print(f"[red]✗ LLM explainer module not available: {str(e)}[/red]")
    except ConnectionError as e:
        console.print(f"[red]✗ Cannot connect to Ollama: {str(e)}[/red]")
        console.print("[yellow]Make sure Ollama is running: ollama serve[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error generating explanations: {str(e)}[/red]")
        logger.error(f"LLM explanation failed: {str(e)}")


def main():
    """Main function."""
    console.print(Panel(
        "[bold blue]Custom Terraform File Analyzer[/bold blue]\n"
        "Detect Security Anomalies in Your Infrastructure Code",
        style="blue"
    ))

    # Parse arguments
    args = parse_arguments()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input path
    if not os.path.exists(args.input):
        console.print(f"[red]✗ Input path does not exist: {args.input}[/red]")
        sys.exit(1)

    # Parse model names
    model_names = None
    if args.models:
        model_names = [m.strip() for m in args.models.split(',')]
        console.print(f"[cyan]Using models: {', '.join(model_names)}[/cyan]")

    try:
        # Initialize analyzer
        console.print("[cyan]Loading pre-trained models...[/cyan]")
        analyzer = CustomTerraformAnalyzer(models_dir=args.models_dir)

        if not analyzer.load_models(model_names):
            console.print("[red]✗ Failed to load models. Have you trained the models yet?[/red]")
            console.print("[yellow]Run: python main.py[/yellow]")
            sys.exit(1)

        console.print("[green]✓ Models loaded successfully[/green]")

        # Analyze files
        console.print(f"[cyan]Analyzing: {args.input}[/cyan]")
        results_df = analyzer.analyze(args.input)

        if results_df is None or len(results_df) == 0:
            console.print("[yellow]No results to display[/yellow]")
            sys.exit(0)

        # Get summary
        summary = analyzer.get_summary(results_df)

        # Display results
        console.print("\n")
        display_results_table(results_df, threshold=args.threshold)

        # Print summary
        console.print(f"\n[bold]Analysis Summary:[/bold]")
        console.print(f"  • Total configurations: {summary['total_configurations']}")
        console.print(f"  • Anomalies detected: {summary['anomalies_detected']}")
        console.print(f"  • Anomaly rate: {summary['anomaly_rate']:.1%}")
        console.print(f"  • Average score: {summary['average_ensemble_score']:.3f}")

        # Save results
        console.print(f"\n[cyan]Saving results to {args.output}...[/cyan]")
        save_results(results_df, summary, args.output)

        # Generate LLM explanations if requested
        if args.explain:
            generate_llm_explanations(
                results_df,
                args.output,
                args.llm_model,
                args.min_anomaly_score
            )

        # Final message
        console.print(Panel(
            f"[bold green]Analysis Complete![/bold green]\n\n"
            f"Results saved to: {args.output}\n"
            f"Check the output directory for:\n"
            f"  • Detailed results: analysis_results.csv\n"
            f"  • Summary: analysis_summary.json\n"
            f"  • Report: analysis_report.md" +
            (f"\n  • LLM explanations: explanations/" if args.explain else ""),
            style="green"
        ))

    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Analysis failed: {str(e)}[/red]")
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
