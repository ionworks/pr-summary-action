"""Different prompt variations for testing PR summarization."""

from typing import Dict, Any


def get_prompt_variations() -> Dict[str, str]:
    """Get different prompt variations for testing."""
    return {
        "default": get_default_prompt(),
        "concise": get_concise_prompt(),
        "detailed": get_detailed_prompt(),
        "user_focused": get_user_focused_prompt(),
        "technical_focused": get_technical_focused_prompt(),
        "structured": get_structured_prompt(),
        "conversational": get_conversational_prompt(),
        "bullet_points": get_bullet_points_prompt(),
    }


def get_default_prompt() -> str:
    """Original prompt from the current system."""
    return """You are a technical writer creating PR summaries. 

Analyze this pull request and create two summaries:

PR DETAILS:
Title: {title}
Description: {body}
Diff (first {max_diff_length} chars): {diff_excerpt}

INSTRUCTIONS:
- Create a "technical" summary (2-3 sentences describing what changed technically)
- Create a "marketing" summary (1-2 sentences describing user benefits, or "Minor technical improvements" for basic fixes)
- Do not mention author names in the summaries
- Respond with ONLY a valid JSON object, no other text
- Use this exact format: {{"technical": "your technical summary", "marketing": "your marketing summary"}}

JSON Response:"""


def get_concise_prompt() -> str:
    """Shorter, more direct prompt."""
    return """Analyze this PR and create two brief summaries:

PR: {title}
Description: {body}
Changes: {diff_excerpt}

Create:
1. Technical summary: What changed (1-2 sentences)
2. Marketing summary: User benefit (1 sentence)

Return only JSON: {{"technical": "...", "marketing": "..."}}"""


def get_detailed_prompt() -> str:
    """More detailed prompt with specific guidance."""
    return """You are an expert technical writer specializing in software development communication.

TASK: Create professional summaries for this pull request that will be shared with both technical and business stakeholders.

PR INFORMATION:
Title: {title}
Description: {body}
Code Changes: {diff_excerpt}

REQUIREMENTS:

Technical Summary:
- 2-3 sentences maximum
- Focus on WHAT changed (files, functions, logic)
- Include technical details like APIs, algorithms, or architecture changes
- Use precise technical language
- Avoid implementation details that don't affect functionality

Marketing Summary:
- 1-2 sentences maximum
- Focus on WHY it matters to users/business
- Highlight user-facing benefits, performance improvements, or problem solutions
- Use accessible language that non-technical stakeholders can understand
- If no clear user benefit, use "Technical improvements and maintenance"

OUTPUT FORMAT:
Respond with ONLY valid JSON, no additional text or explanation.
Format: {{"technical": "your technical summary", "marketing": "your marketing summary"}}

JSON Response:"""


def get_user_focused_prompt() -> str:
    """Prompt that emphasizes user benefits."""
    return """Create summaries for this PR focusing on user impact:

PR: {title}
Details: {body}
Changes: {diff_excerpt}

For each summary, think about:
- Technical: What systems/components were modified?
- Marketing: How does this improve the user experience?

Create concise summaries that emphasize user benefits and business value.

Return JSON: {{"technical": "...", "marketing": "..."}}"""


def get_technical_focused_prompt() -> str:
    """Prompt that emphasizes technical accuracy."""
    return """As a senior software engineer, analyze this PR with technical precision:

PR: {title}
Description: {body}
Diff: {diff_excerpt}

Technical Summary Requirements:
- Identify specific components/modules affected
- Mention architectural patterns or design changes
- Include performance implications if evident
- Use exact technical terminology

Marketing Summary Requirements:
- Translate technical changes into business value
- Focus on measurable improvements
- Keep it factual and specific

Output JSON only: {{"technical": "...", "marketing": "..."}}"""


def get_structured_prompt() -> str:
    """Prompt with clear structure and formatting."""
    return """PULL REQUEST ANALYSIS

INPUT:
- Title: {title}
- Description: {body}
- Code Changes: {diff_excerpt}

OUTPUT REQUIREMENTS:

Technical Summary:
□ What was changed (files, functions, logic)
□ How it was implemented
□ Technical impact/scope
□ 2-3 sentences maximum

Marketing Summary:
□ User-facing benefits
□ Business value
□ Problem solved
□ 1-2 sentences maximum

RESPONSE FORMAT:
{{"technical": "your technical summary", "marketing": "your marketing summary"}}

Response:"""


def get_conversational_prompt() -> str:
    """More conversational, natural language prompt."""
    return """Hey! I need you to help me explain this pull request to different audiences.

Here's what happened:
- PR Title: {title}
- What they said: {body}
- What actually changed: {diff_excerpt}

Can you help me write two explanations?

1. For the tech team - what exactly changed in the code?
2. For everyone else - why should they care?

Keep it short and sweet. Just give me back:
{{"technical": "explanation for developers", "marketing": "explanation for everyone else"}}"""


def get_bullet_points_prompt() -> str:
    """Prompt that requests bullet point format."""
    return """Summarize this PR in bullet points:

PR: {title}
Description: {body}
Changes: {diff_excerpt}

Technical Summary (bullet points):
• What files/components were modified
• What functionality was added/changed
• Any architectural or design changes

Marketing Summary (bullet points):
• User benefits or improvements
• Business value
• Problem solved

Convert to JSON format: {{"technical": "• point 1 • point 2 • point 3", "marketing": "• benefit 1 • benefit 2"}}"""


def format_prompt(
    prompt_template: str,
    pr_data: Dict[str, Any],
    diff_excerpt: str,
    max_diff_length: int,
) -> str:
    """Format a prompt template with PR data."""
    return prompt_template.format(
        title=pr_data["title"],
        body=pr_data.get("body", ""),
        diff_excerpt=diff_excerpt,
        max_diff_length=max_diff_length,
    )


def get_prompt_metadata() -> Dict[str, Dict[str, Any]]:
    """Get metadata about each prompt variation."""
    return {
        "default": {
            "description": "Original prompt from current system",
            "focus": "balanced",
            "style": "formal",
            "length": "medium",
        },
        "concise": {
            "description": "Shorter, more direct approach",
            "focus": "brevity",
            "style": "minimal",
            "length": "short",
        },
        "detailed": {
            "description": "Comprehensive with specific guidance",
            "focus": "completeness",
            "style": "formal",
            "length": "long",
        },
        "user_focused": {
            "description": "Emphasizes user benefits and business value",
            "focus": "user_impact",
            "style": "business",
            "length": "medium",
        },
        "technical_focused": {
            "description": "Technical precision and accuracy",
            "focus": "technical_accuracy",
            "style": "technical",
            "length": "medium",
        },
        "structured": {
            "description": "Clear structure with checkboxes",
            "focus": "organization",
            "style": "structured",
            "length": "medium",
        },
        "conversational": {
            "description": "Natural, informal language",
            "focus": "accessibility",
            "style": "casual",
            "length": "short",
        },
        "bullet_points": {
            "description": "Bullet point format",
            "focus": "readability",
            "style": "formatted",
            "length": "medium",
        },
    }


def get_prompt_by_name(name: str) -> str:
    """Get a specific prompt variation by name."""
    variations = get_prompt_variations()
    if name not in variations:
        raise ValueError(
            f"Unknown prompt variation: {name}. Available: {list(variations.keys())}"
        )
    return variations[name]
