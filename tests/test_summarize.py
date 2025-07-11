"""
Unit tests for PR summary functionality.
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.pr_summary_action.summarize import (
    load_pr_data,
    should_process_pr,
    get_pr_diff,
    generate_summaries,
    post_to_slack,
    main,
)
from src.pr_summary_action.config import Config
from tests.test_fixtures import MockGitHubEvents, MockPRDiffs, MockOpenAIResponses


class TestLoadPRData:
    """Test load_pr_data function."""

    def test_load_pr_data_success(self, tmp_path):
        """Test successful PR data loading."""
        # Create mock GitHub event file
        event_data = MockGitHubEvents.feature_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        config = Config(
            github_event_path=str(event_file),
            github_token="test_token",
            github_repository="test/repo",
            openai_api_key="test_key",
            slack_webhook="test_webhook",
        )
        result = load_pr_data(config)

        assert result == event_data
        assert result["action"] == "closed"
        assert result["pull_request"]["number"] == 42

    def test_load_pr_data_file_not_found(self):
        """Test handling of missing event file."""
        config = Config(
            github_event_path="/nonexistent/file.json",
            github_token="test_token",
            github_repository="test/repo",
            openai_api_key="test_key",
            slack_webhook="test_webhook",
        )
        with pytest.raises(FileNotFoundError):
            load_pr_data(config)

    def test_load_pr_data_invalid_json(self, tmp_path):
        """Test handling of invalid JSON in event file."""
        event_file = tmp_path / "invalid_event.json"
        event_file.write_text("{ invalid json")

        config = Config(
            github_event_path=str(event_file),
            github_token="test_token",
            github_repository="test/repo",
            openai_api_key="test_key",
            slack_webhook="test_webhook",
        )
        with pytest.raises(json.JSONDecodeError):
            load_pr_data(config)


class TestShouldProcessPR:
    """Test should_process_pr function."""

    def test_should_process_merged_pr(self):
        """Test processing of merged PR."""
        event = MockGitHubEvents.feature_pr_event()
        assert should_process_pr(event) is True

    def test_should_not_process_open_pr(self):
        """Test not processing open PR."""
        event = MockGitHubEvents.feature_pr_event()
        event["action"] = "opened"
        assert should_process_pr(event) is False

    def test_should_not_process_closed_unmerged_pr(self):
        """Test not processing closed but unmerged PR."""
        event = MockGitHubEvents.feature_pr_event()
        event["pull_request"]["merged"] = False
        assert should_process_pr(event) is False

    def test_should_not_process_missing_pr(self):
        """Test handling of event without pull_request."""
        event = {"action": "closed"}
        assert should_process_pr(event) is False


class TestGetPRDiff:
    """Test get_pr_diff function."""

    @patch("src.pr_summary_action.summarize.requests.get")
    def test_get_pr_diff_success(self, mock_get):
        """Test successful diff retrieval."""
        mock_response = Mock()
        mock_response.text = MockPRDiffs.feature_diff()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_pr_diff("testorg/test-repo", 42, "fake_token")

        assert "OAuth2 authentication implementation" in result
        mock_get.assert_called_once_with(
            "https://api.github.com/repos/testorg/test-repo/pulls/42",
            headers={
                "Authorization": "token fake_token",
                "Accept": "application/vnd.github.v3.diff",
            },
        )

    @patch("src.pr_summary_action.summarize.requests.get")
    def test_get_pr_diff_api_error(self, mock_get):
        """Test handling of API error when getting diff."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response

        result = get_pr_diff("testorg/test-repo", 42, "fake_token")

        assert result == ""

    @patch("src.pr_summary_action.summarize.requests.get")
    def test_get_pr_diff_request_exception(self, mock_get):
        """Test handling of request exception."""
        mock_get.side_effect = Exception("Network Error")

        result = get_pr_diff("testorg/test-repo", 42, "fake_token")

        assert result == ""


class TestGenerateSummaries:
    """Test generate_summaries function."""

    def test_generate_summaries_success(self):
        """Test successful summary generation."""
        pr_data = MockGitHubEvents.feature_pr_event()["pull_request"]
        diff = MockPRDiffs.feature_diff()

        mock_client = Mock()
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = MockOpenAIResponses.feature_summary()
        mock_response.choices = [Mock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response

        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/tmp/event.json",
            openai_api_key="test_key",
            slack_webhook="test_webhook",
            openai_model="gpt-3.5-turbo",
        )

        result = generate_summaries(pr_data, diff, mock_client, config)

        assert "technical" in result
        assert "marketing" in result
        assert "OAuth2 authentication" in result["technical"]
        assert "Google accounts" in result["marketing"]

    def test_generate_summaries_invalid_json(self):
        """Test handling of invalid JSON response."""
        pr_data = MockGitHubEvents.feature_pr_event()["pull_request"]
        diff = MockPRDiffs.feature_diff()

        mock_client = Mock()
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = MockOpenAIResponses.invalid_json_response()
        mock_response.choices = [Mock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response

        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/tmp/event.json",
            openai_api_key="test_key",
            slack_webhook="test_webhook",
            openai_model="gpt-3.5-turbo",
        )

        result = generate_summaries(pr_data, diff, mock_client, config)

        # Should fall back to PR title
        assert result["technical"] == pr_data["title"]
        assert result["marketing"] == "Improvements and updates"

    def test_generate_summaries_empty_response(self):
        """Test handling of empty response."""
        pr_data = MockGitHubEvents.feature_pr_event()["pull_request"]
        diff = MockPRDiffs.feature_diff()

        mock_client = Mock()
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = None
        mock_response.choices = [Mock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response

        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/tmp/event.json",
            openai_api_key="test_key",
            slack_webhook="test_webhook",
            openai_model="gpt-3.5-turbo",
        )

        result = generate_summaries(pr_data, diff, mock_client, config)

        assert result["technical"] == pr_data["title"]
        assert result["marketing"] == "Improvements and updates"

    def test_generate_summaries_api_error(self):
        """Test handling of OpenAI API error."""
        pr_data = MockGitHubEvents.feature_pr_event()["pull_request"]
        diff = MockPRDiffs.feature_diff()

        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/tmp/event.json",
            openai_api_key="test_key",
            slack_webhook="test_webhook",
            openai_model="gpt-3.5-turbo",
        )

        result = generate_summaries(pr_data, diff, mock_client, config)

        assert result["technical"] == pr_data["title"]
        assert result["marketing"] == "Improvements and updates"

    def test_generate_summaries_excludes_author_info(self):
        """Test that author information is NOT included in the prompt."""
        pr_data = MockGitHubEvents.feature_pr_event()["pull_request"]
        diff = MockPRDiffs.feature_diff()

        mock_client = Mock()
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = MockOpenAIResponses.feature_summary()
        mock_response.choices = [Mock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response

        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/tmp/event.json",
            openai_api_key="test_key",
            slack_webhook="test_webhook",
            openai_model="gpt-3.5-turbo",
        )

        generate_summaries(pr_data, diff, mock_client, config)

        # Check that the prompt does NOT include author information
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][1]["content"]

        # Verify author info is not in prompt
        assert "Author:" not in prompt
        assert "Merged by:" not in prompt
        assert "@developer1" not in prompt
        assert "@maintainer" not in prompt

        # But verify the instruction to exclude author names is present
        assert "Do not mention author names in the summaries" in prompt


class TestPostToSlack:
    """Test post_to_slack function."""

    @patch("src.pr_summary_action.summarize.requests.post")
    def test_post_to_slack_success(self, mock_post):
        """Test successful Slack posting."""
        pr_data = MockGitHubEvents.feature_pr_event()["pull_request"]
        summaries = {
            "technical": "Added OAuth2 authentication support",
            "marketing": "Users can now log in with Google accounts",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        config = Config(
            github_token="test_token",
            github_repository="test/repo",
            github_event_path="/tmp/event.json",
            openai_api_key="test_key",
            slack_webhook="https://hooks.slack.com/test",
        )

        result = post_to_slack(pr_data, summaries, config)

        assert result is True
        mock_post.assert_called_once()

        # Check that the posted data contains expected content
        posted_data = mock_post.call_args[1]["json"]
        assert "PR #42 Merged" in posted_data["text"]
        assert "Add user authentication with OAuth2" in posted_data["text"]

    @patch("src.pr_summary_action.summarize.requests.post")
    def test_post_to_slack_api_error(self, mock_post):
        """Test handling of Slack API error."""
        pr_data = MockGitHubEvents.feature_pr_event()["pull_request"]
        summaries = {"technical": "test", "marketing": "test"}

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Slack API Error")
        mock_post.return_value = mock_response

        result = post_to_slack(pr_data, summaries, "https://hooks.slack.com/test")

        assert result is False

    @patch("src.pr_summary_action.summarize.requests.post")
    def test_post_to_slack_request_exception(self, mock_post):
        """Test handling of request exception."""
        pr_data = MockGitHubEvents.feature_pr_event()["pull_request"]
        summaries = {"technical": "test", "marketing": "test"}

        mock_post.side_effect = Exception("Network Error")

        result = post_to_slack(pr_data, summaries, "https://hooks.slack.com/test")

        assert result is False


class TestMain:
    """Test main function integration."""

    @patch("src.pr_summary_action.summarize.post_to_slack")
    @patch("src.pr_summary_action.summarize.generate_summaries")
    @patch("src.pr_summary_action.summarize.get_pr_diff")
    @patch("src.pr_summary_action.summarize.OpenAI")
    @patch("src.pr_summary_action.summarize.load_pr_data")
    def test_main_success_flow(
        self,
        mock_load_pr,
        mock_openai,
        mock_get_diff,
        mock_generate,
        mock_post_slack,
        tmp_path,
    ):
        """Test successful main execution flow."""
        # Setup mocks
        event_data = MockGitHubEvents.feature_pr_event()
        mock_load_pr.return_value = event_data

        mock_get_diff.return_value = MockPRDiffs.feature_diff()

        mock_generate.return_value = {
            "technical": "Test technical summary",
            "marketing": "Test marketing summary",
        }

        mock_post_slack.return_value = True

        # Setup environment
        env_vars = {
            "GITHUB_EVENT_PATH": str(tmp_path / "event.json"),
            "GITHUB_REPOSITORY": "testorg/test-repo",
            "GITHUB_TOKEN": "fake_token",
            "OPENAI_API_KEY": "fake_key",
            "SLACK_WEBHOOK": "https://hooks.slack.com/test",
            "MODEL": "gpt-3.5-turbo",
        }

        with patch.dict(os.environ, env_vars):
            main()

        # Verify all functions were called
        mock_load_pr.assert_called_once()
        mock_get_diff.assert_called_once_with("testorg/test-repo", 42, "fake_token")
        mock_generate.assert_called_once()
        mock_post_slack.assert_called_once()

    @patch("src.pr_summary_action.summarize.load_pr_data")
    def test_main_skip_non_merged_pr(self, mock_load_pr):
        """Test main skips non-merged PRs."""
        event_data = MockGitHubEvents.feature_pr_event()
        event_data["pull_request"]["merged"] = False
        mock_load_pr.return_value = event_data

        env_vars = {
            "GITHUB_EVENT_PATH": "/tmp/event.json",
            "GITHUB_REPOSITORY": "testorg/test-repo",
            "GITHUB_TOKEN": "fake_token",
            "OPENAI_API_KEY": "fake_key",
            "SLACK_WEBHOOK": "https://hooks.slack.com/test",
            "MODEL": "gpt-3.5-turbo",
        }

        with patch.dict(os.environ, env_vars):
            main()

        mock_load_pr.assert_called_once()

    def test_main_missing_environment_variables(self):
        """Test main raises error for missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Required configuration field"):
                main()


class TestPRScenarios:
    """Test different PR scenarios end-to-end."""

    @patch("src.pr_summary_action.summarize.requests.post")
    @patch("src.pr_summary_action.summarize.requests.get")
    @patch("src.pr_summary_action.summarize.OpenAI")
    def test_feature_pr_scenario(self, mock_openai, mock_get, mock_post):
        """Test feature PR scenario."""
        self._setup_successful_mocks(
            mock_openai, mock_get, mock_post, MockOpenAIResponses.feature_summary()
        )

        event_data = MockGitHubEvents.feature_pr_event()

        with patch(
            "src.pr_summary_action.summarize.load_pr_data", return_value=event_data
        ):
            self._run_main_with_env()

        # Verify Slack message contains feature-specific content
        slack_call = mock_post.call_args[1]["json"]
        assert "OAuth2 authentication" in str(slack_call)

    @patch("src.pr_summary_action.summarize.requests.post")
    @patch("src.pr_summary_action.summarize.requests.get")
    @patch("src.pr_summary_action.summarize.OpenAI")
    def test_bugfix_pr_scenario(self, mock_openai, mock_get, mock_post):
        """Test bugfix PR scenario."""
        self._setup_successful_mocks(
            mock_openai, mock_get, mock_post, MockOpenAIResponses.bugfix_summary()
        )

        event_data = MockGitHubEvents.bugfix_pr_event()

        with patch(
            "src.pr_summary_action.summarize.load_pr_data", return_value=event_data
        ):
            self._run_main_with_env()

        # Verify Slack message contains bugfix-specific content
        slack_call = mock_post.call_args[1]["json"]
        assert "memory leak" in str(slack_call)

    @patch("src.pr_summary_action.summarize.requests.post")
    @patch("src.pr_summary_action.summarize.requests.get")
    @patch("src.pr_summary_action.summarize.OpenAI")
    def test_docs_pr_scenario(self, mock_openai, mock_get, mock_post):
        """Test documentation PR scenario."""
        self._setup_successful_mocks(
            mock_openai, mock_get, mock_post, MockOpenAIResponses.docs_summary()
        )

        event_data = MockGitHubEvents.docs_pr_event()

        with patch(
            "src.pr_summary_action.summarize.load_pr_data", return_value=event_data
        ):
            self._run_main_with_env()

        # Verify Slack message contains docs-specific content
        slack_call = mock_post.call_args[1]["json"]
        assert "documentation" in str(slack_call)

    def _setup_successful_mocks(
        self, mock_openai, mock_get, mock_post, openai_response
    ):
        """Setup successful mocks for testing."""
        # Mock GitHub API diff response
        mock_get_response = Mock()
        mock_get_response.text = MockPRDiffs.feature_diff()
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response

        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = openai_response
        mock_response.choices = [Mock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Mock Slack response
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.raise_for_status.return_value = None
        mock_post.return_value = mock_post_response

    def _run_main_with_env(self):
        """Run main with test environment variables."""
        env_vars = {
            "GITHUB_EVENT_PATH": "/tmp/event.json",
            "GITHUB_REPOSITORY": "testorg/test-repo",
            "GITHUB_TOKEN": "fake_token",
            "OPENAI_API_KEY": "fake_key",
            "SLACK_WEBHOOK": "https://hooks.slack.com/test",
            "MODEL": "gpt-3.5-turbo",
        }

        with patch.dict(os.environ, env_vars):
            main()
