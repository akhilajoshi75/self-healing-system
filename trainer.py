import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

FILE_PATH = "labeled_metrics_new.csv"

def train_model():
    df = pd.read_csv(FILE_PATH)

    # Filter only normal data for training
    df = df[df["status"] == "Normal"]

    features = ["cpu_usage", "memory_usage", "process_cpu", "process_memory"]
    X = df[features].values

    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X)

    joblib.dump(model, "self_healing_model_new.pkl")
    print("✅ Model trained and saved as 'self_healing_model_new.pkl'")

if __name__ == "__main__":
    train_model()
