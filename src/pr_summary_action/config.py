"""Configuration management for PR Summary Action."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration settings for PR Summary Action."""

    # Required fields (no defaults)
    github_token: str
    github_repository: str
    github_event_path: str
    openai_api_key: str
    slack_webhook: str

    # Optional fields (with defaults)
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 300
    temperature: float = 0.7
    slack_channel: Optional[str] = None
    max_diff_length: int = 3000
    enable_debugging: bool = True

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            github_token=os.getenv("GITHUB_TOKEN", ""),
            github_repository=os.getenv("GITHUB_REPOSITORY", ""),
            github_event_path=os.getenv("GITHUB_EVENT_PATH", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("MODEL", "gpt-3.5-turbo"),
            max_tokens=int(os.getenv("MAX_TOKENS", "300")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            slack_webhook=os.getenv("SLACK_WEBHOOK", ""),
            slack_channel=os.getenv("SLACK_CHANNEL"),
            max_diff_length=int(os.getenv("MAX_DIFF_LENGTH", "3000")),
            enable_debugging=os.getenv("ENABLE_DEBUG", "true").lower() == "true",
        )

    def validate(self) -> None:
        """Validate configuration settings."""
        required_fields = [
            "github_token",
            "github_repository",
            "github_event_path",
            "openai_api_key",
            "slack_webhook",
        ]

        for field in required_fields:
            if not getattr(self, field):
                raise ValueError(f"Required configuration field '{field}' is missing")

        # Validate OpenAI model
        valid_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        if self.openai_model not in valid_models:
            raise ValueError(f"Invalid OpenAI model: {self.openai_model}")

        # Validate Slack webhook
        if not self.slack_webhook.startswith("https://hooks.slack.com/"):
            raise ValueError("Invalid Slack webhook URL format")

        # Validate numeric ranges
        if self.max_tokens < 50 or self.max_tokens > 4000:
            raise ValueError("max_tokens must be between 50 and 4000")

        if self.temperature < 0.0 or self.temperature > 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")

        if self.max_diff_length < 100:
            raise ValueError("max_diff_length must be at least 100")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "github_token": "***" if self.github_token else "",
            "github_repository": self.github_repository,
            "github_event_path": self.github_event_path,
            "openai_api_key": "***" if self.openai_api_key else "",
            "openai_model": self.openai_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "slack_webhook": "***" if self.slack_webhook else "",
            "slack_channel": self.slack_channel,
            "max_diff_length": self.max_diff_length,
            "enable_debugging": self.enable_debugging,
        }
