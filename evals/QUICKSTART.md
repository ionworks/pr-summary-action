# Quick Start Guide - PR Summary Evaluation System

## Setup

1. **Set environment variables:**

   ```bash
   export GITHUB_TOKEN=your_github_token
   export OPENAI_API_KEY=your_openai_api_key
   ```

2. **Navigate to evals directory:**
   ```bash
   cd evals
   ```

## Basic Usage

### 1. Run Complete Demo

```bash
python examples/run_evaluation_example.py
```

### 2. Using the CLI

#### Build a dataset

**Option 1: Latest merged PRs**

```bash
python eval_cli.py build-dataset microsoft/vscode --limit 10 --output my_dataset.json
```

**Option 2: Specific PR numbers**

```bash
python eval_cli.py build-dataset microsoft/vscode --pr-numbers 123456,123457,123458 --output my_dataset.json
```

#### Run evaluation

```bash
python eval_cli.py evaluate my_dataset.json \
    --prompt-versions default,concise,user_focused \
    --sample-size 5 \
    --export-human-eval \
    --output results/
```

#### Compare results

```bash
python eval_cli.py compare results1/evaluation_results.json results2/evaluation_results.json
```

#### Validate dataset

```bash
python eval_cli.py validate my_dataset.json
```

## Available Commands

- `build-dataset` - Create test dataset from repository PRs
- `evaluate` - Run evaluation with multiple prompt versions
- `compare` - Compare results from different evaluation runs
- `validate` - Check dataset quality

## Output Files

- `evaluation_results.json` - Raw evaluation data
- `evaluation_report.md` - Human-readable report
- `human_evaluation/` - HTML forms for manual evaluation

## Prompt Variations

The system includes 8 built-in prompt variations:

- `default` - Original system prompt
- `concise` - Shorter, direct approach
- `detailed` - Comprehensive guidance
- `user_focused` - Emphasizes user benefits
- `technical_focused` - Technical precision
- `structured` - Clear structure with checkboxes
- `conversational` - Natural, informal language
- `bullet_points` - Bullet point format

## Troubleshooting

1. **Import errors**: Make sure you're running from the `evals` directory
2. **API rate limits**: Reduce sample size or add delays
3. **Large diffs**: Adjust `--max-diff-length` parameter

## Next Steps

1. Start with a small dataset (10-20 PRs)
2. Test 2-3 prompt variations
3. Review automated metrics
4. Complete human evaluation forms
5. Iterate based on results
