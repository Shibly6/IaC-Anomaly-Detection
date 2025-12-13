"""
Explanation Generator - Main orchestrator for generating LLM-powered explanations

This module coordinates the entire explanation generation process.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .ollama_client import OllamaClient
from .context_builder import ContextBuilder
from .prompt_templates import get_prompt_for_anomaly, PromptTemplates
from .cache import ExplanationCache
from . import config

logger = logging.getLogger("anomaly_detector.llm_explainer")
console = Console()


class ExplanationGenerator:
    """Generate explanations for detected anomalies using LLM"""
    
    def __init__(
        self,
        output_dir: str = "data/output",
        model_name: str = None,
        use_cache: bool = True
    ):
        """
        Initialize explanation generator
        
        Args:
            output_dir: Directory containing anomaly detection outputs
            model_name: Ollama model to use (default: from config)
            use_cache: Whether to use caching
        """
        self.output_dir = output_dir
        self.model_name = model_name or config.DEFAULT_MODEL
        
        # Initialize components
        self.llm_client = OllamaClient(model_name=self.model_name)
        self.context_builder = ContextBuilder(output_dir=output_dir)
        self.cache = ExplanationCache() if use_cache else None
        
        # Create output directory
        self.explanations_dir = os.path.join(output_dir, "explanations")
        os.makedirs(self.explanations_dir, exist_ok=True)
        
        logger.info(f"Initialized ExplanationGenerator with model: {self.model_name}")
    
    def explain_anomaly(
        self,
        index: int,
        model_name: str = 'ensemble',
        include_code: bool = True
    ) -> Dict[str, Any]:
        """
        Generate explanation for a single anomaly
        
        Args:
            index: Index of the anomaly
            model_name: Which model's scores to use
            include_code: Whether to include remediation code
            
        Returns:
            Dictionary with explanation and metadata
        """
        # Build context
        context = self.context_builder.build_context(index, model_name)
        
        if not context:
            logger.error(f"Could not build context for index {index}")
            return {}
        
        # Generate prompt
        prompt = get_prompt_for_anomaly(context, prompt_type="auto")
        
        # Check cache
        if self.cache:
            cached_explanation = self.cache.get(context, prompt)
            if cached_explanation:
                return {
                    'index': index,
                    'context': context,
                    'explanation': cached_explanation,
                    'from_cache': True
                }
        
        # Generate explanation
        try:
            result = self.llm_client.generate(prompt)
            explanation = result['response']
            
            # Cache the result
            if self.cache:
                self.cache.set(context, prompt, explanation)
            
            # Optionally generate remediation code
            remediation_code = None
            if include_code:
                remediation_code = self._generate_remediation_code(context)
            
            return {
                'index': index,
                'context': context,
                'explanation': explanation,
                'remediation_code': remediation_code,
                'metadata': result.get('metadata', {}),
                'from_cache': False
            }
            
        except Exception as e:
            logger.error(f"Error generating explanation for index {index}: {e}")
            return {
                'index': index,
                'context': context,
                'error': str(e)
            }
    
    def _generate_remediation_code(self, context: Dict[str, Any]) -> Optional[str]:
        """Generate remediation Terraform code"""
        try:
            templates = PromptTemplates()
            code_prompt = templates.get_remediation_code_prompt(context)
            
            result = self.llm_client.generate(code_prompt, temperature=0.3)
            code = result['response']
            
            # Extract code block if wrapped in markdown
            if '```' in code:
                # Find HCL/Terraform code block
                parts = code.split('```')
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Odd indices are code blocks
                        # Remove language identifier if present
                        lines = part.strip().split('\n')
                        if lines[0].lower() in ['hcl', 'terraform', 'tf']:
                            return '\n'.join(lines[1:])
                        return part.strip()
            
            return code.strip()
            
        except Exception as e:
            logger.warning(f"Could not generate remediation code: {e}")
            return None
    
    def explain_all_anomalies(
        self,
        model_name: str = 'ensemble',
        min_score: float = 0.5,
        max_anomalies: int = None
    ) -> List[Dict[str, Any]]:
        """
        Generate explanations for all detected anomalies
        
        Args:
            model_name: Which model's predictions to use
            min_score: Minimum anomaly score threshold
            max_anomalies: Maximum number of anomalies to explain (None = all)
            
        Returns:
            List of explanation dictionaries
        """
        # Get anomaly indices
        anomaly_indices = self.context_builder.get_anomalies(model_name, min_score)
        
        if not anomaly_indices:
            console.print("[yellow]No anomalies found to explain[/yellow]")
            return []
        
        # Limit if requested
        if max_anomalies and len(anomaly_indices) > max_anomalies:
            console.print(f"[yellow]Limiting to top {max_anomalies} anomalies[/yellow]")
            # Sort by score and take top N
            contexts = self.context_builder.get_batch_context(anomaly_indices, model_name)
            sorted_indices = sorted(
                range(len(contexts)),
                key=lambda i: contexts[i].get('anomaly_score', 0),
                reverse=True
            )
            anomaly_indices = [anomaly_indices[i] for i in sorted_indices[:max_anomalies]]
        
        console.print(f"[cyan]Generating explanations for {len(anomaly_indices)} anomalies...[/cyan]")
        
        explanations = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task(
                "[cyan]Explaining anomalies...",
                total=len(anomaly_indices)
            )
            
            for i, idx in enumerate(anomaly_indices, 1):
                progress.update(task, description=f"[cyan]Processing anomaly {i}/{len(anomaly_indices)} (index {idx})...")
                explanation = self.explain_anomaly(idx, model_name)
                explanations.append(explanation)
                progress.update(task, advance=1)
        
        return explanations
    
    def generate_executive_summary(
        self,
        anomaly_indices: List[int],
        model_name: str = 'ensemble'
    ) -> str:
        """
        Generate executive summary for multiple anomalies
        
        Args:
            anomaly_indices: List of anomaly indices
            model_name: Which model's scores to use
            
        Returns:
            Executive summary text
        """
        if not anomaly_indices:
            return "No anomalies detected."
        
        # Get contexts for all anomalies
        contexts = self.context_builder.get_batch_context(anomaly_indices, model_name)
        
        # Generate summary prompt
        templates = PromptTemplates()
        prompt = templates.get_batch_summary_prompt(contexts)
        
        try:
            result = self.llm_client.generate(prompt)
            return result['response']
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def save_explanations(
        self,
        explanations: List[Dict[str, Any]],
        filename: str = "anomaly_explanations.json"
    ):
        """
        Save explanations to JSON file
        
        Args:
            explanations: List of explanation dictionaries
            filename: Output filename
        """
        output_path = os.path.join(self.explanations_dir, filename)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(explanations, f, indent=2, default=str)
            
            console.print(f"[green]Saved explanations to {output_path}[/green]")
            logger.info(f"Saved {len(explanations)} explanations to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving explanations: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the explanation generation"""
        stats = {
            'model': self.model_name,
            'output_dir': self.output_dir
        }
        
        # Add cache stats if available
        if self.cache:
            stats['cache'] = self.cache.get_stats()
        
        # Add anomaly stats
        anomaly_indices = self.context_builder.get_anomalies()
        if anomaly_indices:
            stats['anomalies'] = self.context_builder.get_summary_stats(anomaly_indices)
        
        return stats


def main(
    output_dir: str = "data/output",
    model_name: str = None,
    min_score: float = 0.5,
    max_anomalies: int = None
):
    """
    Main function to generate explanations
    
    Args:
        output_dir: Directory containing anomaly detection outputs
        model_name: Ollama model to use
        min_score: Minimum anomaly score threshold
        max_anomalies: Maximum number of anomalies to explain
    """
    console.print("[bold blue]LLM-Powered Anomaly Explanation Generator[/bold blue]\n")
    
    try:
        # Initialize generator
        generator = ExplanationGenerator(
            output_dir=output_dir,
            model_name=model_name
        )
        
        # Get statistics
        stats = generator.get_statistics()
        console.print(f"[cyan]Using model: {stats['model']}[/cyan]")
        
        if 'anomalies' in stats:
            console.print(f"[cyan]Total anomalies: {stats['anomalies']['total_anomalies']}[/cyan]")
            console.print(f"[cyan]Severity distribution: {stats['anomalies']['severity_distribution']}[/cyan]")
        
        # Generate explanations
        explanations = generator.explain_all_anomalies(
            min_score=min_score,
            max_anomalies=max_anomalies
        )
        
        if not explanations:
            console.print("[yellow]No anomalies to explain[/yellow]")
            return
        
        # Save explanations
        generator.save_explanations(explanations)
        
        # Generate executive summary
        console.print("\n[cyan]Generating executive summary...[/cyan]")
        anomaly_indices = [exp['index'] for exp in explanations]
        summary = generator.generate_executive_summary(anomaly_indices)
        
        # Save summary
        summary_path = os.path.join(generator.explanations_dir, "executive_summary.txt")
        with open(summary_path, 'w') as f:
            f.write(summary)
        console.print(f"[green]Saved executive summary to {summary_path}[/green]")
        
        # Print summary
        console.print("\n[bold]Executive Summary:[/bold]")
        console.print(summary)
        
        console.print(f"\n[green]✓ Generated {len(explanations)} explanations[/green]")
        
        # Show cache stats
        if generator.cache:
            cache_stats = generator.cache.get_stats()
            if cache_stats.get('enabled'):
                console.print(f"[cyan]Cache: {cache_stats['cached_items']} items, "
                            f"{cache_stats['total_size_mb']:.2f} MB[/cyan]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Explanation generation failed: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate LLM explanations for anomalies")
    parser.add_argument("--output-dir", default="data/output", help="Output directory")
    parser.add_argument("--model", help="Ollama model name")
    parser.add_argument("--min-score", type=float, default=0.5, help="Minimum anomaly score")
    parser.add_argument("--max-anomalies", type=int, help="Maximum anomalies to explain")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    main(
        output_dir=args.output_dir,
        model_name=args.model,
        min_score=args.min_score,
        max_anomalies=args.max_anomalies
    )
