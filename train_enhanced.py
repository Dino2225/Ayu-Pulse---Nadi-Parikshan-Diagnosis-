"""
Enhanced Training Script for Nadi Parikshan Model
Compares individual ensembles and stacked classifiers using richer BPM feature extraction.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier, VotingClassifier, StackingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

FEATURE_COLUMNS = [
    'bpm1', 'bpm2', 'bpm3',
    'mean_bpm', 'bpm_range', 'bpm_std', 'bpm_cv', 'bpm_sum', 'bpm_min', 'bpm_max', 'bpm_mid',
    'vata_balance', 'pitta_balance', 'kapha_balance',
    'bpm1_bpm2_ratio', 'bpm2_bpm3_ratio', 'bpm1_bpm3_ratio',
    'bpm1_bpm2_diff', 'bpm2_bpm3_diff', 'bpm1_bpm3_diff',
    'bpm1_pct', 'bpm2_pct', 'bpm3_pct',
    'bpm1_mean_dev', 'bpm2_mean_dev', 'bpm3_mean_dev',
    'bpm_std_norm'
]


def add_enhanced_features(df):
    """Add enhanced features from 3-sensor BPM data."""
    df_enhanced = df.copy()

    if not all(col in df.columns for col in ['bpm1', 'bpm2', 'bpm3']):
        raise ValueError("Dataset must contain bpm1, bpm2, bpm3 columns.")

    df_enhanced['mean_bpm'] = df[['bpm1', 'bpm2', 'bpm3']].mean(axis=1)
    df_enhanced['bpm_range'] = df[['bpm1', 'bpm2', 'bpm3']].max(axis=1) - df[['bpm1', 'bpm2', 'bpm3']].min(axis=1)
    df_enhanced['bpm_std'] = df[['bpm1', 'bpm2', 'bpm3']].std(axis=1)
    df_enhanced['bpm_cv'] = df_enhanced['bpm_std'] / (df_enhanced['mean_bpm'] + 1e-6)
    df_enhanced['bpm_sum'] = df[['bpm1', 'bpm2', 'bpm3']].sum(axis=1)
    df_enhanced['bpm_min'] = df[['bpm1', 'bpm2', 'bpm3']].min(axis=1)
    df_enhanced['bpm_max'] = df[['bpm1', 'bpm2', 'bpm3']].max(axis=1)
    df_enhanced['bpm_mid'] = df[['bpm1', 'bpm2', 'bpm3']].median(axis=1)

    total = df_enhanced['bpm_sum'].replace(0, 1e-6)
    df_enhanced['vata_balance'] = df_enhanced['bpm1'] / total
    df_enhanced['pitta_balance'] = df_enhanced['bpm2'] / total
    df_enhanced['kapha_balance'] = df_enhanced['bpm3'] / total

    df_enhanced['bpm1_bpm2_ratio'] = df_enhanced['bpm1'] / (df_enhanced['bpm2'] + 1e-6)
    df_enhanced['bpm2_bpm3_ratio'] = df_enhanced['bpm2'] / (df_enhanced['bpm3'] + 1e-6)
    df_enhanced['bpm1_bpm3_ratio'] = df_enhanced['bpm1'] / (df_enhanced['bpm3'] + 1e-6)

    df_enhanced['bpm1_bpm2_diff'] = (df_enhanced['bpm1'] - df_enhanced['bpm2']).abs()
    df_enhanced['bpm2_bpm3_diff'] = (df_enhanced['bpm2'] - df_enhanced['bpm3']).abs()
    df_enhanced['bpm1_bpm3_diff'] = (df_enhanced['bpm1'] - df_enhanced['bpm3']).abs()

    df_enhanced['bpm1_pct'] = df_enhanced['bpm1'] / total
    df_enhanced['bpm2_pct'] = df_enhanced['bpm2'] / total
    df_enhanced['bpm3_pct'] = df_enhanced['bpm3'] / total

    df_enhanced['bpm1_mean_dev'] = df_enhanced['bpm1'] - df_enhanced['mean_bpm']
    df_enhanced['bpm2_mean_dev'] = df_enhanced['bpm2'] - df_enhanced['mean_bpm']
    df_enhanced['bpm3_mean_dev'] = df_enhanced['bpm3'] - df_enhanced['mean_bpm']
    df_enhanced['bpm_std_norm'] = df_enhanced['bpm_std'] / (df_enhanced['mean_bpm'] + 1e-6)

    return df_enhanced


def evaluate_models(X, y, models, cv):
    results = {}
    for name, clf in models.items():
        print(f"Evaluating {name}...")
        scores = cross_val_score(clf, X, y, cv=cv, scoring='accuracy', n_jobs=-1)
        results[name] = scores
        print(f"  mean={scores.mean():.4f}, std={scores.std():.4f}")
    return results


def plot_confusion(model, X_test, y_test, target_names, filename):
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='coolwarm', xticklabels=target_names, yticklabels=target_names)
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.title(f'Confusion Matrix - {filename}')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


# Load dataset
print("Loading dataset...")
df = pd.read_csv('nadiparikshan_3sensor.csv')
print(f"Dataset shape: {df.shape}")
print(f"Labels distribution:\n{df['label'].value_counts().sort_index()}\n")

# Add enhanced features
print("Adding enhanced features...")
df_enhanced = add_enhanced_features(df)
print(f"Enhanced dataset shape: {df_enhanced.shape}")
print(f"Feature columns: {len(FEATURE_COLUMNS)}\n")

label_encoder = LabelEncoder()
df_enhanced['label_encoded'] = label_encoder.fit_transform(df_enhanced['label'])
print("Label mapping:", dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_))))

X = df_enhanced[FEATURE_COLUMNS]
y = df_enhanced['label_encoded']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

models = {
    'random_forest': RandomForestClassifier(n_estimators=500, max_depth=14, random_state=42, class_weight='balanced'),
    'xgboost': XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=6, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='mlogloss', use_label_encoder=False),
    'gradient_boosting': GradientBoostingClassifier(n_estimators=500, learning_rate=0.05, max_depth=6, random_state=42),
    'hist_gradient_boosting': HistGradientBoostingClassifier(max_iter=300, max_depth=10, random_state=42),
    'svc': SVC(kernel='rbf', C=10, gamma='scale', probability=True, random_state=42),
    'logistic_regression': LogisticRegression(max_iter=5000, random_state=42),
    'gaussian_nb': GaussianNB()
}

print("\n=== Cross-validated model comparison ===")
results = evaluate_models(X_scaled, y, models, cv)

estimators = [
    ('rf', models['random_forest']),
    ('xgb', models['xgboost']),
    ('gb', models['gradient_boosting'])
]
stacking = StackingClassifier(
    estimators=estimators,
    final_estimator=LogisticRegression(max_iter=5000, random_state=42),
    passthrough=True,
    cv=cv,
    n_jobs=-1
)
voting = VotingClassifier(
    estimators=[('rf', models['random_forest']), ('xgb', models['xgboost']), ('gb', models['gradient_boosting'])],
    voting='soft',
    weights=[2, 2, 1],
    n_jobs=-1
)

ensemble_models = {
    'stacking': stacking,
    'soft_voting': voting
}

print("\n=== Ensemble comparison ===")
ensemble_results = evaluate_models(X_scaled, y, ensemble_models, cv)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

print("\nTraining final models on holdout split...")
final_models = {
    'random_forest': models['random_forest'],
    'xgboost': models['xgboost'],
    'stacking': stacking
}

best_model_name = None
best_acc = 0.0
best_model = None

for name, clf in final_models.items():
    print(f"Training {name}...")
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"{name}: holdout accuracy={acc:.4f}")
    if acc > best_acc:
        best_acc = acc
        best_model_name = name
        best_model = clf
    if name == 'stacking':
        print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
        plot_confusion(clf, X_test, y_test, label_encoder.classes_, 'confusion_matrix_stacking.png')

print(f"\nBest holdout model: {best_model_name} ({best_acc:.4f})")

joblib.dump(scaler, 'scaler_enhanced.joblib')
joblib.dump(label_encoder, 'label_encoder_enhanced.joblib')
joblib.dump(best_model, 'rf_nadi_model_enhanced.joblib')
joblib.dump(best_model, 'rf_nadi_model.joblib')
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(label_encoder, 'label_encoder.joblib')

print("\nSaved enhanced scaler and model files:")
print("- rf_nadi_model_enhanced.joblib")
print("- rf_nadi_model.joblib")
print("- scaler_enhanced.joblib")
print("- scaler.joblib")
print("- label_encoder_enhanced.joblib")
print("- label_encoder.joblib")

if hasattr(models['random_forest'], 'feature_importances_'):
    importances = models['random_forest'].feature_importances_
    indices = np.argsort(importances)[::-1]
    print("\n=== RandomForest feature importance ===")
    for i in range(min(10, len(FEATURE_COLUMNS))):
        print(f"{i+1}. {FEATURE_COLUMNS[indices[i]]}: {importances[indices[i]]:.4f}")

print("\n✅ Training complete. Review confusion_matrix_stacking.png and the printed results.")