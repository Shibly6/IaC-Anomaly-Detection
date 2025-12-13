#!/usr/bin/env python3
"""
Example script demonstrating how to use the LLM Explainer module

This script shows how to:
1. Generate explanations for detected anomalies
2. Create reports
3. Use different models
"""

import logging
from rich.console import Console
from llm_explainer.explanation_generator import ExplanationGenerator
from llm_explainer.report_builder import ReportBuilder

# Setup
logging.basicConfig(level=logging.INFO)
console = Console()

def example_basic_usage():
    """Example 1: Basic usage - generate explanations for all anomalies"""
    console.print("[bold blue]Example 1: Basic Usage[/bold blue]\n")
    
    # Initialize generator
    generator = ExplanationGenerator(
        output_dir="data/output",
        model_name="deepseek-r1:1.5b"
    )
    
    # Generate explanations
    explanations = generator.explain_all_anomalies(min_score=0.5)
    
    # Save results
    generator.save_explanations(explanations)
    
    console.print(f"[green]Generated {len(explanations)} explanations[/green]\n")


def example_single_anomaly():
    """Example 2: Explain a single anomaly"""
    console.print("[bold blue]Example 2: Single Anomaly Explanation[/bold blue]\n")
    
    generator = ExplanationGenerator(output_dir="data/output")
    
    # Get first anomaly
    anomaly_indices = generator.context_builder.get_anomalies()
    if anomaly_indices:
        # Explain first anomaly
        explanation = generator.explain_anomaly(anomaly_indices[0])
        
        console.print(f"[cyan]Bucket:[/cyan] {explanation['context']['bucket_name']}")
        console.print(f"[cyan]Score:[/cyan] {explanation['context']['anomaly_score']:.3f}")
        console.print(f"\n[yellow]Explanation:[/yellow]")
        console.print(explanation['explanation'])
    else:
        console.print("[yellow]No anomalies found[/yellow]")
    
    console.print()


def example_with_reports():
    """Example 3: Generate explanations and create reports"""
    console.print("[bold blue]Example 3: Generate Reports[/bold blue]\n")
    
    # Generate explanations
    generator = ExplanationGenerator(output_dir="data/output")
    explanations = generator.explain_all_anomalies(min_score=0.6)
    
    if not explanations:
        console.print("[yellow]No anomalies to report[/yellow]")
        return
    
    # Generate executive summary
    anomaly_indices = [exp['index'] for exp in explanations]
    summary = generator.generate_executive_summary(anomaly_indices)
    
    # Create reports
    report_builder = ReportBuilder(output_dir="data/output/explanations")
    
    md_path = report_builder.generate_markdown_report(explanations, summary)
    html_path = report_builder.generate_html_report(explanations, summary)
    
    console.print(f"[green]Reports generated:[/green]")
    console.print(f"  Markdown: {md_path}")
    console.print(f"  HTML: {html_path}\n")


def example_different_models():
    """Example 4: Compare different models"""
    console.print("[bold blue]Example 4: Compare Models[/bold blue]\n")
    
    models = ["gemma3:1b", "deepseek-r1:1.5b"]
    
    for model in models:
        try:
            console.print(f"[cyan]Testing {model}...[/cyan]")
            generator = ExplanationGenerator(
                output_dir="data/output",
                model_name=model
            )
            
            # Get first anomaly
            anomaly_indices = generator.context_builder.get_anomalies()
            if anomaly_indices:
                explanation = generator.explain_anomaly(anomaly_indices[0])
                
                console.print(f"[green]✓ {model} works[/green]")
                console.print(f"  Response length: {len(explanation['explanation'])} chars")
                
                if 'metadata' in explanation:
                    eval_count = explanation['metadata'].get('eval_count', 0)
                    console.print(f"  Tokens generated: {eval_count}")
            
            console.print()
            
        except Exception as e:
            console.print(f"[red]✗ {model} failed: {e}[/red]\n")


def example_statistics():
    """Example 5: Get statistics"""
    console.print("[bold blue]Example 5: Statistics[/bold blue]\n")
    
    generator = ExplanationGenerator(output_dir="data/output")
    stats = generator.get_statistics()
    
    console.print(f"[cyan]Model:[/cyan] {stats['model']}")
    
    if 'anomalies' in stats:
        console.print(f"\n[cyan]Anomaly Statistics:[/cyan]")
        for key, value in stats['anomalies'].items():
            console.print(f"  {key}: {value}")
    
    if 'cache' in stats and stats['cache'].get('enabled'):
        console.print(f"\n[cyan]Cache Statistics:[/cyan]")
        console.print(f"  Cached items: {stats['cache']['cached_items']}")
        console.print(f"  Size: {stats['cache']['total_size_mb']:.2f} MB")
    
    console.print()


if __name__ == "__main__":
    console.print("[bold green]LLM Explainer Module - Usage Examples[/bold green]\n")
    
    try:
        # Run examples
        example_basic_usage()
        example_single_anomaly()
        example_with_reports()
        example_statistics()
        # example_different_models()  # Uncomment to test both models
        
        console.print("[bold green]✓ All examples completed successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
