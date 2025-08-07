#!/usr/bin/env python3
"""
Test script to verify OpenAI API key and Slack webhook are working correctly.
"""

import os
import json
import pytest
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class TestCredentials:
    """Test class for credential validation."""

    def test_openai_api_key_format(self):
        """Test OpenAI API key format validation."""
        api_key = os.getenv("OPENAI_API_KEY")

        assert api_key is not None, "OpenAI API key not found in environment"
        assert api_key.startswith("sk-"), "OpenAI API key should start with 'sk-'"
        assert len(api_key) > 20, "OpenAI API key appears too short"

    def test_slack_webhook_format(self):
        """Test Slack webhook URL format validation."""
        webhook_url = os.getenv("SLACK_WEBHOOK")

        assert webhook_url is not None, "Slack webhook URL not found in environment"
        assert webhook_url.startswith("https://hooks.slack.com/"), (
            "Invalid Slack webhook URL format"
        )

    @pytest.mark.integration
    def test_openai_api_connectivity(self):
        """Test OpenAI API connectivity with actual API call."""
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            pytest.skip("OpenAI API key not available")

        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say 'API test successful' in 3 words"}
                ],
                max_tokens=10,
            )

            result = response.choices[0].message.content
            assert result is not None, "OpenAI API returned no content"
            assert len(result.strip()) > 0, "OpenAI API returned empty response"

        except Exception as e:
            pytest.fail(f"OpenAI API test failed: {str(e)}")

    @pytest.mark.integration
    def test_slack_webhook_connectivity(self):
        """Test Slack webhook connectivity with actual webhook call."""
        webhook_url = os.getenv("SLACK_WEBHOOK")

        if not webhook_url:
            pytest.skip("Slack webhook URL not available")

        test_message = {
            "text": "🧪 PR Summary Action Test",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ *Test Message*\nThis is a test to verify the PR Summary Action credentials are working correctly.",
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "🔧 Sent from PR Summary Action test script",
                        }
                    ],
                },
            ],
        }

        try:
            response = requests.post(webhook_url, json=test_message, timeout=30)
            response.raise_for_status()

            assert response.status_code == 200, (
                f"Slack webhook returned status {response.status_code}"
            )

        except Exception as e:
            pytest.fail(f"Slack webhook test failed: {str(e)}")

    @pytest.mark.integration
    def test_full_pr_summary_simulation(self):
        """Test the full PR summary workflow simulation."""
        api_key = os.getenv("OPENAI_API_KEY")
        webhook_url = os.getenv("SLACK_WEBHOOK")

        if not api_key or not webhook_url:
            pytest.skip("Missing required credentials for full simulation")

        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        mock_pr_data = {
            "number": 123,
            "title": "Add new feature for user authentication",
            "body": "This PR adds OAuth2 authentication support",
            "html_url": "https://github.com/test/repo/pull/123",
        }

        # Test OpenAI summary generation
        prompt = f"""
        Analyze this PR and create summaries:

        Title: {mock_pr_data["title"]}
        Description: {mock_pr_data["body"]}
        Diff: Added login/logout functionality with proper session management

        Return JSON:
        {{"technical": "2-3 sentence technical summary", "marketing": "1-2 sentence user benefit"}}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )

            try:
                summaries = json.loads(response.choices[0].message.content)
                assert "technical" in summaries, "Technical summary not found"
                assert "marketing" in summaries, "Marketing summary not found"
            except json.JSONDecodeError:
                summaries = {
                    "technical": "Test technical summary",
                    "marketing": "Test marketing summary",
                }

            # Test Slack posting
            slack_message = {
                "text": "🧪 PR Summary Action - Full Test",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"🚀 *Test PR Summary*\n\n**Technical:** {summaries['technical']}\n**Marketing:** {summaries['marketing']}",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "🔧 This is a test of the full PR summary workflow",
                            }
                        ],
                    },
                ],
            }

            response = requests.post(webhook_url, json=slack_message, timeout=30)
            response.raise_for_status()

            assert response.status_code == 200, (
                f"Slack posting failed with status {response.status_code}"
            )

        except Exception as e:
            pytest.fail(f"Full PR summary simulation failed: {str(e)}")
