"""
PR Summary Evaluation System

This package contains tools for evaluating and improving PR summarization prompts.
"""

from .evaluation import (
    EvaluationRunner,
    TestDatasetBuilder,
    PRTestCase,
    EvaluationMetrics,
)
from .prompt_variations import (
    get_prompt_variations,
    get_prompt_metadata,
    get_prompt_by_name,
)

__all__ = [
    "EvaluationRunner",
    "TestDatasetBuilder",
    "PRTestCase",
    "EvaluationMetrics",
    "get_prompt_variations",
    "get_prompt_metadata",
    "get_prompt_by_name",
]
