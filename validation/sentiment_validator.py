"""
Sentiment Model Validation Framework
=====================================
Validates VADER sentiment analysis against human-labeled crypto text
Provides accuracy metrics and suggests improvements
"""

import sys
from pathlib import Path
import json
from typing import Dict, List, Tuple
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.sentiment_analyzer import SentimentAnalyzer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class SentimentValidator:
    """
    Validates sentiment model performance against human labels
    """

    def __init__(self, labels_file: str = None):
        """
        Initialize sentiment validator

        Args:
            labels_file: Path to JSON file with labeled data
        """
        if labels_file is None:
            labels_file = Path(__file__).parent / 'labeled_data.json'

        self.labels_file = Path(labels_file)
        self.analyzer = SentimentAnalyzer()
        self.labeled_data = self._load_labels()

        logging.info(f"Sentiment validator initialized ({len(self.labeled_data)} labeled samples)")

    def _load_labels(self) -> List[Dict]:
        """Load human-labeled data"""
        if not self.labels_file.exists():
            logging.info(f"Creating new labels file: {self.labels_file}")
            self.labels_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_labels([])
            return []

        try:
            with open(self.labels_file, 'r', encoding='utf-8') as f:
                labels = json.load(f)
            return labels
        except Exception as e:
            logging.error(f"Error loading labels: {e}")
            return []

    def _save_labels(self, labels: List[Dict]):
        """Save labeled data"""
        try:
            with open(self.labels_file, 'w', encoding='utf-8') as f:
                json.dump(labels, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving labels: {e}")

    def add_labeled_sample(self,
                          text: str,
                          human_sentiment: str,
                          platform: str = 'reddit',
                          coin_symbol: str = None,
                          metadata: Dict = None) -> Dict:
        """
        Add a human-labeled sample for validation

        Args:
            text: The text content (post/comment/tweet)
            human_sentiment: Human label ('positive', 'negative', 'neutral')
            platform: Platform ('reddit', 'tiktok', 'twitter')
            coin_symbol: Associated coin (optional)
            metadata: Additional metadata

        Returns:
            The labeled sample dictionary
        """
        if human_sentiment not in ['positive', 'negative', 'neutral']:
            raise ValueError("human_sentiment must be 'positive', 'negative', or 'neutral'")

        # Get model prediction
        if platform == 'reddit':
            model_result = self.analyzer.analyze_text(text)
        elif platform == 'tiktok':
            model_result = self.analyzer.analyze_text(text)
        else:
            model_result = self.analyzer.analyze_text(text)

        # Determine model's sentiment classification
        if model_result['compound'] >= 0.05:
            model_sentiment = 'positive'
        elif model_result['compound'] <= -0.05:
            model_sentiment = 'negative'
        else:
            model_sentiment = 'neutral'

        sample = {
            'id': len(self.labeled_data) + 1,
            'text': text,
            'human_sentiment': human_sentiment,
            'model_sentiment': model_sentiment,
            'model_scores': model_result,
            'platform': platform,
            'coin_symbol': coin_symbol,
            'metadata': metadata or {},
            'labeled_at': datetime.utcnow().isoformat(),
            'correct': human_sentiment == model_sentiment
        }

        self.labeled_data.append(sample)
        self._save_labels(self.labeled_data)

        logging.info(f"Sample added (ID: {sample['id']}, Correct: {sample['correct']})")
        return sample

    def validate_model(self) -> Dict:
        """
        Calculate validation metrics against all labeled data

        Returns:
            Dictionary with accuracy, precision, recall, F1 score
        """
        if not self.labeled_data:
            return {
                'error': 'No labeled data available',
                'sample_count': 0
            }

        # Count correct predictions
        correct = sum(1 for sample in self.labeled_data if sample['correct'])
        total = len(self.labeled_data)

        # Calculate per-class metrics
        metrics_by_class = {}
        for sentiment_class in ['positive', 'negative', 'neutral']:
            tp = sum(1 for s in self.labeled_data
                    if s['human_sentiment'] == sentiment_class and s['model_sentiment'] == sentiment_class)
            fp = sum(1 for s in self.labeled_data
                    if s['human_sentiment'] != sentiment_class and s['model_sentiment'] == sentiment_class)
            fn = sum(1 for s in self.labeled_data
                    if s['human_sentiment'] == sentiment_class and s['model_sentiment'] != sentiment_class)
            tn = sum(1 for s in self.labeled_data
                    if s['human_sentiment'] != sentiment_class and s['model_sentiment'] != sentiment_class)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            metrics_by_class[sentiment_class] = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'support': tp + fn  # Total human-labeled samples for this class
            }

        # Macro-averaged metrics
        macro_precision = sum(m['precision'] for m in metrics_by_class.values()) / 3
        macro_recall = sum(m['recall'] for m in metrics_by_class.values()) / 3
        macro_f1 = sum(m['f1_score'] for m in metrics_by_class.values()) / 3

        # Confusion matrix
        confusion_matrix = self._build_confusion_matrix()

        return {
            'sample_count': total,
            'overall_accuracy': correct / total,
            'macro_precision': macro_precision,
            'macro_recall': macro_recall,
            'macro_f1': macro_f1,
            'by_class': metrics_by_class,
            'confusion_matrix': confusion_matrix
        }

    def _build_confusion_matrix(self) -> Dict:
        """Build confusion matrix"""
        matrix = {
            'positive': {'positive': 0, 'negative': 0, 'neutral': 0},
            'negative': {'positive': 0, 'negative': 0, 'neutral': 0},
            'neutral': {'positive': 0, 'negative': 0, 'neutral': 0}
        }

        for sample in self.labeled_data:
            human = sample['human_sentiment']
            model = sample['model_sentiment']
            matrix[human][model] += 1

        return matrix

    def get_misclassified_samples(self, sentiment_class: str = None) -> List[Dict]:
        """
        Get samples that were misclassified

        Args:
            sentiment_class: Filter by human sentiment class (optional)

        Returns:
            List of misclassified samples
        """
        misclassified = [s for s in self.labeled_data if not s['correct']]

        if sentiment_class:
            misclassified = [s for s in misclassified if s['human_sentiment'] == sentiment_class]

        return misclassified

    def suggest_lexicon_additions(self) -> Dict:
        """
        Analyze misclassified samples and suggest crypto-specific lexicon additions

        Returns:
            Suggested additions to positive/negative word lists
        """
        misclassified = self.get_misclassified_samples()

        # Extract tokens from misclassified samples
        positive_tokens = []
        negative_tokens = []

        for sample in misclassified:
            tokens = sample['text'].lower().split()

            # If human labeled positive but model said negative/neutral
            if sample['human_sentiment'] == 'positive' and sample['model_sentiment'] != 'positive':
                positive_tokens.extend(tokens)

            # If human labeled negative but model said positive/neutral
            elif sample['human_sentiment'] == 'negative' and sample['model_sentiment'] != 'negative':
                negative_tokens.extend(tokens)

        # Count frequencies
        from collections import Counter
        positive_freq = Counter(positive_tokens)
        negative_freq = Counter(negative_tokens)

        # Filter to crypto-relevant terms (simple heuristic)
        crypto_terms = ['moon', 'rocket', 'lambo', 'hodl', 'dump', 'crash', 'pump',
                       'bullish', 'bearish', 'rug', 'scam', 'gem', 'fomo', 'fud']

        suggested_positive = [word for word, count in positive_freq.most_common(20)
                             if word in crypto_terms or word.startswith('$')]

        suggested_negative = [word for word, count in negative_freq.most_common(20)
                             if word in crypto_terms or word.startswith('$')]

        return {
            'positive_additions': suggested_positive[:10],
            'negative_additions': suggested_negative[:10],
            'misclassified_count': len(misclassified),
            'recommendation': 'Add these terms to sentiment analyzer custom lexicon'
        }

    def export_report(self, filepath: str):
        """Export validation report to markdown file"""
        metrics = self.validate_model()

        if 'error' in metrics:
            logging.warning("Cannot export report: no labeled data")
            return

        report = f"""# Sentiment Model Validation Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Sample Count:** {metrics['sample_count']}

## Overall Performance

- **Accuracy:** {metrics['overall_accuracy']:.2%}
- **Macro Precision:** {metrics['macro_precision']:.2%}
- **Macro Recall:** {metrics['macro_recall']:.2%}
- **Macro F1 Score:** {metrics['macro_f1']:.2%}

## Per-Class Metrics

"""
        for sentiment_class, class_metrics in metrics['by_class'].items():
            report += f"""### {sentiment_class.capitalize()}

- **Precision:** {class_metrics['precision']:.2%}
- **Recall:** {class_metrics['recall']:.2%}
- **F1 Score:** {class_metrics['f1_score']:.2%}
- **Support:** {class_metrics['support']} samples

"""

        report += """## Confusion Matrix

|             | Predicted Positive | Predicted Negative | Predicted Neutral |
|-------------|-------------------|-------------------|------------------|
"""
        cm = metrics['confusion_matrix']
        for true_class in ['positive', 'negative', 'neutral']:
            row = f"| **True {true_class.capitalize()}** | "
            row += f"{cm[true_class]['positive']} | {cm[true_class]['negative']} | {cm[true_class]['neutral']} |"
            report += row + "\n"

        # Add lexicon suggestions
        suggestions = self.suggest_lexicon_additions()
        if suggestions['misclassified_count'] > 0:
            report += f"""
## Suggested Improvements

**Misclassified Samples:** {suggestions['misclassified_count']}

### Suggested Positive Terms
{', '.join(suggestions['positive_additions']) if suggestions['positive_additions'] else 'None'}

### Suggested Negative Terms
{', '.join(suggestions['negative_additions']) if suggestions['negative_additions'] else 'None'}

**Recommendation:** {suggestions['recommendation']}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        logging.info(f"Validation report exported to {filepath}")

    def get_statistics(self) -> Dict:
        """Get dataset statistics"""
        if not self.labeled_data:
            return {'total_samples': 0}

        from collections import Counter

        return {
            'total_samples': len(self.labeled_data),
            'correct_predictions': sum(1 for s in self.labeled_data if s['correct']),
            'accuracy': sum(1 for s in self.labeled_data if s['correct']) / len(self.labeled_data),
            'by_platform': dict(Counter(s['platform'] for s in self.labeled_data)),
            'by_human_sentiment': dict(Counter(s['human_sentiment'] for s in self.labeled_data)),
            'by_coin': dict(Counter(s.get('coin_symbol', 'unknown') for s in self.labeled_data))
        }


def label_samples_cli():
    """Interactive CLI for labeling samples"""
    validator = SentimentValidator()

    print("\n=== Sentiment Model Validation - Sample Labeling ===\n")
    print("Enter sample texts to label. Type 'quit' to exit.\n")

    while True:
        text = input("\nEnter text to label (or 'quit'): ").strip()
        if text.lower() == 'quit':
            break

        platform = input("Platform (reddit/tiktok/twitter): ").strip().lower() or 'reddit'
        coin = input("Coin symbol (optional): ").strip().upper() or None

        # Show model prediction
        model_result = validator.analyzer.analyze_text(text)
        print(f"\nModel prediction: {model_result}")
        if model_result['compound'] >= 0.05:
            print("  -> POSITIVE")
        elif model_result['compound'] <= -0.05:
            print("  -> NEGATIVE")
        else:
            print("  -> NEUTRAL")

        human_label = input("\nYour label (positive/negative/neutral): ").strip().lower()

        if human_label in ['positive', 'negative', 'neutral']:
            validator.add_labeled_sample(text, human_label, platform, coin)
            print("Sample labeled and saved!")
        else:
            print("Invalid label, skipping...")

    # Show statistics
    stats = validator.get_statistics()
    print(f"\n=== Statistics ===")
    print(f"Total labeled: {stats['total_samples']}")
    print(f"Current accuracy: {stats.get('accuracy', 0):.1%}")


if __name__ == "__main__":
    label_samples_cli()
