"""
Tests for the Config class.
"""

import os
import pytest
from unittest.mock import patch

from src.pr_summary_action.config import Config


class TestConfig:
    """Test Config class functionality."""

    def test_config_from_env_success(self):
        """Test successful configuration from environment variables."""
        env_vars = {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_EVENT_PATH": "/path/to/event.json",
            "OPENAI_API_KEY": "sk-test-key",
            "SLACK_WEBHOOK": "https://hooks.slack.com/services/test",
            "MODEL": "gpt-4",
            "MAX_TOKENS": "500",
            "TEMPERATURE": "0.5",
            "SLACK_CHANNEL": "#test-channel",
            "MAX_DIFF_LENGTH": "5000",
            "ENABLE_DEBUG": "false",
        }

        with patch.dict(os.environ, env_vars):
            config = Config.from_env()

        assert config.github_token == "test_token"
        assert config.github_repository == "test/repo"
        assert config.github_event_path == "/path/to/event.json"
        assert config.openai_api_key == "sk-test-key"
        assert config.slack_webhook == "https://hooks.slack.com/services/test"
        assert config.openai_model == "gpt-4"
        assert config.max_tokens == 500
        assert config.temperature == 0.5
        assert config.slack_channel == "#test-channel"
        assert config.max_diff_length == 5000
        assert config.enable_debugging is False

    def test_config_from_env_defaults(self):
        """Test configuration with default values."""
        env_vars = {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_EVENT_PATH": "/path/to/event.json",
            "OPENAI_API_KEY": "sk-test-key",
            "SLACK_WEBHOOK": "https://hooks.slack.com/services/test",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()

        # Check defaults
        assert config.openai_model == "gpt-3.5-turbo"
        assert config.max_tokens == 300
        assert config.temperature == 0.7
        assert config.slack_channel is None
        assert config.max_diff_length == 3000
        assert config.enable_debugging is True

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="sk-test-key",
            slack_webhook="https://hooks.slack.com/services/test",
            openai_model="gpt-3.5-turbo",
            max_tokens=300,
            temperature=0.7,
            slack_channel=None,
            max_diff_length=3000,
            enable_debugging=True,
        )

        # Should not raise any exception
        config.validate()

    def test_config_validation_missing_required_field(self):
        """Test validation fails for missing required fields."""
        config = Config(
            github_token="",  # Missing required field
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="sk-test-key",
            slack_webhook="https://hooks.slack.com/services/test",
        )

        with pytest.raises(
            ValueError, match="Required configuration field 'github_token' is missing"
        ):
            config.validate()

    def test_config_validation_invalid_model(self):
        """Test validation fails for invalid OpenAI model."""
        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="sk-test-key",
            slack_webhook="https://hooks.slack.com/services/test",
            openai_model="invalid-model",
        )

        with pytest.raises(ValueError, match="Invalid OpenAI model: invalid-model"):
            config.validate()

    def test_config_validation_invalid_slack_webhook(self):
        """Test validation fails for invalid Slack webhook."""
        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="sk-test-key",
            slack_webhook="https://invalid-webhook.com",
        )

        with pytest.raises(ValueError, match="Invalid Slack webhook URL format"):
            config.validate()

    def test_config_validation_invalid_max_tokens(self):
        """Test validation fails for invalid max_tokens."""
        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="sk-test-key",
            slack_webhook="https://hooks.slack.com/services/test",
            max_tokens=10,  # Too low
        )

        with pytest.raises(ValueError, match="max_tokens must be between 50 and 4000"):
            config.validate()

    def test_config_validation_invalid_temperature(self):
        """Test validation fails for invalid temperature."""
        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="sk-test-key",
            slack_webhook="https://hooks.slack.com/services/test",
            temperature=3.0,  # Too high
        )

        with pytest.raises(ValueError, match="temperature must be between 0.0 and 2.0"):
            config.validate()

    def test_config_validation_invalid_max_diff_length(self):
        """Test validation fails for invalid max_diff_length."""
        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="sk-test-key",
            slack_webhook="https://hooks.slack.com/services/test",
            max_diff_length=50,  # Too low
        )

        with pytest.raises(ValueError, match="max_diff_length must be at least 100"):
            config.validate()

    def test_config_to_dict_masks_secrets(self):
        """Test that to_dict masks sensitive information."""
        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="sk-test-key",
            slack_webhook="https://hooks.slack.com/services/test",
        )

        config_dict = config.to_dict()

        assert config_dict["github_token"] == "***"
        assert config_dict["openai_api_key"] == "***"
        assert config_dict["slack_webhook"] == "***"
        assert config_dict["github_repository"] == "test/repo"
        assert config_dict["github_event_path"] == "/path/to/event.json"

    def test_config_to_dict_empty_secrets(self):
        """Test that to_dict handles empty secrets."""
        config = Config(
            github_token="",
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="",
            slack_webhook="",
        )

        config_dict = config.to_dict()

        assert config_dict["github_token"] == ""
        assert config_dict["openai_api_key"] == ""
        assert config_dict["slack_webhook"] == ""

    def test_config_environment_variable_parsing(self):
        """Test parsing of different environment variable types."""
        env_vars = {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_EVENT_PATH": "/path/to/event.json",
            "OPENAI_API_KEY": "sk-test-key",
            "SLACK_WEBHOOK": "https://hooks.slack.com/services/test",
            "MAX_TOKENS": "invalid",  # Invalid integer
            "TEMPERATURE": "invalid",  # Invalid float
            "ENABLE_DEBUG": "yes",  # Non-boolean value
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(ValueError):
                Config.from_env()

    def test_config_enable_debugging_parsing(self):
        """Test parsing of enable_debugging boolean values."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("yes", False),  # Only "true" should be True
            ("1", False),
            ("", False),
        ]

        for env_value, expected in test_cases:
            env_vars = {
                "GITHUB_TOKEN": "test_token",
                "GITHUB_REPOSITORY": "test/repo",
                "GITHUB_EVENT_PATH": "/path/to/event.json",
                "OPENAI_API_KEY": "sk-test-key",
                "SLACK_WEBHOOK": "https://hooks.slack.com/services/test",
                "ENABLE_DEBUG": env_value,
            }

            with patch.dict(os.environ, env_vars):
                config = Config.from_env()
                assert config.enable_debugging == expected, (
                    f"Failed for value '{env_value}'"
                )

    def test_config_all_valid_openai_models(self):
        """Test validation accepts all valid OpenAI models."""
        valid_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]

        for model in valid_models:
            config = Config(
                github_token="test_token",
                github_repository="test/repo",
                github_event_path="/path/to/event.json",
                openai_api_key="sk-test-key",
                slack_webhook="https://hooks.slack.com/services/test",
                openai_model=model,
            )

            # Should not raise any exception
            config.validate()

    def test_config_boundary_values(self):
        """Test configuration with boundary values."""
        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/path/to/event.json",
            openai_api_key="sk-test-key",
            slack_webhook="https://hooks.slack.com/services/test",
            max_tokens=50,  # Minimum
            temperature=0.0,  # Minimum
            max_diff_length=100,  # Minimum
        )

        # Should not raise any exception
        config.validate()

        config.max_tokens = 4000  # Maximum
        config.temperature = 2.0  # Maximum
        config.validate()

    def test_config_integration_with_real_env(self):
        """Test config integration with realistic environment setup."""
        # This tests the actual environment variable names used in production
        env_vars = {
            "GITHUB_TOKEN": "ghp_test_token",
            "GITHUB_REPOSITORY": "myorg/myrepo",
            "GITHUB_EVENT_PATH": "/github/workspace/event.json",
            "OPENAI_API_KEY": "sk-test-openai-key",
            "SLACK_WEBHOOK": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
            "MODEL": "gpt-4",
            "MAX_TOKENS": "1000",
            "TEMPERATURE": "0.8",
            "MAX_DIFF_LENGTH": "5000",
            "ENABLE_DEBUG": "true",
        }

        with patch.dict(os.environ, env_vars):
            config = Config.from_env()
            config.validate()

            # Verify realistic values are parsed correctly
            assert config.github_token.startswith("ghp_")
            assert config.openai_api_key.startswith("sk-")
            assert "hooks.slack.com" in config.slack_webhook
            assert config.openai_model == "gpt-4"
            assert config.max_tokens == 1000
            assert config.temperature == 0.8
            assert config.max_diff_length == 5000
            assert config.enable_debugging is True
