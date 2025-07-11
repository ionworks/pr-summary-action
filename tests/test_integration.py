"""
Integration tests for PR Summary Action.
Tests complete workflows with realistic scenarios.
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.pr_summary_action.summarize import main
from tests.test_fixtures import MockGitHubEvents, MockPRDiffs, MockOpenAIResponses


class TestFullWorkflowIntegration:
    """Test complete PR summary workflow integration."""

    def test_feature_pr_complete_workflow(self, tmp_path):
        """Test complete workflow for a feature PR."""
        # Create event file
        event_data = MockGitHubEvents.feature_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        # Mock external dependencies
        with (
            patch("src.pr_summary_action.summarize.requests.get") as mock_get,
            patch("src.pr_summary_action.summarize.requests.post") as mock_post,
            patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
        ):
            # Setup GitHub API mock
            mock_get_response = Mock()
            mock_get_response.text = MockPRDiffs.feature_diff()
            mock_get_response.raise_for_status.return_value = None
            mock_get.return_value = mock_get_response

            # Setup OpenAI mock
            mock_client = Mock()
            mock_response = Mock()
            mock_message = Mock()
            mock_message.content = MockOpenAIResponses.feature_summary()
            mock_response.choices = [Mock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            # Setup Slack mock
            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            # Run main function
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": "testorg/test-repo",
                    "GITHUB_TOKEN": "fake_token",
                    "OPENAI_API_KEY": "fake_key",
                    "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                    "MODEL": "gpt-3.5-turbo",
                },
            ):
                main()

            # Verify all steps were executed
            mock_get.assert_called_once()
            mock_client.chat.completions.create.assert_called_once()
            mock_post.assert_called_once()

            # Verify Slack message content
            slack_call = mock_post.call_args[1]["json"]
            assert "PR #42 Merged" in slack_call["text"]
            assert (
                "John Developer (@developer1)"
                in slack_call["blocks"][0]["text"]["text"]
            )
            assert "OAuth2 authentication" in slack_call["blocks"][1]["text"]["text"]
            assert "Google accounts" in slack_call["blocks"][1]["text"]["text"]

    def test_bugfix_pr_complete_workflow(self, tmp_path):
        """Test complete workflow for a bugfix PR."""
        event_data = MockGitHubEvents.bugfix_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        with (
            patch("src.pr_summary_action.summarize.requests.get") as mock_get,
            patch("src.pr_summary_action.summarize.requests.post") as mock_post,
            patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
        ):
            # Setup mocks
            mock_get_response = Mock()
            mock_get_response.text = MockPRDiffs.bugfix_diff()
            mock_get_response.raise_for_status.return_value = None
            mock_get.return_value = mock_get_response

            mock_client = Mock()
            mock_response = Mock()
            mock_message = Mock()
            mock_message.content = MockOpenAIResponses.bugfix_summary()
            mock_response.choices = [Mock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            # Run main function
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": "testorg/test-repo",
                    "GITHUB_TOKEN": "fake_token",
                    "OPENAI_API_KEY": "fake_key",
                    "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                    "MODEL": "gpt-3.5-turbo",
                },
            ):
                main()

            # Verify bugfix-specific content
            slack_call = mock_post.call_args[1]["json"]
            assert "memory leak" in slack_call["blocks"][1]["text"]["text"]
            assert (
                "Alice Developer (@developer2)"
                in slack_call["blocks"][0]["text"]["text"]
            )

    def test_docs_pr_complete_workflow(self, tmp_path):
        """Test complete workflow for a documentation PR."""
        event_data = MockGitHubEvents.docs_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        with (
            patch("src.pr_summary_action.summarize.requests.get") as mock_get,
            patch("src.pr_summary_action.summarize.requests.post") as mock_post,
            patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
        ):
            # Setup mocks
            mock_get_response = Mock()
            mock_get_response.text = MockPRDiffs.docs_diff()
            mock_get_response.raise_for_status.return_value = None
            mock_get.return_value = mock_get_response

            mock_client = Mock()
            mock_response = Mock()
            mock_message = Mock()
            mock_message.content = MockOpenAIResponses.docs_summary()
            mock_response.choices = [Mock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            # Run main function
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": "testorg/test-repo",
                    "GITHUB_TOKEN": "fake_token",
                    "OPENAI_API_KEY": "fake_key",
                    "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                    "MODEL": "gpt-3.5-turbo",
                },
            ):
                main()

            # Verify docs-specific content
            slack_call = mock_post.call_args[1]["json"]
            assert "documentation" in slack_call["blocks"][1]["text"]["text"]
            assert (
                "Bob Writer (@techwriter1)" in slack_call["blocks"][0]["text"]["text"]
            )


class TestErrorHandlingIntegration:
    """Test error handling in complete workflows."""

    def test_openai_json_error_recovery(self, tmp_path):
        """Test recovery from OpenAI JSON parsing errors."""
        event_data = MockGitHubEvents.feature_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        with (
            patch("src.pr_summary_action.summarize.requests.get") as mock_get,
            patch("src.pr_summary_action.summarize.requests.post") as mock_post,
            patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
        ):
            # Setup GitHub API mock
            mock_get_response = Mock()
            mock_get_response.text = MockPRDiffs.feature_diff()
            mock_get_response.raise_for_status.return_value = None
            mock_get.return_value = mock_get_response

            # Setup OpenAI mock with invalid JSON
            mock_client = Mock()
            mock_response = Mock()
            mock_message = Mock()
            mock_message.content = MockOpenAIResponses.invalid_json_response()
            mock_response.choices = [Mock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            # Setup Slack mock
            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            # Run main function
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": "testorg/test-repo",
                    "GITHUB_TOKEN": "fake_token",
                    "OPENAI_API_KEY": "fake_key",
                    "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                    "MODEL": "gpt-3.5-turbo",
                },
            ):
                main()

            # Verify it still posts to Slack with fallback content
            mock_post.assert_called_once()
            slack_call = mock_post.call_args[1]["json"]
            # Should use PR title as fallback
            assert (
                "Add user authentication with OAuth2"
                in slack_call["blocks"][1]["text"]["text"]
            )

    def test_github_api_error_recovery(self, tmp_path):
        """Test recovery from GitHub API errors."""
        event_data = MockGitHubEvents.feature_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        with (
            patch("src.pr_summary_action.summarize.requests.get") as mock_get,
            patch("src.pr_summary_action.summarize.requests.post") as mock_post,
            patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
        ):
            # Setup GitHub API mock with error
            mock_get_response = Mock()
            mock_get_response.raise_for_status.side_effect = Exception(
                "GitHub API Error"
            )
            mock_get.return_value = mock_get_response

            # Setup OpenAI mock
            mock_client = Mock()
            mock_response = Mock()
            mock_message = Mock()
            mock_message.content = MockOpenAIResponses.feature_summary()
            mock_response.choices = [Mock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            # Setup Slack mock
            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            # Run main function
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": "testorg/test-repo",
                    "GITHUB_TOKEN": "fake_token",
                    "OPENAI_API_KEY": "fake_key",
                    "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                    "MODEL": "gpt-3.5-turbo",
                },
            ):
                main()

            # Should still continue with empty diff
            mock_post.assert_called_once()

    def test_slack_api_error_handling(self, tmp_path):
        """Test handling of Slack API errors."""
        event_data = MockGitHubEvents.feature_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        with (
            patch("src.pr_summary_action.summarize.requests.get") as mock_get,
            patch("src.pr_summary_action.summarize.requests.post") as mock_post,
            patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
        ):
            # Setup GitHub API mock
            mock_get_response = Mock()
            mock_get_response.text = MockPRDiffs.feature_diff()
            mock_get_response.raise_for_status.return_value = None
            mock_get.return_value = mock_get_response

            # Setup OpenAI mock
            mock_client = Mock()
            mock_response = Mock()
            mock_message = Mock()
            mock_message.content = MockOpenAIResponses.feature_summary()
            mock_response.choices = [Mock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            # Setup Slack mock with error
            mock_post_response = Mock()
            mock_post_response.raise_for_status.side_effect = Exception(
                "Slack API Error"
            )
            mock_post.return_value = mock_post_response

            # Run main function
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": "testorg/test-repo",
                    "GITHUB_TOKEN": "fake_token",
                    "OPENAI_API_KEY": "fake_key",
                    "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                    "MODEL": "gpt-3.5-turbo",
                },
            ):
                main()

            # Should attempt to post to Slack but handle the error
            mock_post.assert_called_once()


class TestRealWorldScenarios:
    """Test scenarios that mimic real-world usage patterns."""

    def test_large_pr_with_multiple_files(self, tmp_path):
        """Test handling of large PRs with multiple files."""
        # Create a large PR event
        event_data = MockGitHubEvents.refactor_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        # Create a large diff
        large_diff = MockPRDiffs.refactor_diff() * 10  # Simulate large diff

        with (
            patch("src.pr_summary_action.summarize.requests.get") as mock_get,
            patch("src.pr_summary_action.summarize.requests.post") as mock_post,
            patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
        ):
            # Setup mocks
            mock_get_response = Mock()
            mock_get_response.text = large_diff
            mock_get_response.raise_for_status.return_value = None
            mock_get.return_value = mock_get_response

            mock_client = Mock()
            mock_response = Mock()
            mock_message = Mock()
            mock_message.content = MockOpenAIResponses.refactor_summary()
            mock_response.choices = [Mock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            # Run main function
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": "testorg/test-repo",
                    "GITHUB_TOKEN": "fake_token",
                    "OPENAI_API_KEY": "fake_key",
                    "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                    "MODEL": "gpt-3.5-turbo",
                },
            ):
                main()

            # Verify the prompt was truncated appropriately
            openai_call = mock_client.chat.completions.create.call_args
            prompt = openai_call[1]["messages"][1]["content"]
            # Should be truncated to 3000 characters
            assert (
                len(prompt.split("Diff (first 3000 chars):")[1].split("\n")[0]) <= 3000
            )

    def test_pr_with_minimal_description(self, tmp_path):
        """Test PR with minimal description."""
        event_data = MockGitHubEvents.feature_pr_event()
        event_data["pull_request"]["body"] = "Fix bug"  # Minimal description
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        with (
            patch("src.pr_summary_action.summarize.requests.get") as mock_get,
            patch("src.pr_summary_action.summarize.requests.post") as mock_post,
            patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
        ):
            # Setup mocks
            mock_get_response = Mock()
            mock_get_response.text = MockPRDiffs.feature_diff()
            mock_get_response.raise_for_status.return_value = None
            mock_get.return_value = mock_get_response

            mock_client = Mock()
            mock_response = Mock()
            mock_message = Mock()
            mock_message.content = MockOpenAIResponses.feature_summary()
            mock_response.choices = [Mock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            # Run main function
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": "testorg/test-repo",
                    "GITHUB_TOKEN": "fake_token",
                    "OPENAI_API_KEY": "fake_key",
                    "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                    "MODEL": "gpt-3.5-turbo",
                },
            ):
                main()

            # Verify it still works with minimal description
            mock_post.assert_called_once()
            slack_call = mock_post.call_args[1]["json"]
            assert "OAuth2 authentication" in slack_call["blocks"][1]["text"]["text"]

    def test_pr_with_no_diff(self, tmp_path):
        """Test PR with no diff (empty diff)."""
        event_data = MockGitHubEvents.feature_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        with (
            patch("src.pr_summary_action.summarize.requests.get") as mock_get,
            patch("src.pr_summary_action.summarize.requests.post") as mock_post,
            patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
        ):
            # Setup mocks with empty diff
            mock_get_response = Mock()
            mock_get_response.text = ""  # Empty diff
            mock_get_response.raise_for_status.return_value = None
            mock_get.return_value = mock_get_response

            mock_client = Mock()
            mock_response = Mock()
            mock_message = Mock()
            mock_message.content = MockOpenAIResponses.feature_summary()
            mock_response.choices = [Mock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            # Run main function
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": "testorg/test-repo",
                    "GITHUB_TOKEN": "fake_token",
                    "OPENAI_API_KEY": "fake_key",
                    "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                    "MODEL": "gpt-3.5-turbo",
                },
            ):
                main()

            # Should still work with empty diff
            mock_post.assert_called_once()

    def test_different_gpt_models(self, tmp_path):
        """Test with different GPT models."""
        event_data = MockGitHubEvents.feature_pr_event()
        event_file = tmp_path / "github_event.json"
        event_file.write_text(json.dumps(event_data))

        models_to_test = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]

        for model in models_to_test:
            with (
                patch("src.pr_summary_action.summarize.requests.get") as mock_get,
                patch("src.pr_summary_action.summarize.requests.post") as mock_post,
                patch("src.pr_summary_action.summarize.OpenAI") as mock_openai,
            ):
                # Setup mocks
                mock_get_response = Mock()
                mock_get_response.text = MockPRDiffs.feature_diff()
                mock_get_response.raise_for_status.return_value = None
                mock_get.return_value = mock_get_response

                mock_client = Mock()
                mock_response = Mock()
                mock_message = Mock()
                mock_message.content = MockOpenAIResponses.feature_summary()
                mock_response.choices = [Mock(message=mock_message)]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                mock_post_response = Mock()
                mock_post_response.status_code = 200
                mock_post_response.raise_for_status.return_value = None
                mock_post.return_value = mock_post_response

                # Run main function with specific model
                with patch.dict(
                    os.environ,
                    {
                        "GITHUB_EVENT_PATH": str(event_file),
                        "GITHUB_REPOSITORY": "testorg/test-repo",
                        "GITHUB_TOKEN": "fake_token",
                        "OPENAI_API_KEY": "fake_key",
                        "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                        "MODEL": model,
                    },
                ):
                    main()

                # Verify the correct model was used
                openai_call = mock_client.chat.completions.create.call_args
                assert openai_call[1]["model"] == model
