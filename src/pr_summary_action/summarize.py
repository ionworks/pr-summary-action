"""PR Summary Action - Main summarization logic."""

import os
import json
import requests
import logging
from typing import Dict, Optional, Any
from openai import OpenAI


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_pr_data() -> Dict[str, Any]:
    """Load PR data from GitHub event."""
    try:
        with open(os.environ["GITHUB_EVENT_PATH"]) as f:
            event = json.load(f)
        return event
    except Exception as e:
        logger.error(f"Failed to load PR data: {e}")
        raise


def should_process_pr(event: Dict[str, Any]) -> bool:
    """Check if PR should be processed (merged and closed)."""
    pr = event.get("pull_request", {})
    return event.get("action") == "closed" and pr.get("merged", False)


def get_pr_diff(repo: str, pr_number: int, github_token: str) -> str:
    """Fetch PR diff from GitHub API."""
    diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    try:
        diff_resp = requests.get(
            diff_url,
            headers={
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3.diff",
            },
        )
        diff_resp.raise_for_status()
        return diff_resp.text
    except Exception as e:
        logger.error(f"Failed to fetch PR diff: {e}")
        return ""


def generate_summaries(
    pr: Dict[str, Any], diff: str, openai_client: OpenAI, model: str
) -> Dict[str, str]:
    """Generate technical and marketing summaries using OpenAI."""
    prompt = f"""
    Analyze this PR and create summaries:

    Title: {pr["title"]}
    Description: {pr.get("body", "")}
    Diff: {diff[:3000]}...

    Return JSON:
    {{"technical": "2-3 sentence technical summary", "marketing": "1-2 sentence user benefit"}}
    """

    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )

        summaries = json.loads(response.choices[0].message.content)
        logger.info("Successfully generated AI summaries")
        return summaries
    except Exception as e:
        logger.error(f"Failed to generate summaries: {e}")
        return {"technical": pr["title"], "marketing": "Improvements and updates"}


def post_to_slack(
    pr: Dict[str, Any], summaries: Dict[str, str], webhook_url: str
) -> bool:
    """Post PR summary to Slack."""
    slack_msg = {
        "text": f"🚀 PR #{pr['number']} Merged: {pr['title']}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**Technical:** {summaries['technical']}\n**Marketing:** {summaries['marketing']}",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View PR"},
                        "url": pr["html_url"],
                    }
                ],
            },
        ],
    }

    try:
        response = requests.post(webhook_url, json=slack_msg)
        response.raise_for_status()
        logger.info("Successfully posted to Slack")
        return True
    except Exception as e:
        logger.error(f"Failed to post to Slack: {e}")
        return False


def main() -> None:
    """Main entry point for PR summarization."""
    try:
        # Load environment variables
        required_vars = [
            "GITHUB_EVENT_PATH",
            "GITHUB_REPOSITORY",
            "GITHUB_TOKEN",
            "OPENAI_API_KEY",
            "SLACK_WEBHOOK",
            "MODEL",
        ]

        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Required environment variable {var} not found")

        # Load PR data
        event = load_pr_data()

        # Check if we should process this PR
        if not should_process_pr(event):
            logger.info("PR not merged or not closed, skipping")
            return

        pr = event["pull_request"]
        repo = os.environ["GITHUB_REPOSITORY"]

        logger.info(f"Processing PR #{pr['number']}: {pr['title']}")

        # Get PR diff
        diff = get_pr_diff(repo, pr["number"], os.environ["GITHUB_TOKEN"])

        # Generate summaries
        openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        summaries = generate_summaries(pr, diff, openai_client, os.environ["MODEL"])

        # Post to Slack
        slack_success = post_to_slack(pr, summaries, os.environ["SLACK_WEBHOOK"])

        if slack_success:
            logger.info(f"✅ Successfully summarized PR #{pr['number']}")
        else:
            logger.error(f"❌ Failed to complete all operations for PR #{pr['number']}")

    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise


if __name__ == "__main__":
    main()
