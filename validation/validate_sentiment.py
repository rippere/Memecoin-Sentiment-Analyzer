"""
Sentiment Validation Script
============================
Run sentiment model validation and generate reports
"""

import sys
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.sentiment_validator import SentimentValidator


def main():
    """Command-line interface for sentiment validation"""
    parser = argparse.ArgumentParser(
        description='Validate sentiment model performance',
        epilog='Examples:\n'
               '  python validate_sentiment.py --report\n'
               '  python validate_sentiment.py --label\n'
               '  python validate_sentiment.py --misclassified',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--label', action='store_true',
                       help='Interactive labeling mode')

    parser.add_argument('--report', action='store_true',
                       help='Generate validation report')

    parser.add_argument('--stats', action='store_true',
                       help='Show dataset statistics')

    parser.add_argument('--misclassified', action='store_true',
                       help='Show misclassified samples')

    parser.add_argument('--suggest', action='store_true',
                       help='Suggest lexicon additions')

    parser.add_argument('--output', type=str, default='validation_report.md',
                       help='Output file for report (default: validation_report.md)')

    args = parser.parse_args()

    validator = SentimentValidator()

    # Interactive labeling
    if args.label:
        from validation.sentiment_validator import label_samples_cli
        label_samples_cli()
        return

    # Show statistics
    if args.stats:
        stats = validator.get_statistics()
        print("\n=== Dataset Statistics ===\n")
        print(f"Total samples: {stats['total_samples']}")
        if stats['total_samples'] > 0:
            print(f"Accuracy: {stats['accuracy']:.1%}")
            print(f"Correct: {stats['correct_predictions']}/{stats['total_samples']}")
            print(f"\nBy platform: {stats['by_platform']}")
            print(f"By sentiment: {stats['by_human_sentiment']}")
        return

    # Show misclassified
    if args.misclassified:
        misclassified = validator.get_misclassified_samples()
        print(f"\n=== Misclassified Samples ({len(misclassified)}) ===\n")
        for sample in misclassified[:10]:  # Show first 10
            print(f"ID: {sample['id']}")
            print(f"Text: {sample['text'][:100]}...")
            print(f"Human: {sample['human_sentiment']}, Model: {sample['model_sentiment']}")
            print(f"Scores: {sample['model_scores']}\n")
        return

    # Suggest lexicon additions
    if args.suggest:
        suggestions = validator.suggest_lexicon_additions()
        print("\n=== Lexicon Suggestions ===\n")
        print(f"Based on {suggestions['misclassified_count']} misclassified samples\n")
        print(f"Suggested positive terms: {', '.join(suggestions['positive_additions'])}")
        print(f"Suggested negative terms: {', '.join(suggestions['negative_additions'])}")
        print(f"\n{suggestions['recommendation']}")
        return

    # Generate report
    if args.report:
        metrics = validator.validate_model()
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
            print("Use --label to add labeled samples first")
            return

        print("\n=== Validation Metrics ===\n")
        print(f"Sample count: {metrics['sample_count']}")
        print(f"Overall accuracy: {metrics['overall_accuracy']:.2%}")
        print(f"Macro precision: {metrics['macro_precision']:.2%}")
        print(f"Macro recall: {metrics['macro_recall']:.2%}")
        print(f"Macro F1: {metrics['macro_f1']:.2%}")

        print("\nPer-class metrics:")
        for sentiment_class, class_metrics in metrics['by_class'].items():
            print(f"\n  {sentiment_class.capitalize()}:")
            print(f"    Precision: {class_metrics['precision']:.2%}")
            print(f"    Recall: {class_metrics['recall']:.2%}")
            print(f"    F1: {class_metrics['f1_score']:.2%}")

        # Export detailed report
        validator.export_report(args.output)
        print(f"\nDetailed report exported to: {args.output}")
        return

    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
