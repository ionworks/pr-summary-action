# PR Summary Evaluation System

A comprehensive evaluation framework for testing and improving PR summarization prompts using automated metrics and human evaluation.

## Overview

This evaluation system helps you systematically test different prompt variations for PR summarization by:

- **Building test datasets** from real repository PRs
- **Running automated evaluations** with multiple metrics
- **Generating human evaluation forms** for subjective assessment
- **Comparing prompt variations** with detailed reports
- **Iterating on prompt improvements** based on data

## Quick Start

### Prerequisites

1. **Environment Variables**:

   ```bash
   export GITHUB_TOKEN=your_github_token
   export OPENAI_API_KEY=your_openai_key
   ```

2. **Python Dependencies**:
   ```bash
   pip install openai requests python-dateutil
   ```

### Basic Usage

```bash
# Run the complete evaluation demo
cd evals
python examples/run_evaluation_example.py
```

This will:

1. Build a test dataset from a sample repository
2. Test multiple prompt variations
3. Generate automated metrics
4. Create human evaluation forms
5. Produce a comprehensive report

## Detailed Usage

### 1. Building Test Datasets

Create a dataset from any public repository. You can either use the latest merged PRs or specify exact PR numbers for targeted testing:

```python
# From the evals directory
from evaluation import TestDatasetBuilder

# Initialize builder
builder = TestDatasetBuilder(github_token="your_token")

# Option 1: Build dataset from latest merged PRs
test_cases = builder.build_dataset_from_repo("owner/repo", limit=50)

# Option 2: Build dataset from specific PR numbers
specific_prs = [123456, 123457, 123458]
test_cases = builder.build_dataset_from_repo("owner/repo", pr_numbers=specific_prs)

# Save dataset
builder.save_dataset(test_cases, "my_dataset.json")
```

**CLI Usage:**

```bash
cd evals
python eval_cli.py build-dataset microsoft/vscode \
    --limit 20 \
    --output vscode_dataset.json
```

**Or with specific PR numbers:**

```bash
cd evals
python eval_cli.py build-dataset microsoft/vscode \
    --pr-numbers 123456,123457,123458 \
    --output vscode_dataset.json
```

### 2. Running Evaluations

Test different prompt variations:

```python
# From the evals directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evaluation import EvaluationRunner
from pr_summary_action.config import Config

# Setup configuration
config = Config(
    openai_api_key="your_key",
    openai_model="gpt-4o-mini",
    max_tokens=500,
    temperature=0.3,
    max_diff_length=8000,
    github_token="your_token",
    # ... other config
)

# Load test cases
builder = TestDatasetBuilder("")
test_cases = builder.load_dataset("my_dataset.json")

# Run evaluation
runner = EvaluationRunner(config)
results = runner.run_evaluation(test_cases, ["default", "concise", "user_focused"])
```

**CLI Usage:**

```bash
cd evals
python eval_cli.py evaluate my_dataset.json \
    --prompt-versions default,concise,user_focused \
    --sample-size 10 \
    --export-human-eval \
    --output results/
```

### 3. Available Prompt Variations

The system includes 8 built-in prompt variations:

| Variation           | Description                     | Style      | Focus         |
| ------------------- | ------------------------------- | ---------- | ------------- |
| `default`           | Original system prompt          | Formal     | Balanced      |
| `concise`           | Shorter, direct approach        | Minimal    | Brevity       |
| `detailed`          | Comprehensive guidance          | Formal     | Completeness  |
| `user_focused`      | Emphasizes user benefits        | Business   | User Impact   |
| `technical_focused` | Technical precision             | Technical  | Accuracy      |
| `structured`        | Clear structure with checkboxes | Structured | Organization  |
| `conversational`    | Natural, informal language      | Casual     | Accessibility |
| `bullet_points`     | Bullet point format             | Formatted  | Readability   |

### 4. Understanding Metrics

#### Automated Metrics

- **Length**: Character/word count of summaries
- **Readability**: Simplified readability score (0-1)
- **Keyword Coverage**: Percentage of relevant keywords covered
- **Diff Relevance**: How well summary relates to actual changes
- **Factual Consistency**: Basic factual accuracy checks

#### Human Evaluation Metrics

- **Technical Summary**: Accuracy, Completeness, Clarity (1-5 scale)
- **Marketing Summary**: Appeal, Accuracy, Clarity (1-5 scale)
- **Overall Assessment**: Qualitative feedback

### 5. Analyzing Results

#### Automated Report

The system generates a comprehensive report including:

```markdown
# PR Summary Evaluation Report

## Summary Statistics

- Average lengths by prompt variation
- Generation times
- Readability scores
- Test case coverage

## Results by Category

- Performance breakdown by PR type (feature, bugfix, etc.)
- Difficulty analysis (easy, medium, hard)
```

#### Human Evaluation

HTML forms are generated for each test case:

- Side-by-side comparison of summaries
- Rating scales for key metrics
- Text areas for detailed feedback
- Structured evaluation workflow

### 6. Comparing Prompt Versions

```bash
# Compare results from multiple evaluation runs
cd evals
python eval_cli.py compare \
    results1/evaluation_results.json \
    results2/evaluation_results.json \
    --output comparison_report.md
```

## Advanced Usage

### Custom Prompt Variations

Create your own prompt variations:

```python
from pr_summary_action.prompt_variations import get_prompt_variations

# Add custom prompt
custom_prompts = get_prompt_variations()
custom_prompts["my_custom"] = """
Your custom prompt template here...
Title: {title}
Description: {body}
Changes: {diff_excerpt}
"""
```

### Custom Metrics

Extend the automated evaluator:

```python
from pr_summary_action.evaluation import AutomatedEvaluator

class CustomEvaluator(AutomatedEvaluator):
    def evaluate_summary(self, summary, summary_type, test_case):
        metrics = super().evaluate_summary(summary, summary_type, test_case)

        # Add custom metrics
        metrics['custom_score'] = self.calculate_custom_score(summary)

        return metrics
```

### Filtering Test Cases

Filter test cases by criteria:

```python
# Filter by category
feature_cases = [tc for tc in test_cases if tc.category == "feature"]

# Filter by difficulty
easy_cases = [tc for tc in test_cases if tc.difficulty == "easy"]

# Filter by repository
specific_repo_cases = [tc for tc in test_cases if "specific-repo" in tc.repo]
```

## Best Practices

### Dataset Quality

1. **Diverse PRs**: Include various types (features, bugfixes, docs)
2. **Size Range**: Mix of small and large PRs
3. **Repository Variety**: Test across different codebases
4. **Recency**: Use recent PRs for relevance

### Evaluation Strategy

1. **Start Small**: Begin with 10-20 test cases
2. **Iterate Quickly**: Test 2-3 prompt variations initially
3. **Automated First**: Use automated metrics for quick feedback
4. **Human Validation**: Follow up with human evaluation
5. **Statistical Significance**: Use enough samples for reliable results

### Prompt Development

1. **Hypothesis-Driven**: Have clear goals for each variation
2. **Single Changes**: Modify one aspect at a time
3. **Document Rationale**: Keep notes on why each variation exists
4. **A/B Testing**: Compare variations systematically

## Troubleshooting

### Common Issues

1. **API Rate Limits**:

   - Use delays between requests
   - Consider using multiple API keys
   - Reduce batch sizes

2. **Large Diffs**:

   - Adjust `max_diff_length` parameter
   - Filter out very large PRs
   - Use diff summarization

3. **JSON Parsing Errors**:
   - Check prompt formatting
   - Validate OpenAI responses
   - Add error handling

### Performance Tips

1. **Parallel Processing**: Run evaluations in parallel where possible
2. **Caching**: Cache API responses to avoid repeated calls
3. **Sampling**: Use representative samples for large datasets
4. **Incremental**: Build datasets incrementally

## Integration

### CI/CD Pipeline

Integrate evaluations into your development workflow:

```yaml
# .github/workflows/eval.yml
name: Prompt Evaluation
on:
  pull_request:
    paths: ["src/pr_summary_action/prompt_variations.py"]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Evaluation
        run: python -m pr_summary_action.eval_cli evaluate dataset.json
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Monitoring

Track prompt performance over time:

```python
# Add to your monitoring system
def track_prompt_metrics(results):
    for result in results['results']:
        metrics = result['metrics']
        log_metric('prompt_performance', {
            'version': result['prompt_version'],
            'technical_length': metrics['technical_length'],
            'marketing_length': metrics['marketing_length'],
            'readability': metrics['technical_readability_score']
        })
```

## Examples

See the `examples/` directory for:

- **Complete evaluation workflow**
- **Custom prompt variations**
- **Advanced filtering and analysis**
- **Integration patterns**

## Contributing

To add new prompt variations:

1. Add to `prompt_variations.py`
2. Update metadata in `get_prompt_metadata()`
3. Add tests for new variations
4. Update documentation

## License

This evaluation system is part of the PR Summary Action project and follows the same license terms.
