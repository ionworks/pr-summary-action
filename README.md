# PR Summary Action

AI-powered PR summaries to Slack and Changelog service with embedded credentials for private use.

## Quick Setup (Private Action)

### 1. Create Private Repository

```bash
gh repo create your-org/pr-summary-action --private
cd pr-summary-action
```

### 2. Configure Credentials

Edit the `action.yml` file and replace the placeholder credentials with your actual values:

```yaml
# Replace these with your actual credentials
OPENAI_API_KEY: "sk-your-actual-key-here"
SLACK_WEBHOOK: "https://hooks.slack.com/your-actual-webhook"
CHANGELOG_WEBHOOK: "https://feedback.ionworks.com/api/changelog" # Optional
```

### 3. Deploy

```bash
git add .
git commit -m "Private PR summary action"
git tag v1
git push origin main --tags
```

### 4. Use Everywhere (One Line!)

In any repo, create `.github/workflows/pr-summary.yml`:

```yaml
name: PR Summary
on:
  pull_request:
    types: [closed]
jobs:
  summary:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: your-org/pr-summary-action@v1
```

## Usage Options

### Basic Usage

```yaml
- uses: your-org/pr-summary-action@v1
```

### With GPT-4

```yaml
- uses: your-org/pr-summary-action@v1
  with:
    model: "gpt-4"
```

### Custom Slack Channel

```yaml
- uses: your-org/pr-summary-action@v1
  with:
    slack_channel: "#team-frontend"
```

### Full Configuration

```yaml
- uses: your-org/pr-summary-action@v1
  with:
    model: "gpt-4"
    slack_channel: "#releases"
```

## How It Works

1. **Triggers**: When a PR is merged
2. **Analyzes**: Gets PR title, description, and diff
3. **Summarizes**: Uses OpenAI to generate technical and marketing summaries
4. **Posts**: Sends formatted message to Slack with PR link
5. **Logs**: Posts to changelog service (if configured)

## Features

- ✅ **No secrets management** - Credentials embedded in private action
- ✅ **One-line setup** - Works across all repos instantly
- ✅ **AI-powered** - Technical and marketing summaries
- ✅ **Slack integration** - Rich formatted messages with buttons
- ✅ **Changelog service** - Optional external logging
- ✅ **Customizable** - Choose AI model and Slack channel

## Security

Since this is a **private repository**, only your organization can use the action with the embedded credentials. This eliminates the need for secret management across multiple repositories.

## Pro Tips

- Use GPT-4 for critical repositories that need high-quality summaries
- Override Slack channels for different teams/projects
- Add repo-specific logic in `summarize.py` using `os.environ['GITHUB_REPOSITORY']`
- Monitor your OpenAI API usage to manage costs

## Requirements

- Private GitHub repository (for credential security)
- OpenAI API key
- Slack webhook URL
- Optional: Changelog service webhook
