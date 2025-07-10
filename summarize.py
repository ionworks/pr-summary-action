import os, json, requests
from openai import OpenAI

# Load PR data
with open(os.environ["GITHUB_EVENT_PATH"]) as f:
    event = json.load(f)

pr = event["pull_request"]
if event["action"] != "closed" or not pr["merged"]:
    exit()

# Get PR diff
repo = os.environ["GITHUB_REPOSITORY"]
diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr['number']}"
diff_resp = requests.get(
    diff_url,
    headers={
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3.diff",
    },
)

# Generate summaries with OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
prompt = f"""
Analyze this PR and create summaries:

Title: {pr["title"]}
Description: {pr.get("body", "")}
Diff: {diff_resp.text[:3000]}...

Return JSON:
{{"technical": "2-3 sentence technical summary", "marketing": "1-2 sentence user benefit"}}
"""

response = client.chat.completions.create(
    model=os.environ["MODEL"],
    messages=[{"role": "user", "content": prompt}],
    max_tokens=200,
)

try:
    summaries = json.loads(response.choices[0].message.content)
except:
    summaries = {"technical": pr["title"], "marketing": "Improvements and updates"}

# Post to Slack
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

requests.post(os.environ["SLACK_WEBHOOK"], json=slack_msg)

# Post to changelog
changelog_data = {
    "title": pr["title"],
    "content": summaries["marketing"],
    "date": pr["merged_at"],
    "pr_url": pr["html_url"],
}

if os.environ.get("CHANGELOG_WEBHOOK"):
    requests.post(os.environ["CHANGELOG_WEBHOOK"], json=changelog_data)

print(f"✅ Summarized PR #{pr['number']}")
