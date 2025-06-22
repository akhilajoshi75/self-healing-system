# Self-Healing Software System Using AI & ML

This project is a real-time, AI-powered system monitoring and self-healing tool. It is designed to detect anomalous behavior in system resource usage (CPU, memory, and process-level metrics) and respond with appropriate automated or user-confirmed corrective actions.

## Overview

The system continuously monitors CPU, memory usage, and individual process statistics. It uses an Isolation Forest model trained on labeled metrics to classify anomalies and suggests or performs actions such as terminating or restarting problematic processes.

---

## Features

- Real-time monitoring of system and process-level resource usage
- Machine Learning-based anomaly detection using Isolation Forest
- GUI prompts for user-verified healing actions using `tkinter`
- Automated self-healing responses to abnormal usage patterns
- Historical data logging and labeling for training and analysis
- Configurable thresholds and cooldown periods to prevent false positives

---

## Architecture

1. **Data Collection**: `ipcollection.py` logs system and process metrics to a CSV file.
2. **Labeling**: `labeled.py` assigns labels based on usage thresholds.
3. **Model Training**: `trainmodel.py` trains an Isolation Forest model using labeled data.
4. **Evaluation**: `accuracytest.py` evaluates the trained model's performance.
5. **Self-Healing Runtime**: `healing_new.py` loads the trained model and executes real-time anomaly detection and healing actions.
6. **Configuration**: `config.py` defines known safe processes and application mappings.

## Modules
1. ipcollection.py
Collects real-time system and process-level metrics

Logs data to metrics.csv

2. labeled.py
Labels the data for model training based on threshold rules

Creates labeled_metrics.csv

3. trainmodel.py
Trains an Isolation Forest model on labeled data

Saves model as self_healing_model.pkl

4. accuracytest.py
Evaluates model performance using accuracy, confusion matrix, and ROC-AUC

5. healing_new.py
Main runtime system that:

Loads the trained model

Detects anomalies in real-time

Prompts user for corrective action (terminate, restart, etc.)

6. config.py
Provides platform-specific exclusion lists and known application mappings

Defines cooldown duration to avoid repeated prompts


## Project Structure
self-healing-system/
│
├── accuracytest.py
├── config.py
├── healing_new.py
├── ipcollection.py
├── labeled.py
├── metrics.csv                # Auto-generated
├── labeled_metrics.csv        # Auto-generated
├── requirements.txt
├── self_healing_model.pkl     # Auto-generated
├── trainmodel.py
└── README.md

