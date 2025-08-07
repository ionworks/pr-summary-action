#!/usr/bin/env python3
"""Command-line interface for PR summary evaluation."""

import argparse
import os
import json
import logging
from pathlib import Path
from typing import List

import sys
from pathlib import Path

# Add the src directory to the path so we can import the main modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pr_summary_action.config import Config
from evaluation import (
    EvaluationRunner,
    TestDatasetBuilder,
    PRTestCase,
    HumanEvaluationTemplate,
)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def cmd_build_dataset(args):
    """Build test dataset from repository."""
    if not args.github_token:
        print("Error: GitHub token required for dataset building")
        return 1

    builder = TestDatasetBuilder(args.github_token)

    # Parse PR numbers if provided
    pr_numbers = None
    if args.pr_numbers:
        try:
            pr_numbers = [int(pr.strip()) for pr in args.pr_numbers.split(",")]
            print(f"Building dataset from {args.repo} with specific PRs: {pr_numbers}")
        except ValueError:
            print(
                "Error: PR numbers must be comma-separated integers (e.g., 123,456,789)"
            )
            return 1
    else:
        print(f"Building dataset from {args.repo} (limit: {args.limit})")

    test_cases = builder.build_dataset_from_repo(args.repo, args.limit, pr_numbers)

    if not test_cases:
        print("No test cases created")
        return 1

    builder.save_dataset(test_cases, args.output)
    print(f"Created dataset with {len(test_cases)} test cases")
    print(f"Saved to: {args.output}")

    # Show categories breakdown
    categories = {}
    difficulties = {}
    for tc in test_cases:
        categories[tc.category] = categories.get(tc.category, 0) + 1
        difficulties[tc.difficulty] = difficulties.get(tc.difficulty, 0) + 1

    print("\nDataset breakdown:")
    print("Categories:", categories)
    print("Difficulties:", difficulties)

    return 0


def cmd_run_evaluation(args):
    """Run evaluation on test dataset."""
    if not args.openai_api_key:
        print("Error: OpenAI API key required for evaluation")
        return 1

    # Load configuration
    config = Config(
        openai_api_key=args.openai_api_key,
        openai_model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        max_diff_length=args.max_diff_length,
        github_token=args.github_token or "",
        slack_webhook="",  # Not needed for evaluation
        github_repository="",  # Not needed for evaluation
        github_event_path="",  # Not needed for evaluation
        enable_debugging=args.verbose,
    )

    # Load test dataset
    builder = TestDatasetBuilder("")
    test_cases = builder.load_dataset(args.dataset)

    if args.sample_size and args.sample_size < len(test_cases):
        print(f"Using sample of {args.sample_size} test cases")
        test_cases = test_cases[: args.sample_size]

    # Define prompt versions to test
    prompt_versions = (
        args.prompt_versions.split(",") if args.prompt_versions else ["default"]
    )

    # Run evaluation
    runner = EvaluationRunner(config)
    runner.current_test_cases = test_cases  # Store for human evaluation export

    print(f"Running evaluation on {len(test_cases)} test cases")
    print(f"Testing {len(prompt_versions)} prompt versions: {prompt_versions}")

    results = runner.run_evaluation(test_cases, prompt_versions)

    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    # Save raw results
    with open(output_dir / "evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Generate and save report
    report = runner.generate_report(results)
    with open(output_dir / "evaluation_report.md", "w") as f:
        f.write(report)

    # Export for human evaluation if requested
    if args.export_human_eval:
        human_eval_dir = output_dir / "human_evaluation"
        runner.export_for_human_evaluation(results, str(human_eval_dir))
        print(f"Human evaluation forms exported to: {human_eval_dir}")

    print(f"Evaluation complete. Results saved to: {output_dir}")
    print(f"Report: {output_dir / 'evaluation_report.md'}")

    return 0


def cmd_compare_prompts(args):
    """Compare multiple prompt versions."""
    if not args.results_files:
        print("Error: At least one results file required")
        return 1

    all_results = []
    for results_file in args.results_files:
        with open(results_file) as f:
            results = json.load(f)
            all_results.extend(results["results"])

    # Group by prompt version
    prompt_versions = {}
    for result in all_results:
        version = result["prompt_version"]
        if version not in prompt_versions:
            prompt_versions[version] = []
        prompt_versions[version].append(result)

    # Generate comparison report
    report = "# Prompt Version Comparison\n\n"

    for version, version_results in prompt_versions.items():
        if not version_results:
            continue

        # Calculate metrics
        avg_tech_length = sum(
            r["metrics"]["technical_length"] for r in version_results
        ) / len(version_results)
        avg_marketing_length = sum(
            r["metrics"]["marketing_length"] for r in version_results
        ) / len(version_results)
        avg_evaluation_time = sum(
            r["metrics"]["evaluation_time"] for r in version_results
        ) / len(version_results)
        avg_readability = sum(
            (
                r["metrics"]["technical_readability_score"]
                + r["metrics"]["marketing_readability_score"]
            )
            / 2
            for r in version_results
        ) / len(version_results)

        report += f"""
## {version} ({len(version_results)} test cases)

- **Average Technical Length:** {avg_tech_length:.1f} characters
- **Average Marketing Length:** {avg_marketing_length:.1f} characters
- **Average Generation Time:** {avg_evaluation_time:.2f} seconds
- **Average Readability Score:** {avg_readability:.2f}

"""

    # Save comparison report
    with open(args.output, "w") as f:
        f.write(report)

    print(f"Comparison report saved to: {args.output}")
    return 0


def cmd_validate_dataset(args):
    """Validate test dataset."""
    builder = TestDatasetBuilder("")
    test_cases = builder.load_dataset(args.dataset)

    print(f"Validating dataset: {args.dataset}")
    print(f"Total test cases: {len(test_cases)}")

    # Check for issues
    issues = []

    for i, tc in enumerate(test_cases):
        if not tc.title:
            issues.append(f"Test case {i}: Missing title")
        if not tc.diff:
            issues.append(f"Test case {i}: Missing diff")
        if len(tc.diff) < 50:
            issues.append(f"Test case {i}: Diff too short ({len(tc.diff)} chars)")
        if not tc.author:
            issues.append(f"Test case {i}: Missing author")

    if issues:
        print(f"\nFound {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("\nDataset validation passed!")

    # Show statistics
    categories = {}
    difficulties = {}
    for tc in test_cases:
        categories[tc.category] = categories.get(tc.category, 0) + 1
        difficulties[tc.difficulty] = difficulties.get(tc.difficulty, 0) + 1

    print("\nDataset statistics:")
    print(f"Categories: {categories}")
    print(f"Difficulties: {difficulties}")

    return 0 if not issues else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PR Summary Evaluation CLI")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Build dataset command
    build_parser = subparsers.add_parser(
        "build-dataset", help="Build test dataset from repository"
    )
    build_parser.add_argument("repo", help="Repository in format owner/repo")
    build_parser.add_argument(
        "--github-token", help="GitHub token (or set GITHUB_TOKEN env var)"
    )
    build_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of PRs to process (ignored if --pr-numbers is used)",
    )
    build_parser.add_argument(
        "--pr-numbers",
        help="Comma-separated list of specific PR numbers to include (e.g., 123,456,789)",
    )
    build_parser.add_argument(
        "--output", "-o", default="test_dataset.json", help="Output file path"
    )

    # Run evaluation command
    eval_parser = subparsers.add_parser(
        "evaluate", help="Run evaluation on test dataset"
    )
    eval_parser.add_argument("dataset", help="Path to test dataset JSON file")
    eval_parser.add_argument(
        "--openai-api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    eval_parser.add_argument("--github-token", help="GitHub token for API calls")
    eval_parser.add_argument(
        "--model", default="gpt-4o-mini", help="OpenAI model to use"
    )
    eval_parser.add_argument(
        "--max-tokens", type=int, default=500, help="Maximum tokens for response"
    )
    eval_parser.add_argument(
        "--temperature", type=float, default=0.3, help="Temperature for generation"
    )
    eval_parser.add_argument(
        "--max-diff-length",
        type=int,
        default=8000,
        help="Maximum diff length to include",
    )
    eval_parser.add_argument(
        "--sample-size", type=int, help="Use only a sample of test cases"
    )
    eval_parser.add_argument(
        "--prompt-versions", help="Comma-separated list of prompt versions to test"
    )
    eval_parser.add_argument(
        "--export-human-eval",
        action="store_true",
        help="Export forms for human evaluation",
    )
    eval_parser.add_argument(
        "--output", "-o", default="evaluation_results", help="Output directory"
    )

    # Compare prompts command
    compare_parser = subparsers.add_parser(
        "compare", help="Compare multiple prompt versions"
    )
    compare_parser.add_argument(
        "results_files", nargs="+", help="Evaluation results JSON files"
    )
    compare_parser.add_argument(
        "--output", "-o", default="prompt_comparison.md", help="Output report file"
    )

    # Validate dataset command
    validate_parser = subparsers.add_parser("validate", help="Validate test dataset")
    validate_parser.add_argument("dataset", help="Path to test dataset JSON file")

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)

    # Get tokens from environment if not provided
    if hasattr(args, "github_token") and not args.github_token:
        args.github_token = os.getenv("GITHUB_TOKEN")

    if hasattr(args, "openai_api_key") and not args.openai_api_key:
        args.openai_api_key = os.getenv("OPENAI_API_KEY")

    # Execute command
    if args.command == "build-dataset":
        return cmd_build_dataset(args)
    elif args.command == "evaluate":
        return cmd_run_evaluation(args)
    elif args.command == "compare":
        return cmd_compare_prompts(args)
    elif args.command == "validate":
        return cmd_validate_dataset(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
