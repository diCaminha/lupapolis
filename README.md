# Expense Anomaly Detection Project

This project is designed to detect anomalies in parliamentary expenses using an Isolation Forest model. The pipeline processes historical expense data, filters and preprocesses it, and then trains an unsupervised Isolation Forest algorithm to flag unusual expense records. The project integrates data transformation (including one-hot encoding for categorical variables and scaling for numerical variables) and provides a detailed explanation of anomaly results using SHAP for feature contribution analysis.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture & Pipeline](#architecture--pipeline)
- [Integrations](#integrations)
- [Installation & Prerequisites](#installation--prerequisites)
- [Usage](#usage)
- [Evaluation & Results Explanation](#evaluation--results-explanation)
- [Running Tests](#running-tests)

---

## Overview

The Expense Anomaly Detection Project focuses on identifying outliers in expense records. The goal is to flag potentially fraudulent or irregular expenses using a machine learning model trained on historical data. The Isolation Forest model assigns an anomaly score to each record and classifies them as normal or anomalous. Additionally, the project utilizes SHAP (SHapley Additive exPlanations) to provide insight into which features most strongly influenced the anomaly prediction.

---

## Features

- **Data Ingestion and Preprocessing:**  
  Loads expense data from multiple CSV files, filters required columns, and handles missing values.

- **Feature Engineering:**  
  Separates features into categorical (e.g., `txtDescricao`) and numerical (e.g., `vlrDocumento`, `vlrLiquido`) groups.  
  Applies one-hot encoding to categorical features and scaling (via StandardScaler) to numerical features.

- **Anomaly Detection:**  
  Trains an Isolation Forest model to detect outlier expense records.

- **SHAP Integration:**  
  Computes SHAP values to identify and display the two most influential features that contribute to an anomaly score for any given expense.

- **Custom Alerting:**  
  Generates JSON outputs that include the prediction, anomaly score, alert level (green, yellow, or red), and the two most influential features based on SHAP analysis.

- **Category Restriction:**  
  The model is currently restricted to a predefined list of expense types for enhanced prediction quality:
  - "COMBUSTÍVEIS E LUBRIFICANTES."
  - "PASSAGEM AÉREA - SIGEPA"
  - "SERVIÇO DE TÁXI, PEDÁGIO E ESTACIONAMENTO"
  - "MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR"
  - "TELEFONIA"

---

## Architecture & Pipeline

1. **Data Loading:**  
   Reads CSV files (e.g., despesas2021.csv, despesas2022.csv, etc.) and concatenates them into a single DataFrame. It filters the columns required for analysis.

2. **Preprocessing:**  
   Uses a `ColumnTransformer` to:
   - One-hot encode the categorical feature `txtDescricao`.
   - Scale the numeric features (`numMes`, `numAno`, `vlrDocumento`, `numParcela`, `vlrGlosa`, `vlrLiquido`) with StandardScaler.
   
3. **Model Training:**  
   The preprocessed data is then passed into an Isolation Forest model for anomaly detection.  
   The contamination parameter can be adjusted based on domain expertise.

4. **Evaluation & SHAP Analysis:**  
   Once trained, the model outputs anomaly predictions and scores. SHAP values are computed to explain which features are most influential in the model’s decision for a given record.

5. **Integration & Output:**  
   The final output is a JSON containing:
   - `prediction`: either 1 (normal) or -1 (anomaly)
   - `score`: the continuous anomaly score (lower scores indicate a higher risk)
   - `alert`: a custom alert level (green, yellow, or red)
   - `influential_features`: a list of the top 2 features and their SHAP impact values

---

## Integrations

- **Data Sources:**  
  The model integrates expense data from multiple CSV files (years 2021 to 2024).  
- **Machine Learning:**  
  Uses scikit-learn for preprocessing, pipeline construction, and model training with the Isolation Forest.
- **Explainability:**  
  Integrates SHAP to compute feature contributions and aid in the interpretation of anomaly predictions.
- **Logging:**  
  Python's logging module is used to provide runtime information during data loading, model training, and evaluation.
- **Model Persistence:**  
  Uses joblib to save and load the trained pipeline for inference in production environments.

---

## Installation & Prerequisites

### Prerequisites

- Python 3.7 or higher
- pip

### Required Python Libraries

- pandas
- scikit-learn
- joblib
- numpy
- shap
- matplotlib (optional, for visualization)
- seaborn (optional, for visualization)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/expense-anomaly-detection.git
   cd expense-anomaly-detection
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare your CSV files:**

   Place your CSV files (e.g., `despesas2021.csv`, `despesas2022.csv`, etc.) in a folder named `files` at the project root.

---

## Usage

### Training the Model

Run the main training script:

```bash
python your_model_script.py
```

This script will:
- Load and filter the expense data.
- Build and train the preprocessing and Isolation Forest pipeline.
- Evaluate the model and log the anomaly rate.
- Save the trained pipeline to `saved_models/isolation_forest_pipeline.pkl`.

### Testing Inference

Use the provided test script to validate a single expense record:

```bash
python teste.py
```

This script will:
- Load the trained pipeline.
- Transform a sample expense record.
- Predict whether the expense is normal or anomalous.
- Compute an anomaly score.
- Calculate SHAP values to display the two most influential features.
- Output the results as a formatted JSON.

---

## Evaluation & Results Explanation

The output JSON from the test script includes:
- **Prediction:**  
  - `1` for normal expense
  - `-1` for anomaly
- **Score:**  
  A continuous value from the decision function. Lower values indicate higher anomaly risk.
- **Alert:**  
  Custom alert level based on the following rules:
  - **Green:** `prediction` is 1 and score > 0.1
  - **Yellow:** `prediction` is 1 and score ≤ 0.1
  - **Red:** `prediction` is -1
- **Influential Features:**  
  The two features with the highest absolute SHAP impact, explaining the model’s decision.

This multi-level output enables a nuanced review of expense records and supports further investigation into borderline cases.

---

## Running Tests

To run tests on your model:

1. **Ensure your environment is set up and the model is trained.**
2. **Run the test script:**

   ```bash
   python teste.py
   ```

This will produce a JSON output with the anomaly prediction, score, alert level, and influential features.
