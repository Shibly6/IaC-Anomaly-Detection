"""
Prompt Templates for Anomaly Explanation

This module contains structured prompts for generating explanations
for different types of IaC anomalies.
"""

from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates for anomaly explanation"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt that defines the LLM's role"""
        return """You are a cloud security expert specializing in Infrastructure as Code (IaC) security analysis. Your role is to explain security misconfigurations in Terraform code to developers in a clear, actionable way.

When explaining anomalies:
1. Be concise but thorough
2. Explain WHY the configuration is problematic
3. Describe the SECURITY IMPLICATIONS
4. Provide SPECIFIC remediation steps
5. Include corrected Terraform code examples
6. Reference relevant compliance frameworks (CIS, NIST, etc.) when applicable

Focus on helping developers understand and fix the issues, not just identifying them."""

    @staticmethod
    def get_public_access_prompt(context: Dict[str, Any]) -> str:
        """Prompt for public access misconfigurations"""
        bucket_name = context.get('bucket_name', 'unknown')
        acl = context.get('acl', 'unknown')
        score = context.get('anomaly_score', 0)
        has_encryption = context.get('encryption_enabled', 0)
        has_versioning = context.get('versioning_enabled', 0)
        has_logging = context.get('logging_enabled', 0)
        
        return f"""Analyze this S3 bucket configuration anomaly:

BUCKET: {bucket_name}
ACL: {acl}
ANOMALY SCORE: {score:.2f} (0=normal, 1=highly anomalous)

SECURITY FEATURES:
- Encryption: {'Enabled' if has_encryption else 'DISABLED'}
- Versioning: {'Enabled' if has_versioning else 'DISABLED'}  
- Logging: {'Enabled' if has_logging else 'DISABLED'}

Provide a security analysis with:
1. WHY this configuration is flagged (2-3 sentences)
2. SECURITY IMPLICATIONS (bullet points)
3. COMPLIANCE IMPACT (which standards are violated)
4. HOW TO FIX (step-by-step)
5. CORRECTED TERRAFORM CODE (complete resource block)

Keep the explanation under 300 words but be specific and actionable."""

    @staticmethod
    def get_security_gap_prompt(context: Dict[str, Any]) -> str:
        """Prompt for missing security features"""
        bucket_name = context.get('bucket_name', 'unknown')
        score = context.get('anomaly_score', 0)
        
        missing_features = []
        if not context.get('encryption_enabled', 0):
            missing_features.append('encryption')
        if not context.get('versioning_enabled', 0):
            missing_features.append('versioning')
        if not context.get('logging_enabled', 0):
            missing_features.append('access logging')
        if not context.get('secure_transport', 0):
            missing_features.append('secure transport enforcement')
        
        return f"""Analyze this S3 bucket with missing security features:

BUCKET: {bucket_name}
ANOMALY SCORE: {score:.2f}
MISSING FEATURES: {', '.join(missing_features)}

CURRENT CONFIGURATION:
- Encryption: {'Yes' if context.get('encryption_enabled') else 'No'}
- Versioning: {'Yes' if context.get('versioning_enabled') else 'No'}
- Logging: {'Yes' if context.get('logging_enabled') else 'No'}
- Secure Transport: {'Yes' if context.get('secure_transport') else 'No'}

Explain:
1. WHY these features are important for security
2. RISKS of not having them
3. COMPLIANCE requirements (CIS AWS Foundations, etc.)
4. HOW TO ADD these features (Terraform code)

Be concise but complete."""

    @staticmethod
    def get_general_anomaly_prompt(context: Dict[str, Any]) -> str:
        """General prompt for any anomaly type"""
        bucket_name = context.get('bucket_name', 'unknown')
        score = context.get('anomaly_score', 0)
        source_file = context.get('source_file', 'unknown')
        
        # Build feature summary
        features_summary = []
        for key, value in context.items():
            if key not in ['bucket_name', 'source_file', 'anomaly_score'] and isinstance(value, (int, float)):
                features_summary.append(f"- {key}: {value}")
        
        features_text = '\n'.join(features_summary[:10])  # Limit to top 10 features
        
        return f"""Analyze this Infrastructure as Code anomaly:

RESOURCE: {bucket_name}
SOURCE: {source_file}
ANOMALY SCORE: {score:.2f} (0=normal, 1=highly anomalous)

KEY FEATURES:
{features_text}

This configuration was flagged as anomalous by machine learning models. Provide:

1. ROOT CAUSE: What specific configuration choices likely triggered the anomaly detection? (2-3 sentences)

2. SECURITY ANALYSIS: What are the security implications? (bullet points)

3. BEST PRACTICES: What AWS/cloud security best practices are violated?

4. REMEDIATION: How to fix this? Provide:
   - Step-by-step instructions
   - Updated Terraform code
   - Verification steps

Keep it under 350 words but be specific and actionable."""

    @staticmethod
    def get_batch_summary_prompt(anomalies: list) -> str:
        """Prompt for summarizing multiple anomalies"""
        count = len(anomalies)
        
        # Group by severity
        critical = sum(1 for a in anomalies if a.get('anomaly_score', 0) >= 0.9)
        high = sum(1 for a in anomalies if 0.7 <= a.get('anomaly_score', 0) < 0.9)
        medium = sum(1 for a in anomalies if 0.5 <= a.get('anomaly_score', 0) < 0.7)
        
        return f"""Provide an executive summary of {count} detected IaC anomalies:

SEVERITY BREAKDOWN:
- Critical (score ≥ 0.9): {critical}
- High (score 0.7-0.9): {high}
- Medium (score 0.5-0.7): {medium}

Create a concise executive summary (150-200 words) covering:
1. OVERVIEW: What types of issues were found?
2. TOP RISKS: What are the most critical security concerns?
3. BUSINESS IMPACT: What could happen if these aren't fixed?
4. PRIORITY ACTIONS: What should be fixed first?
5. COMPLIANCE: Which compliance frameworks are affected?

Write for a technical manager audience."""

    @staticmethod
    def get_remediation_code_prompt(context: Dict[str, Any], original_code: str = None) -> str:
        """Prompt specifically for generating remediation code"""
        bucket_name = context.get('bucket_name', 'unknown')
        
        code_section = ""
        if original_code:
            code_section = f"\nORIGINAL TERRAFORM CODE:\n```hcl\n{original_code}\n```\n"
        
        return f"""Generate secure Terraform code to fix this S3 bucket configuration:

BUCKET: {bucket_name}
{code_section}
ISSUES IDENTIFIED:
- ACL: {context.get('acl', 'unknown')}
- Encryption: {'Missing' if not context.get('encryption_enabled') else 'Present'}
- Versioning: {'Missing' if not context.get('versioning_enabled') else 'Present'}
- Logging: {'Missing' if not context.get('logging_enabled') else 'Present'}

Generate ONLY the corrected Terraform code with:
1. Private ACL
2. Server-side encryption (AES256 or KMS)
3. Versioning enabled
4. Access logging configured
5. Public access blocks
6. Secure transport enforcement

Output ONLY valid HCL/Terraform code, no explanations."""


def get_prompt_for_anomaly(context: Dict[str, Any], prompt_type: str = "auto") -> str:
    """
    Get the appropriate prompt for an anomaly based on its characteristics
    
    Args:
        context: Dictionary with anomaly context (features, scores, etc.)
        prompt_type: Type of prompt ('auto', 'public_access', 'security_gap', 'general')
        
    Returns:
        Formatted prompt string
    """
    templates = PromptTemplates()
    
    if prompt_type == "auto":
        # Auto-detect the best prompt type
        acl = context.get('acl', '').lower()
        is_public = context.get('is_public_acl', 0) or context.get('has_public_policy', 0)
        
        if 'public' in acl or is_public:
            prompt_type = "public_access"
        else:
            # Check for missing security features
            missing_count = sum([
                not context.get('encryption_enabled', 0),
                not context.get('versioning_enabled', 0),
                not context.get('logging_enabled', 0)
            ])
            if missing_count >= 2:
                prompt_type = "security_gap"
            else:
                prompt_type = "general"
    
    # Get the appropriate prompt
    if prompt_type == "public_access":
        return templates.get_public_access_prompt(context)
    elif prompt_type == "security_gap":
        return templates.get_security_gap_prompt(context)
    else:
        return templates.get_general_anomaly_prompt(context)
