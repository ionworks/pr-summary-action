#!/usr/bin/env python3
"""
Example script demonstrating how to use the PR summary evaluation system.

This script shows how to:
1. Build a test dataset from a repository
2. Run evaluations with different prompt variations
3. Generate reports and export results for human evaluation
4. Compare different prompt versions
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from pr_summary_action.config import Config
from evaluation import EvaluationRunner, TestDatasetBuilder
from prompt_variations import (
    get_prompt_variations,
    get_prompt_metadata,
)


def main():
    """Main example function."""
    print("🚀 PR Summary Evaluation System Demo")
    print("=" * 50)

    # Check for required environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not github_token:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("   Please set it with: export GITHUB_TOKEN=your_token_here")
        return 1

    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Please set it with: export OPENAI_API_KEY=your_key_here")
        return 1

    print("✅ Environment variables configured")

    # Step 1: Build test dataset
    print("\n📋 Step 1: Building test dataset...")

    # Choose a repository to analyze (you can change this)
    repo = "microsoft/vscode"  # Example repository
    dataset_file = "test_dataset.json"

    if not os.path.exists(dataset_file):
        print(f"   Building dataset from {repo}...")
        builder = TestDatasetBuilder(github_token)

        # Option 1: Build with specific PR numbers (more targeted)
        # specific_prs = [123456, 123457, 123458]  # Replace with actual PR numbers
        # test_cases = builder.build_dataset_from_repo(repo, pr_numbers=specific_prs)

        # Option 2: Build with latest merged PRs (current approach)
        test_cases = builder.build_dataset_from_repo(repo, limit=10)

        if not test_cases:
            print("   ❌ No test cases created. Check repository and token.")
            return 1

        # Save the dataset
        builder.save_dataset(test_cases, dataset_file)
        print(f"   ✅ Created {len(test_cases)} test cases")
    else:
        print(f"   ✅ Using existing dataset: {dataset_file}")

    # Step 2: Show available prompt variations
    print("\n🔀 Step 2: Available prompt variations")
    variations = get_prompt_variations()
    metadata = get_prompt_metadata()

    for name, meta in metadata.items():
        print(f"   • {name}: {meta['description']} ({meta['style']} style)")

    # Step 3: Run evaluation
    print("\n🧪 Step 3: Running evaluation...")

    # Create configuration
    config = Config(
        openai_api_key=openai_api_key,
        openai_model="gpt-4o-mini",  # Using cheaper model for demo
        max_tokens=500,
        temperature=0.3,
        max_diff_length=4000,  # Smaller for demo
        github_token=github_token,
        slack_webhook="",  # Not needed for evaluation
        github_repository="",  # Not needed for evaluation
        github_event_path="",  # Not needed for evaluation
        enable_debugging=False,
    )

    # Load test dataset
    builder = TestDatasetBuilder("")
    test_cases = builder.load_dataset(dataset_file)

    # Use only first 3 test cases for demo
    test_cases = test_cases[:3]
    print(f"   Using {len(test_cases)} test cases for demo")

    # Select prompt variations to test
    prompt_versions = ["default", "concise", "user_focused"]
    print(f"   Testing prompt variations: {prompt_versions}")

    # Run evaluation
    runner = EvaluationRunner(config)
    runner.current_test_cases = test_cases

    print("   🔄 Generating summaries and evaluating...")
    results = runner.run_evaluation(test_cases, prompt_versions)

    # Step 4: Save results
    print("\n💾 Step 4: Saving results...")

    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    # Save raw results
    import json

    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Generate report
    report = runner.generate_report(results)
    with open(output_dir / "report.md", "w") as f:
        f.write(report)

    print(f"   ✅ Results saved to {output_dir}")
    print(f"   📊 Report: {output_dir}/report.md")

    # Step 5: Export for human evaluation
    print("\n👥 Step 5: Exporting for human evaluation...")

    human_eval_dir = output_dir / "human_evaluation"
    runner.export_for_human_evaluation(results, str(human_eval_dir))

    print(f"   ✅ Human evaluation forms: {human_eval_dir}")
    print(f"   📝 Open the HTML files to evaluate summaries manually")

    # Step 6: Show summary
    print("\n📈 Step 6: Summary")
    print(f"   Total test cases: {len(test_cases)}")
    print(f"   Prompt variations tested: {len(prompt_versions)}")
    print(f"   Total evaluations: {len(results['results'])}")

    # Show quick stats
    for prompt_version in prompt_versions:
        version_results = [
            r for r in results["results"] if r["prompt_version"] == prompt_version
        ]
        if version_results:
            avg_tech_length = sum(
                r["metrics"]["technical_length"] for r in version_results
            ) / len(version_results)
            avg_marketing_length = sum(
                r["metrics"]["marketing_length"] for r in version_results
            ) / len(version_results)
            print(
                f"   {prompt_version}: avg {avg_tech_length:.0f} tech chars, {avg_marketing_length:.0f} marketing chars"
            )

    print("\n🎉 Evaluation complete!")
    print("\nNext steps:")
    print("1. Review the generated report")
    print("2. Fill out human evaluation forms")
    print("3. Compare different prompt versions")
    print("4. Iterate on prompt improvements")

    return 0


if __name__ == "__main__":
    exit(main())
