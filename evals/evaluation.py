"""Evaluation framework for PR summarization prompts."""

import json
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from openai import OpenAI
import sys
from pathlib import Path

# Add the src directory to the path so we can import the main modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pr_summary_action.config import Config
from pr_summary_action.summarize import get_pr_diff
from prompt_variations import get_prompt_by_name, format_prompt, get_prompt_metadata


logger = logging.getLogger(__name__)


def generate_summaries_with_prompt(
    pr: Dict[str, Any],
    diff: str,
    openai_client: OpenAI,
    config: Config,
    prompt_version: str = "default",
) -> Dict[str, str]:
    """Generate summaries using a specific prompt variation."""
    # Get the prompt template
    prompt_template = get_prompt_by_name(prompt_version)

    # Truncate diff to configured length
    diff_excerpt = diff[: config.max_diff_length]

    # Format the prompt
    prompt = format_prompt(prompt_template, pr, diff_excerpt, config.max_diff_length)

    try:
        logger.info(
            f"Generating summaries for PR #{pr['number']} using {config.openai_model} with prompt: {prompt_version}"
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

        logger.info(
            f"Successfully generated AI summaries using prompt: {prompt_version}"
        )
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


@dataclass
class EvaluationMetrics:
    """Metrics for evaluating PR summaries."""

    # Automated metrics
    technical_length: float
    marketing_length: float
    technical_readability_score: float
    marketing_readability_score: float
    keyword_coverage: float

    # Human evaluation scores (1-5 scale)
    technical_accuracy: Optional[int] = None
    technical_completeness: Optional[int] = None
    technical_clarity: Optional[int] = None
    marketing_appeal: Optional[int] = None
    marketing_accuracy: Optional[int] = None
    marketing_clarity: Optional[int] = None

    # Overall scores
    overall_technical: Optional[float] = None
    overall_marketing: Optional[float] = None

    # Metadata
    evaluation_time: float = 0.0
    model_used: str = ""
    prompt_version: str = ""
    evaluator_id: str = ""


@dataclass
class PRTestCase:
    """Test case for PR evaluation."""

    id: str
    pr_number: int
    title: str
    body: str
    diff: str
    author: str
    repo: str
    labels: List[str]

    # Expected outputs (for golden dataset)
    expected_technical: Optional[str] = None
    expected_marketing: Optional[str] = None

    # Metadata
    difficulty: str = "medium"  # easy, medium, hard
    category: str = "general"  # feature, bugfix, refactor, docs, etc.

    @classmethod
    def from_github_pr(cls, pr_data: Dict[str, Any], diff: str) -> "PRTestCase":
        """Create test case from GitHub PR data."""
        return cls(
            id=f"pr_{pr_data['number']}_{pr_data['base']['repo']['name']}",
            pr_number=pr_data["number"],
            title=pr_data["title"],
            body=pr_data.get("body", ""),
            diff=diff,
            author=pr_data["user"]["login"],
            repo=pr_data["base"]["repo"]["full_name"],
            labels=[label["name"] for label in pr_data.get("labels", [])],
            difficulty=cls._infer_difficulty(pr_data, diff),
            category=cls._infer_category(pr_data),
        )

    @staticmethod
    def _infer_difficulty(pr_data: Dict[str, Any], diff: str) -> str:
        """Infer difficulty based on PR characteristics."""
        # Simple heuristics
        lines_changed = diff.count("\n")
        files_changed = diff.count("diff --git")

        if lines_changed > 500 or files_changed > 10:
            return "hard"
        elif lines_changed > 100 or files_changed > 3:
            return "medium"
        else:
            return "easy"

    @staticmethod
    def _infer_category(pr_data: Dict[str, Any]) -> str:
        """Infer category based on PR title and labels."""
        title = pr_data["title"].lower()
        labels = [label["name"].lower() for label in pr_data.get("labels", [])]

        # Check labels first
        if any(label in ["bug", "bugfix", "fix"] for label in labels):
            return "bugfix"
        elif any(label in ["feature", "enhancement"] for label in labels):
            return "feature"
        elif any(label in ["refactor", "refactoring"] for label in labels):
            return "refactor"
        elif any(label in ["docs", "documentation"] for label in labels):
            return "docs"

        # Check title
        if any(word in title for word in ["fix", "bug", "error", "issue"]):
            return "bugfix"
        elif any(word in title for word in ["add", "feature", "implement", "new"]):
            return "feature"
        elif any(word in title for word in ["refactor", "cleanup", "improve"]):
            return "refactor"
        elif any(word in title for word in ["doc", "readme", "comment"]):
            return "docs"

        return "general"


class AutomatedEvaluator:
    """Automated evaluation of PR summaries."""

    def __init__(self):
        self.technical_keywords = [
            "function",
            "method",
            "class",
            "variable",
            "api",
            "endpoint",
            "database",
            "query",
            "algorithm",
            "implementation",
            "architecture",
            "performance",
            "optimization",
            "refactor",
            "bug",
            "fix",
            "test",
        ]

        self.marketing_keywords = [
            "user",
            "customer",
            "experience",
            "improve",
            "better",
            "faster",
            "easier",
            "new",
            "feature",
            "benefit",
            "value",
            "quality",
            "performance",
            "reliable",
            "secure",
            "efficient",
        ]

    def evaluate_summary(
        self, summary: str, summary_type: str, test_case: PRTestCase
    ) -> Dict[str, float]:
        """Evaluate a single summary with automated metrics."""
        metrics = {}

        # Length metrics
        metrics["length"] = float(len(summary))
        metrics["word_count"] = float(len(summary.split()))

        # Readability (simplified)
        metrics["readability_score"] = self._calculate_readability(summary)

        # Keyword coverage
        relevant_keywords = (
            self.technical_keywords
            if summary_type == "technical"
            else self.marketing_keywords
        )
        metrics["keyword_coverage"] = self._calculate_keyword_coverage(
            summary, relevant_keywords
        )

        # Diff relevance (how well summary relates to the actual changes)
        metrics["diff_relevance"] = self._calculate_diff_relevance(
            summary, test_case.diff
        )

        # Factual consistency (basic checks)
        metrics["factual_consistency"] = self._check_factual_consistency(
            summary, test_case
        )

        return metrics

    def _calculate_readability(self, text: str) -> float:
        """Calculate a simplified readability score."""
        if not text:
            return 0.0

        sentences = text.count(".") + text.count("!") + text.count("?")
        if sentences == 0:
            sentences = 1

        words = len(text.split())
        avg_sentence_length = words / sentences

        # Simplified readability (lower is better, normalize to 0-1)
        # Good range is 15-20 words per sentence
        if 10 <= avg_sentence_length <= 25:
            return 1.0
        elif avg_sentence_length < 10:
            return 0.8
        else:
            return max(0.2, 1.0 - (avg_sentence_length - 25) / 50)

    def _calculate_keyword_coverage(self, summary: str, keywords: List[str]) -> float:
        """Calculate what percentage of relevant keywords are covered."""
        summary_lower = summary.lower()
        found_keywords = sum(1 for keyword in keywords if keyword in summary_lower)
        return found_keywords / len(keywords) if keywords else 0.0

    def _calculate_diff_relevance(self, summary: str, diff: str) -> float:
        """Calculate how relevant the summary is to the actual diff."""
        if not diff:
            return 0.0

        # Extract file extensions and function names from diff
        diff_tokens = set()

        # File extensions
        import re

        files = re.findall(r"\+\+\+ b/(.+)", diff)
        for file in files:
            if "." in file:
                ext = file.split(".")[-1]
                diff_tokens.add(ext)

        # Function/method names (simplified)
        functions = re.findall(r"def (\w+)|function (\w+)|class (\w+)", diff)
        for func_match in functions:
            for func in func_match:
                if func:
                    diff_tokens.add(func.lower())

        # Check if summary mentions relevant terms
        summary_lower = summary.lower()
        relevant_mentions = sum(1 for token in diff_tokens if token in summary_lower)

        return relevant_mentions / len(diff_tokens) if diff_tokens else 0.5

    def _check_factual_consistency(self, summary: str, test_case: PRTestCase) -> float:
        """Check for basic factual consistency."""
        score = 1.0

        # Check if summary mentions incorrect file types
        if "python" in summary.lower() and not any(
            f.endswith(".py") for f in test_case.diff
        ):
            score -= 0.2

        # Check if summary mentions wrong operation type
        if "add" in summary.lower() and test_case.diff.count(
            "---"
        ) > test_case.diff.count("+++"):
            score -= 0.1

        return max(0.0, score)


class HumanEvaluationTemplate:
    """Templates and tools for human evaluation."""

    @staticmethod
    def generate_evaluation_form(
        test_case: PRTestCase, summaries: Dict[str, str]
    ) -> str:
        """Generate an HTML evaluation form."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PR Summary Evaluation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .pr-info {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .summary {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .evaluation {{ background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; }}
                .rating {{ margin: 10px 0; }}
                .scale {{ font-size: 12px; color: #666; }}
                textarea {{ width: 100%; height: 80px; }}
                button {{ background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>PR Summary Evaluation</h1>
            
            <div class="pr-info">
                <h3>PR #{test_case.pr_number}: {test_case.title}</h3>
                <p><strong>Repository:</strong> {test_case.repo}</p>
                <p><strong>Author:</strong> {test_case.author}</p>
                <p><strong>Category:</strong> {test_case.category}</p>
                <p><strong>Difficulty:</strong> {test_case.difficulty}</p>
                <p><strong>Labels:</strong> {", ".join(test_case.labels)}</p>
                <details>
                    <summary>PR Description</summary>
                    <pre>{test_case.body}</pre>
                </details>
                <details>
                    <summary>Diff (first 2000 chars)</summary>
                    <pre>{test_case.diff[:2000]}...</pre>
                </details>
            </div>
            
            <div class="summary">
                <h3>Technical Summary</h3>
                <p>{summaries["technical"]}</p>
            </div>
            
            <div class="evaluation">
                <h4>Technical Summary Evaluation</h4>
                <div class="rating">
                    <label>Accuracy (1-5):</label>
                    <select name="technical_accuracy">
                        <option value="1">1 - Very Inaccurate</option>
                        <option value="2">2 - Mostly Inaccurate</option>
                        <option value="3">3 - Somewhat Accurate</option>
                        <option value="4">4 - Mostly Accurate</option>
                        <option value="5">5 - Very Accurate</option>
                    </select>
                </div>
                <div class="rating">
                    <label>Completeness (1-5):</label>
                    <select name="technical_completeness">
                        <option value="1">1 - Missing Key Info</option>
                        <option value="2">2 - Some Key Info Missing</option>
                        <option value="3">3 - Adequate Coverage</option>
                        <option value="4">4 - Good Coverage</option>
                        <option value="5">5 - Comprehensive</option>
                    </select>
                </div>
                <div class="rating">
                    <label>Clarity (1-5):</label>
                    <select name="technical_clarity">
                        <option value="1">1 - Very Confusing</option>
                        <option value="2">2 - Somewhat Confusing</option>
                        <option value="3">3 - Understandable</option>
                        <option value="4">4 - Clear</option>
                        <option value="5">5 - Very Clear</option>
                    </select>
                </div>
                <div>
                    <label>Technical Summary Feedback:</label>
                    <textarea name="technical_feedback" placeholder="What could be improved?"></textarea>
                </div>
            </div>
            
            <div class="summary">
                <h3>Marketing Summary</h3>
                <p>{summaries["marketing"]}</p>
            </div>
            
            <div class="evaluation">
                <h4>Marketing Summary Evaluation</h4>
                <div class="rating">
                    <label>Appeal (1-5):</label>
                    <select name="marketing_appeal">
                        <option value="1">1 - No Appeal</option>
                        <option value="2">2 - Little Appeal</option>
                        <option value="3">3 - Some Appeal</option>
                        <option value="4">4 - Good Appeal</option>
                        <option value="5">5 - Very Appealing</option>
                    </select>
                </div>
                <div class="rating">
                    <label>Accuracy (1-5):</label>
                    <select name="marketing_accuracy">
                        <option value="1">1 - Very Inaccurate</option>
                        <option value="2">2 - Mostly Inaccurate</option>
                        <option value="3">3 - Somewhat Accurate</option>
                        <option value="4">4 - Mostly Accurate</option>
                        <option value="5">5 - Very Accurate</option>
                    </select>
                </div>
                <div class="rating">
                    <label>Clarity (1-5):</label>
                    <select name="marketing_clarity">
                        <option value="1">1 - Very Confusing</option>
                        <option value="2">2 - Somewhat Confusing</option>
                        <option value="3">3 - Understandable</option>
                        <option value="4">4 - Clear</option>
                        <option value="5">5 - Very Clear</option>
                    </select>
                </div>
                <div>
                    <label>Marketing Summary Feedback:</label>
                    <textarea name="marketing_feedback" placeholder="What could be improved?"></textarea>
                </div>
            </div>
            
            <div class="evaluation">
                <h4>Overall Assessment</h4>
                <div>
                    <label>Overall Comments:</label>
                    <textarea name="overall_feedback" placeholder="General feedback about both summaries"></textarea>
                </div>
                <div>
                    <label>Evaluator ID:</label>
                    <input type="text" name="evaluator_id" placeholder="Your identifier">
                </div>
                <button onclick="submitEvaluation()">Submit Evaluation</button>
            </div>
            
            <script>
                function submitEvaluation() {{
                    const form = document.forms[0];
                    const data = new FormData(form);
                    const evaluation = {{}};
                    for (let [key, value] of data.entries()) {{
                        evaluation[key] = value;
                    }}
                    evaluation.test_case_id = '{test_case.id}';
                    evaluation.timestamp = new Date().toISOString();
                    
                    // In a real implementation, you'd send this to your evaluation endpoint
                    console.log('Evaluation data:', evaluation);
                    alert('Evaluation submitted (check console for data)');
                }}
            </script>
        </body>
        </html>
        """
        return html


class EvaluationRunner:
    """Main evaluation runner for PR summaries."""

    def __init__(self, config: Config):
        self.config = config
        self.openai_client = OpenAI(api_key=config.openai_api_key)
        self.automated_evaluator = AutomatedEvaluator()
        self.results: List[Dict[str, Any]] = []

    def run_evaluation(
        self, test_cases: List[PRTestCase], prompt_versions: List[str]
    ) -> Dict[str, Any]:
        """Run complete evaluation across test cases and prompt versions."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_cases_count": len(test_cases),
            "prompt_versions": prompt_versions,
            "results": [],
        }

        for prompt_version in prompt_versions:
            logger.info(f"Evaluating prompt version: {prompt_version}")

            for test_case in test_cases:
                logger.info(f"Processing test case: {test_case.id}")

                # Generate summaries with current prompt
                pr_data = self._convert_test_case_to_pr_data(test_case)

                start_time = datetime.now()
                summaries = generate_summaries_with_prompt(
                    pr_data,
                    test_case.diff,
                    self.openai_client,
                    self.config,
                    prompt_version,
                )
                end_time = datetime.now()

                evaluation_time = (end_time - start_time).total_seconds()

                # Run automated evaluation
                tech_metrics = self.automated_evaluator.evaluate_summary(
                    summaries["technical"], "technical", test_case
                )
                marketing_metrics = self.automated_evaluator.evaluate_summary(
                    summaries["marketing"], "marketing", test_case
                )

                # Create evaluation metrics
                metrics = EvaluationMetrics(
                    technical_length=tech_metrics["length"],
                    marketing_length=marketing_metrics["length"],
                    technical_readability_score=tech_metrics["readability_score"],
                    marketing_readability_score=marketing_metrics["readability_score"],
                    keyword_coverage=(
                        tech_metrics["keyword_coverage"]
                        + marketing_metrics["keyword_coverage"]
                    )
                    / 2,
                    evaluation_time=evaluation_time,
                    model_used=self.config.openai_model,
                    prompt_version=prompt_version,
                )

                result = {
                    "test_case_id": test_case.id,
                    "prompt_version": prompt_version,
                    "summaries": summaries,
                    "metrics": asdict(metrics),
                    "automated_scores": {
                        "technical": tech_metrics,
                        "marketing": marketing_metrics,
                    },
                    "test_case_metadata": {
                        "difficulty": test_case.difficulty,
                        "category": test_case.category,
                        "repo": test_case.repo,
                    },
                }

                results["results"].append(result)
                self.results.append(result)

        return results

    def _convert_test_case_to_pr_data(self, test_case: PRTestCase) -> Dict[str, Any]:
        """Convert test case back to PR data format for generate_summaries."""
        return {
            "number": test_case.pr_number,
            "title": test_case.title,
            "body": test_case.body,
            "user": {"login": test_case.author, "name": ""},
            "merged_by": {"login": test_case.author, "name": ""},
            "base": {"ref": "main"},
            "head": {"ref": "feature"},
            "html_url": f"https://github.com/{test_case.repo}/pull/{test_case.pr_number}",
        }

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive evaluation report."""
        report = f"""
# PR Summary Evaluation Report

**Generated:** {results["timestamp"]}
**Test Cases:** {results["test_cases_count"]}
**Prompt Versions:** {len(results["prompt_versions"])}

## Summary Statistics

"""

        # Calculate aggregate metrics
        for prompt_version in results["prompt_versions"]:
            version_results = [
                r for r in results["results"] if r["prompt_version"] == prompt_version
            ]

            if not version_results:
                continue

            # Calculate averages
            avg_tech_length = statistics.mean(
                [r["metrics"]["technical_length"] for r in version_results]
            )
            avg_marketing_length = statistics.mean(
                [r["metrics"]["marketing_length"] for r in version_results]
            )
            avg_evaluation_time = statistics.mean(
                [r["metrics"]["evaluation_time"] for r in version_results]
            )
            avg_readability = statistics.mean(
                [
                    (
                        r["metrics"]["technical_readability_score"]
                        + r["metrics"]["marketing_readability_score"]
                    )
                    / 2
                    for r in version_results
                ]
            )

            report += f"""
### Prompt Version: {prompt_version}

- **Average Technical Length:** {avg_tech_length:.1f} characters
- **Average Marketing Length:** {avg_marketing_length:.1f} characters
- **Average Generation Time:** {avg_evaluation_time:.2f} seconds
- **Average Readability Score:** {avg_readability:.2f}
- **Test Cases Processed:** {len(version_results)}

"""

        # Add detailed breakdown by category
        report += "\n## Results by Category\n"

        categories = set(
            r["test_case_metadata"]["category"] for r in results["results"]
        )
        for category in categories:
            category_results = [
                r
                for r in results["results"]
                if r["test_case_metadata"]["category"] == category
            ]

            report += f"\n### {category.title()} ({len(category_results)} test cases)\n"

            for prompt_version in results["prompt_versions"]:
                version_category_results = [
                    r for r in category_results if r["prompt_version"] == prompt_version
                ]
                if version_category_results:
                    avg_keyword_coverage = statistics.mean(
                        [
                            r["metrics"]["keyword_coverage"]
                            for r in version_category_results
                        ]
                    )
                    report += f"- **{prompt_version}:** {avg_keyword_coverage:.2f} keyword coverage\n"

        return report

    def export_for_human_evaluation(
        self, results: Dict[str, Any], output_dir: str
    ) -> None:
        """Export results for human evaluation."""
        import os

        os.makedirs(output_dir, exist_ok=True)

        # Create evaluation forms
        for result in results["results"]:
            test_case_id = result["test_case_id"]
            summaries = result["summaries"]

            # Find the original test case
            test_case = None
            for tc in getattr(self, "current_test_cases", []):
                if tc.id == test_case_id:
                    test_case = tc
                    break

            if test_case:
                html_form = HumanEvaluationTemplate.generate_evaluation_form(
                    test_case, summaries
                )

                with open(
                    os.path.join(output_dir, f"{test_case_id}_evaluation.html"), "w"
                ) as f:
                    f.write(html_form)

        # Create summary report
        report = self.generate_report(results)
        with open(os.path.join(output_dir, "evaluation_report.md"), "w") as f:
            f.write(report)

        logger.info(f"Evaluation files exported to {output_dir}")


class TestDatasetBuilder:
    """Builder for creating test datasets from real PRs."""

    def __init__(self, github_token: str):
        self.github_token = github_token

    def build_dataset_from_repo(
        self, repo: str, limit: int = 50, pr_numbers: Optional[List[int]] = None
    ) -> List[PRTestCase]:
        """Build a test dataset from a repository's merged PRs.

        Args:
            repo: Repository in format "owner/repo"
            limit: Maximum number of PRs to fetch (ignored if pr_numbers is provided)
            pr_numbers: Specific PR numbers to include (if provided, limit is ignored)
        """
        test_cases = []

        if pr_numbers:
            # Fetch specific PRs by number
            logger.info(f"Fetching specific PRs: {pr_numbers}")

            for pr_number in pr_numbers:
                try:
                    # Get individual PR
                    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
                    response = requests.get(
                        pr_url,
                        headers={
                            "Authorization": f"token {self.github_token}",
                            "Accept": "application/vnd.github.v3+json",
                        },
                    )

                    if response.status_code != 200:
                        logger.error(
                            f"Failed to fetch PR #{pr_number}: {response.status_code}"
                        )
                        continue

                    pr = response.json()

                    # Check if PR was merged
                    if not pr.get("merged_at"):
                        logger.warning(f"PR #{pr_number} was not merged, skipping")
                        continue

                    # Get PR diff
                    diff = get_pr_diff(repo, pr["number"], self.github_token)

                    # Create test case
                    test_case = PRTestCase.from_github_pr(pr, diff)
                    test_cases.append(test_case)

                    logger.info(f"Added test case: {test_case.id}")

                except Exception as e:
                    logger.error(f"Failed to process PR #{pr_number}: {e}")
                    continue
        else:
            # Get merged PRs using existing logic
            url = f"https://api.github.com/repos/{repo}/pulls"
            params = {
                "state": "closed",
                "per_page": limit,
                "sort": "updated",
                "direction": "desc",
            }

            response = requests.get(
                url,
                params=params,
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            if response.status_code != 200:
                logger.error(f"Failed to fetch PRs: {response.status_code}")
                return test_cases

            prs = response.json()
            merged_prs = [pr for pr in prs if pr.get("merged_at")]

            logger.info(f"Found {len(merged_prs)} merged PRs")

            for pr in merged_prs[:limit]:
                try:
                    # Get PR diff
                    diff = get_pr_diff(repo, pr["number"], self.github_token)

                    # Create test case
                    test_case = PRTestCase.from_github_pr(pr, diff)
                    test_cases.append(test_case)

                    logger.info(f"Added test case: {test_case.id}")

                except Exception as e:
                    logger.error(f"Failed to process PR {pr['number']}: {e}")
                    continue

        return test_cases

    def save_dataset(self, test_cases: List[PRTestCase], filepath: str) -> None:
        """Save test dataset to file."""
        data = {
            "created_at": datetime.now().isoformat(),
            "test_cases": [asdict(tc) for tc in test_cases],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(test_cases)} test cases to {filepath}")

    def load_dataset(self, filepath: str) -> List[PRTestCase]:
        """Load test dataset from file."""
        with open(filepath) as f:
            data = json.load(f)

        test_cases = []
        for tc_data in data["test_cases"]:
            test_case = PRTestCase(**tc_data)
            test_cases.append(test_case)

        logger.info(f"Loaded {len(test_cases)} test cases from {filepath}")
        return test_cases
