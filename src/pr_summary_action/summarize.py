"""PR Summary Action - Main summarization logic."""

import os
import json
import requests
import logging
from typing import Dict, Optional, Any
from openai import OpenAI
from .config import Config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_pr_data(config: Config) -> Dict[str, Any]:
    """Load PR data from GitHub event."""
    try:
        with open(config.github_event_path) as f:
            event = json.load(f)

        if config.enable_debugging:
            # Add debugging to log the full event data
            logger.info("=== GitHub Event Data ===")
            logger.info(f"Event action: {event.get('action')}")
            logger.info(f"Event type: {event.get('type', 'unknown')}")

            if "pull_request" in event:
                pr = event["pull_request"]
                logger.info("=== PR Information ===")
                logger.info(f"PR Number: {pr.get('number')}")
                logger.info(f"PR Title: {pr.get('title')}")
                logger.info(f"PR State: {pr.get('state')}")
                logger.info(f"PR Merged: {pr.get('merged')}")
                logger.info(f"PR Author: {pr.get('user', {}).get('login', 'unknown')}")
                logger.info(f"PR Author Name: {pr.get('user', {}).get('name', 'N/A')}")
                logger.info(
                    f"PR Author Type: {pr.get('user', {}).get('type', 'unknown')}"
                )
                logger.info(
                    f"PR Base Branch: {pr.get('base', {}).get('ref', 'unknown')}"
                )
                logger.info(
                    f"PR Head Branch: {pr.get('head', {}).get('ref', 'unknown')}"
                )
                logger.info(f"PR Created At: {pr.get('created_at')}")
                logger.info(f"PR Updated At: {pr.get('updated_at')}")
                logger.info(f"PR Merged At: {pr.get('merged_at')}")
                logger.info(f"PR HTML URL: {pr.get('html_url')}")

                # Log additional PR details
                logger.info(f"PR Body Length: {len(pr.get('body', '') or '')}")
                logger.info(
                    f"PR Labels: {[label.get('name') for label in pr.get('labels', [])]}"
                )
                logger.info(
                    f"PR Milestone: {(pr.get('milestone') or {}).get('title', 'None')}"
                )
                logger.info(
                    f"PR Assignees: {[assignee.get('login') for assignee in pr.get('assignees', [])]}"
                )
                logger.info(
                    f"PR Requested Reviewers: {[reviewer.get('login') for reviewer in pr.get('requested_reviewers', [])]}"
                )

                if pr.get("merged_by"):
                    logger.info(
                        f"PR Merged By: {pr.get('merged_by', {}).get('login', 'unknown')}"
                    )

            if "repository" in event:
                repo = event["repository"]
                logger.info("=== Repository Information ===")
                logger.info(f"Repository Name: {repo.get('name')}")
                logger.info(f"Repository Full Name: {repo.get('full_name')}")
                logger.info(f"Repository Private: {repo.get('private')}")
                logger.info(f"Repository Default Branch: {repo.get('default_branch')}")

            if "sender" in event:
                sender = event["sender"]
                logger.info("=== Event Sender Information ===")
                logger.info(f"Sender Login: {sender.get('login')}")
                logger.info(f"Sender Type: {sender.get('type')}")

            logger.info("=== End GitHub Event Data ===")

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
    pr: Dict[str, Any], diff: str, openai_client: OpenAI, config: Config
) -> Dict[str, str]:
    """Generate technical and marketing summaries using OpenAI."""
    # Extract author information
    author_info = pr.get("user", {})
    author_login = author_info.get("login", "unknown")
    author_name = author_info.get("name", "")
    author_display = author_name if author_name else author_login

    # Get merge information
    merged_by_info = pr.get("merged_by", {})
    merged_by_login = merged_by_info.get("login", "unknown")
    merged_by_name = merged_by_info.get("name", "")
    merged_by_display = merged_by_name if merged_by_name else merged_by_login

    # Get branch information
    base_branch = pr.get("base", {}).get("ref", "unknown")
    head_branch = pr.get("head", {}).get("ref", "unknown")

    # Truncate diff to configured length
    diff_excerpt = diff[: config.max_diff_length]

    prompt = f"""You are a technical writer creating PR summaries. 

Analyze this pull request and create two summaries:

PR DETAILS:
Title: {pr["title"]}
Description: {pr.get("body", "")}
Diff (first {config.max_diff_length} chars): {diff_excerpt}

INSTRUCTIONS:
- Create a "technical" summary (2-3 sentences describing what changed technically)
- Create a "marketing" summary (1-2 sentences describing user benefits, or "Minor technical improvements" for basic fixes)
- Do not mention author names in the summaries
- Respond with ONLY a valid JSON object, no other text
- Use this exact format: {{"technical": "your technical summary", "marketing": "your marketing summary"}}

JSON Response:"""

    try:
        logger.info(
            f"Generating summaries for PR #{pr['number']} using {config.openai_model}"
        )

        response = openai_client.chat.completions.create(
            model=config.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that responds only with valid JSON objects.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )

        if not hasattr(response, "choices") or not response.choices:
            raise ValueError("OpenAI response has no choices")

        first_choice = response.choices[0]

        if not hasattr(first_choice, "message"):
            raise ValueError("OpenAI response choice has no message")

        message = first_choice.message
        response_content = message.content

        if not response_content:
            raise ValueError("Empty response content from OpenAI")

        response_content = response_content.strip()

        # Try to extract JSON if there's extra text
        if not response_content.startswith("{"):
            # Find the first { and last }
            start = response_content.find("{")
            end = response_content.rfind("}") + 1
            if start != -1 and end != 0:
                response_content = response_content[start:end]
            else:
                logger.error("Could not find JSON boundaries in response")

        summaries = json.loads(response_content)

        # Validate that we have the required keys
        if "technical" not in summaries or "marketing" not in summaries:
            raise ValueError("Response missing required keys")

        logger.info("Successfully generated AI summaries")
        return summaries

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        try:
            raw_content = (
                response.choices[0].message.content
                if "response" in locals()
                else "No response available"
            )
            logger.error(f"Raw response was: {repr(raw_content)}")
        except:
            logger.error("Could not access raw response content")
        return {"technical": pr["title"], "marketing": "Improvements and updates"}
    except Exception as e:
        logger.error(f"Failed to generate summaries: {e}")
        logger.error(f"Error type: {type(e)}")
        try:
            if "response" in locals():
                logger.error(f"Response object available: {type(response)}")
                if hasattr(response, "choices") and response.choices:
                    raw_content = response.choices[0].message.content
                    logger.error(f"Raw response was: {repr(raw_content)}")
                else:
                    logger.error("Response object has no choices")
            else:
                logger.error("No response object available")
        except Exception as debug_e:
            logger.error(f"Error accessing response for debugging: {debug_e}")
        return {"technical": pr["title"], "marketing": "Improvements and updates"}


def post_to_slack(
    pr: Dict[str, Any], summaries: Dict[str, str], config: Config
) -> bool:
    """Post PR summary to Slack."""
    # Extract author information for Slack message
    author_info = pr.get("user", {})
    author_login = author_info.get("login", "unknown")
    author_name = author_info.get("name", "")
    author_display = author_name if author_name else author_login

    # Get merge information
    merged_by_info = pr.get("merged_by", {})
    merged_by_login = merged_by_info.get("login", "unknown")
    merged_by_name = merged_by_info.get("name", "")
    merged_by_display = merged_by_name if merged_by_name else merged_by_login

    # Get branch information
    base_branch = pr.get("base", {}).get("ref", "main")
    head_branch = pr.get("head", {}).get("ref", "feature")

    # Build the Slack message with author information
    slack_msg = {
        "text": f"🚀 PR #{pr['number']} Merged: {pr['title']}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"**PR #{pr['number']}:** {pr['title']}\n**Author:** {author_display} (@{author_login})\n**Merged by:** {merged_by_display} (@{merged_by_login})\n**Branches:** `{head_branch}` → `{base_branch}`",
                },
            },
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
        response = requests.post(config.slack_webhook, json=slack_msg)
        response.raise_for_status()
        logger.info("Successfully posted to Slack")
        return True
    except Exception as e:
        logger.error(f"Failed to post to Slack: {e}")
        return False


def main() -> None:
    """Main entry point for PR summarization."""
    try:
        # Load and validate configuration
        config = Config.from_env()
        config.validate()

        # Load PR data
        event = load_pr_data(config)

        # Check if we should process this PR
        if not should_process_pr(event):
            logger.info("PR not merged or not closed, skipping")
            return

        pr = event["pull_request"]

        logger.info(f"Processing PR #{pr['number']}: {pr['title']}")

        # Get PR diff
        diff = get_pr_diff(config.github_repository, pr["number"], config.github_token)

        # Generate summaries
        openai_client = OpenAI(api_key=config.openai_api_key)
        summaries = generate_summaries(pr, diff, openai_client, config)

        # Post to Slack
        slack_success = post_to_slack(pr, summaries, config)

        if slack_success:
            logger.info(f"✅ Successfully summarized PR #{pr['number']}")
        else:
            logger.error(f"❌ Failed to complete all operations for PR #{pr['number']}")

    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise


if __name__ == "__main__":
    main()
