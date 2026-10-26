"""Train only from independently labeled research features, never invented targets.

Usage: python app_and_ml/train.py --features labeled_features.csv --output model.pkl
Columns: subject_id, heart_rate, si, ri, ibi_variance, apg_ba, risk_tier.
Risk tiers must come from an independently documented reference assessment.
"""
import argparse
import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline

FEATURES = ['heart_rate', 'si', 'ri', 'ibi_variance', 'apg_ba']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--features', type=Path, required=True, help='Feature CSV with independent reference labels and subject IDs')
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('research_classifier.pkl'))
    args = parser.parse_args()
    frame = pd.read_csv(args.features)
    required = FEATURES + ['risk_tier', 'subject_id']
    missing = set(required) - set(frame.columns)
    if missing:
        parser.error('Missing required columns: ' + ', '.join(sorted(missing)))
    if frame['subject_id'].isna().any() or frame['subject_id'].nunique() < 5:
        parser.error('At least five distinct, non-missing subject IDs are required for a held-out subject split.')
    if frame['risk_tier'].isna().any() or set(frame['risk_tier'].unique()) != {0, 1, 2}:
        parser.error('Provide independent labels for all three reference tiers (0, 1, 2). Do not derive labels from SI.')
    x = frame[FEATURES].apply(pd.to_numeric, errors='raise')
    if x.isna().all().any():
        parser.error('Each feature must have observed values. APG landmark ratios require an independently verified extractor.')
    train, test = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=42).split(x, groups=frame['subject_id']))
    y = frame['risk_tier']
    if set(y.iloc[train]) != {0, 1, 2} or set(y.iloc[test]) != {0, 1, 2}:
        parser.error('Subject split lacks a reference tier. Collect more labeled subjects before evaluation.')
    model = make_pipeline(SimpleImputer(strategy='median'), RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42))
    model.fit(x.iloc[train], y.iloc[train])
    predictions = model.predict(x.iloc[test])
    print(classification_report(y.iloc[test], predictions, labels=[0, 1, 2], zero_division=0))
    print('Macro F1:', f1_score(y.iloc[test], predictions, average='macro'))
    print('Confusion matrix:\n', confusion_matrix(y.iloc[test], predictions, labels=[0, 1, 2]))
    # Exclusive creation protects existing artifacts from accidental overwrite.
    with args.output.open('xb') as file:
        pickle.dump({'model': model, 'features': FEATURES, 'status': 'research only',
                     'train_subjects': sorted(map(str, frame.iloc[train]['subject_id'].unique())),
                     'test_subjects': sorted(map(str, frame.iloc[test]['subject_id'].unique()))}, file)
    print('Saved research artifact:', args.output)


if __name__ == '__main__':
    main()
