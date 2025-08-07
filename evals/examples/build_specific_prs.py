#!/usr/bin/env python3
"""
Example script showing how to build a dataset with specific PR numbers.

This is useful when you want to:
1. Test specific PRs that are interesting edge cases
2. Create curated test datasets with known examples
3. Compare specific types of changes (e.g., all bugfixes)
4. Build focused datasets for particular features
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation import TestDatasetBuilder


def main():
    """Main example function."""
    print("🎯 Building Dataset with Specific PR Numbers")
    print("=" * 50)

    # Check for required environment variables
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("   Please set it with: export GITHUB_TOKEN=your_token_here")
        return 1

    print("✅ GitHub token configured")

    # Example 1: Build dataset with specific PR numbers
    print("\n📋 Example 1: Specific PR numbers")

    # You can replace these with actual PR numbers from repositories you're interested in
    examples = [
        {
            "repo": "microsoft/vscode",
            "pr_numbers": [200465, 200451, 200441],  # Recent example PRs
            "description": "Recent VSCode PRs",
        },
        {
            "repo": "facebook/react",
            "pr_numbers": [28340, 28338, 28337],  # Recent example PRs
            "description": "Recent React PRs",
        },
    ]

    for example in examples:
        print(f"\n   Building dataset: {example['description']}")
        print(f"   Repository: {example['repo']}")
        print(f"   PR Numbers: {example['pr_numbers']}")

        try:
            builder = TestDatasetBuilder(github_token)
            test_cases = builder.build_dataset_from_repo(
                example["repo"], pr_numbers=example["pr_numbers"]
            )

            if test_cases:
                dataset_file = f"{example['repo'].replace('/', '_')}_specific_prs.json"
                builder.save_dataset(test_cases, dataset_file)
                print(f"   ✅ Created {len(test_cases)} test cases")
                print(f"   📄 Saved to: {dataset_file}")

                # Show breakdown
                categories = {}
                for tc in test_cases:
                    categories[tc.category] = categories.get(tc.category, 0) + 1
                print(f"   📊 Categories: {categories}")
            else:
                print("   ❌ No test cases created (check PR numbers and repository)")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue

    # Example 2: CLI usage examples
    print("\n🖥️  Example 2: CLI Usage")
    print("   You can also use the CLI to build datasets with specific PRs:")
    print()
    print("   # Build dataset with specific PR numbers")
    print("   python eval_cli.py build-dataset microsoft/vscode \\")
    print("       --pr-numbers 200465,200451,200441 \\")
    print("       --output vscode_specific.json")
    print()
    print("   # Build dataset with latest PRs (traditional approach)")
    print("   python eval_cli.py build-dataset microsoft/vscode \\")
    print("       --limit 10 \\")
    print("       --output vscode_latest.json")

    print("\n🎉 Example complete!")
    print("\nUse cases for specific PR numbers:")
    print("• 🐛 Test challenging PRs that were hard to summarize")
    print("• 📈 Compare different types of changes (features vs bugfixes)")
    print("• 🔄 Build consistent test datasets for prompt comparison")
    print("• 🎯 Focus on specific areas of your codebase")
    print("• 📋 Create curated golden datasets for evaluation")

    return 0


if __name__ == "__main__":
    exit(main())
