"""PR Summary Action - AI-powered PR summaries to Slack."""

__version__ = "1.0.0"
__author__ = "Ionworks"
__description__ = "AI-powered PR summaries to Slack"

from .summarize import main as summarize_pr

__all__ = ["summarize_pr"]
