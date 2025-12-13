"""
LLM Explainer Module for IaC Anomaly Detection

This module provides LLM-powered explanations for detected anomalies in 
Infrastructure as Code (Terraform) configurations.

Components:
- ollama_client: Interface to Ollama API
- prompt_templates: Structured prompts for anomaly explanation
- context_builder: Extract and format anomaly context
- explanation_generator: Main orchestrator for generating explanations
- report_builder: Generate enhanced reports with LLM insights
"""

__version__ = "1.0.0"
__all__ = [
    "OllamaClient",
    "ContextBuilder", 
    "ExplanationGenerator",
    "ReportBuilder"
]
