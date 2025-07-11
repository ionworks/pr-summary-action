# PR Summary Action

AI-powered PR summaries to Slack using GitHub secrets for secure credential management.

## Quick Setup

### 1. The action is already deployed at `ionworks/pr-summary-action`

No need to create your own repository - just use the public action with GitHub secrets.

### 2. Configure GitHub Secrets

The action uses GitHub secrets for secure credential storage. You need to add these secrets to any repository where you want to use the action:

**Required Secrets:**

- `OPENAI_API_KEY`: Your OpenAI API key (starts with `sk-`)
- `SLACK_WEBHOOK`: Your Slack webhook URL (starts with `https://hooks.slack.com/`)

**How to add secrets:**

1. Go to your repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with the exact names above

### 3. Use Everywhere (One Line!)

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
      - uses: ionworks/pr-summary-action@v1.3
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          slack_webhook: ${{ secrets.SLACK_WEBHOOK }}
```

## Usage Options

### Basic Usage

```yaml
- uses: ionworks/pr-summary-action@v1.3
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    slack_webhook: ${{ secrets.SLACK_WEBHOOK }}
```

### With GPT-4

```yaml
- uses: ionworks/pr-summary-action@v1.3
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    slack_webhook: ${{ secrets.SLACK_WEBHOOK }}
    model: "gpt-4"
```

### Custom Slack Channel

```yaml
- uses: ionworks/pr-summary-action@v1.3
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    slack_webhook: ${{ secrets.SLACK_WEBHOOK }}
    slack_channel: "#team-frontend"
```

### Full Configuration

```yaml
- uses: ionworks/pr-summary-action@v1.3
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    slack_webhook: ${{ secrets.SLACK_WEBHOOK }}
    model: "gpt-4"
    slack_channel: "#releases"
```

## How It Works

1. **Triggers**: When a PR is merged
2. **Analyzes**: Gets PR title, description, and diff
3. **Summarizes**: Uses OpenAI to generate technical and marketing summaries
4. **Posts**: Sends formatted message to Slack with PR link

## Features

- ✅ **Secure credential management** - Uses GitHub secrets for secure storage
- ✅ **One-line setup** - Works across all repos instantly
- ✅ **AI-powered** - Technical and marketing summaries
- ✅ **Slack integration** - Rich formatted messages with buttons
- ✅ **Customizable** - Choose AI model and Slack channel

## Security

The action uses **GitHub secrets** passed as inputs for secure credential storage. Each repository needs to have the required secrets configured in its settings. This ensures credentials are:

- Encrypted and secure
- Repository-specific
- Not exposed in logs or code
- Managed through GitHub's built-in security features
- Explicitly passed (no hidden dependencies)

## Why Use Inputs Instead of Direct Secret Access?

✅ **Explicit**: Clear what secrets the action needs  
✅ **Flexible**: Repositories can use different secret names  
✅ **Reusable**: Works across different organizations  
✅ **Secure**: Follows GitHub Actions best practices  
✅ **Transparent**: Workflow files show exactly what's being passed

## Pro Tips

- Use GPT-4 for critical repositories that need high-quality summaries
- Override Slack channels for different teams/projects
- Add repo-specific logic in `summarize.py` using `os.environ['GITHUB_REPOSITORY']`
- Monitor your OpenAI API usage to manage costs

## Requirements

- GitHub repository with configured secrets
- OpenAI API key
- Slack webhook URL
