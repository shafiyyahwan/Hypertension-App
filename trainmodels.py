# train_and_save_models.py
# Ready-to-run: load data -> split -> train (MLP+SMOTE+Scaler, RF+balanced) -> evaluate -> save for Streamlit

import os
import json
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE


# =========================
# 1) CONFIG
# =========================
DATA_PATH = "data/V1_label.csv"         # <- your current folder shows this exists
TARGET_COL = "Hypertension"             # <- change if your label column name differs
OUT_DIR = "model"                       # <- where we save .pkl + feature columns

RANDOM_STATE = 42
TEST_SIZE = 0.2


# =========================
# 2) LOAD DATA
# =========================
V1_label = pd.read_csv(DATA_PATH)

if TARGET_COL not in V1_label.columns:
    raise ValueError(
        f"Target column '{TARGET_COL}' not found. Available columns:\n{list(V1_label.columns)}"
    )

# Features + target
X_label = V1_label.drop(columns=[TARGET_COL])
y_label = V1_label[TARGET_COL]

# Basic checks
print("Loaded:", DATA_PATH)
print("Shape:", V1_label.shape)
print("Target unique:", sorted(pd.Series(y_label).unique()))
try:
    print("Positive rate:", float(pd.Series(y_label).mean()))
except Exception:
    pass


# =========================
# 3) TRAIN / TEST SPLIT
# =========================
Xl_train, Xl_test, yl_train, yl_test = train_test_split(
    X_label,
    y_label,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y_label
)

print("\n--- Split Info ---")
print("Train shape:", Xl_train.shape, "Test shape:", Xl_test.shape)
print("Train positive rate:", float(pd.Series(yl_train).mean()))
print("Test positive rate:", float(pd.Series(yl_test).mean()))

feature_cols = list(Xl_train.columns)


# =========================
# 4) TRAIN MLP (Scaler + SMOTE + Best Params)
# =========================
mlp_best_params = {
    "hidden_layer_sizes": (50,),
    "activation": "tanh",
    "alpha": 0.001824319396315293,
    "learning_rate_init": 0.07808901863593044
}

mlp_model = ImbPipeline(steps=[
    ("scaler", StandardScaler()),
    ("smote", SMOTE(random_state=RANDOM_STATE)),
    ("mlp", MLPClassifier(
        **mlp_best_params,
        max_iter=400,
        random_state=RANDOM_STATE,
        early_stopping=True,
        n_iter_no_change=20
    ))
])

print("\nTraining MLP...")
mlp_model.fit(Xl_train, yl_train)

y_pred_mlp = mlp_model.predict(Xl_test)
y_proba_mlp = mlp_model.predict_proba(Xl_test)[:, 1]

mlp_results = {
    "Accuracy": accuracy_score(yl_test, y_pred_mlp),
    "Precision": precision_score(yl_test, y_pred_mlp, zero_division=0),
    "Recall": recall_score(yl_test, y_pred_mlp, zero_division=0),
    "F1-Score": f1_score(yl_test, y_pred_mlp, zero_division=0),
    "ROC-AUC": roc_auc_score(yl_test, y_proba_mlp)
}

print("\n--- MLP (Best Params) Results ---")
print(pd.DataFrame(list(mlp_results.items()), columns=["Metric", "Score"]))


# =========================
# 5) TRAIN RANDOM FOREST (Balanced + Best Params)
# =========================
rf_best_params = {
    "n_estimators": 166,
    "max_depth": 16,
    "min_samples_split": 8,
    "min_samples_leaf": 3,
    "max_features": 0.5
}

rf_model = RandomForestClassifier(
    **rf_best_params,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1
)

print("\nTraining Random Forest...")
rf_model.fit(Xl_train, yl_train)

y_pred_rf = rf_model.predict(Xl_test)
y_proba_rf = rf_model.predict_proba(Xl_test)[:, 1]

rf_results = {
    "Accuracy": accuracy_score(yl_test, y_pred_rf),
    "Precision": precision_score(yl_test, y_pred_rf, zero_division=0),
    "Recall": recall_score(yl_test, y_pred_rf, zero_division=0),
    "F1-Score": f1_score(yl_test, y_pred_rf, zero_division=0),
    "ROC-AUC": roc_auc_score(yl_test, y_proba_rf)
}

print("\n--- Random Forest (Best Params) Results ---")
print(pd.DataFrame(list(rf_results.items()), columns=["Metric", "Score"]))


# =========================
# 6) SAVE FOR STREAMLIT
# =========================
os.makedirs(OUT_DIR, exist_ok=True)

joblib.dump(mlp_model, os.path.join(OUT_DIR, "pipeline_mlp.pkl"))
joblib.dump(rf_model, os.path.join(OUT_DIR, "pipeline_rf.pkl"))

with open(os.path.join(OUT_DIR, "feature_columns.json"), "w") as f:
    json.dump(feature_cols, f, indent=2)

print("\nSaved files:")
print("-", os.path.join(OUT_DIR, "pipeline_mlp.pkl"))
print("-", os.path.join(OUT_DIR, "pipeline_rf.pkl"))
print("-", os.path.join(OUT_DIR, "feature_columns.json"))

print("\nDone ✅ Now you can load these in Streamlit.")
