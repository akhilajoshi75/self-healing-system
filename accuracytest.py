import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score

# Load labeled dataset
FILE_PATH = "labeled_metrics.csv"
df = pd.read_csv(FILE_PATH, dtype={"pid": str})

# Select features
features = ["cpu_usage", "memory_usage", "process_cpu", "process_memory"]
X = df[features].values
y = df["status"].apply(lambda x: 1 if x == "Normal" else -1).values  # Convert status to 1 (Normal) and -1 (Anomaly)

# 🔹 **Split data into Training & Testing Sets**
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 **Train Isolation Forest Model**
model = IsolationForest(contamination=0.02, random_state=42)
model.fit(X_train)

# 🔹 **Evaluate Model Performance**
y_pred = model.predict(X_test)  # Predict on test data

#  **Basic Accuracy Score**
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# **Precision, Recall, F1-Score**
print("\nClassification Report:\n", classification_report(y_test, y_pred))

#  **Confusion Matrix**
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Normal", "Anomaly"], yticklabels=["Normal", "Anomaly"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

#  **ROC-AUC Score**
auc_score = roc_auc_score(y_test, model.decision_function(X_test))
print(f"ROC-AUC Score: {auc_score:.2f}")

# **Cross-Validation**
cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"Cross-Validation Accuracy: {cv_scores.mean() * 100:.2f}%")

# 🔹 **Save trained model**
joblib.dump(model, "self_healing_model.pkl")
print(f"ML Model trained and saved! Features used: {X.shape[1]}")
