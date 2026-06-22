import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Step 1: Load dataset
# Using 3-sensor dataset to match Flask app expectations (bpm1, bpm2, bpm3)
df = pd.read_csv('nadiparikshan_3sensor.csv')
print("Dataset shape:", df.shape)
print("Columns:", list(df.columns))
print(df.head())

# Step 2: Encode labels
label_encoder = LabelEncoder()
df['label_encoded'] = label_encoder.fit_transform(df['label'])
print("\nLabel Mapping:", dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_))))

# Step 3: Split features and target
X = df.drop(columns=['label', 'label_encoded'])
y = df['label_encoded']

# Step 4: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Step 5: Normalize features (recommended for physiological data)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 6: Train RandomForest model
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    class_weight='balanced'
)
rf_model.fit(X_train_scaled, y_train)

# Step 7: Train XGBoost model (optional alternative)
xgb_model = XGBClassifier(
    n_estimators=250,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='mlogloss'
)
xgb_model.fit(X_train_scaled, y_train)

# Step 8: Evaluate both models
rf_pred = rf_model.predict(X_test_scaled)
xgb_pred = xgb_model.predict(X_test_scaled)

print("\n=== RandomForest Performance ===")
print("Accuracy:", accuracy_score(y_test, rf_pred))
print(classification_report(y_test, rf_pred, target_names=label_encoder.classes_))

print("\n=== XGBoost Performance ===")
print("Accuracy:", accuracy_score(y_test, xgb_pred))
print(classification_report(y_test, xgb_pred, target_names=label_encoder.classes_))

# Step 9: Confusion Matrix for RandomForest
plt.figure(figsize=(7,5))
sns.heatmap(confusion_matrix(y_test, rf_pred), annot=True, fmt='d', cmap='cool', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title("Confusion Matrix — RandomForest")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig('confusion_matrix_rf.png')
plt.close()

# Step 10: Feature Importance (RandomForest)
importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(10,6))
plt.bar(range(X.shape[1]), importances[indices], align='center', color='cyan')
plt.xticks(range(X.shape[1]), X.columns[indices], rotation=45, ha='right')
plt.title("Feature Importance — RandomForest")
plt.tight_layout()
plt.savefig('feature_importance_rf.png')
plt.close()

# Step 11: Save trained models and encoders
joblib.dump(rf_model, 'rf_nadi_model.joblib')
joblib.dump(xgb_model, 'xgb_nadi_model.joblib')
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(label_encoder, 'label_encoder.joblib')

print("\n✅ Models saved successfully as:")
print("rf_nadi_model.joblib, xgb_nadi_model.joblib, scaler.joblib, label_encoder.joblib")
