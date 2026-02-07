import json
import joblib
import pandas as pd
import streamlit as st

# -----------------------------
# Paths
# -----------------------------
DATA_PATH = "data/V1_label.csv"
FEAT_PATH = "model/feature_columns.json"
RF_PATH = "model/pipeline_rf.pkl"
MLP_PATH = "model/pipeline_mlp.pkl"
TARGET_COL = "Hypertension"  # only used if present in CSV

# -----------------------------
# Categorical label mappings (frontend labels -> backend encoded values)
# MUST match your LabelEncoder outputs
# -----------------------------
SMOKING_STATUS_MAP = {"Current": 0, "Former": 1, "Never": 2}
PHYSICAL_ACTIVITY_MAP = {"High": 0, "Low": 1, "Moderate": 2}
GENDER_MAP = {"Female": 0, "Male": 1}
EDUCATION_LEVEL_MAP = {"Primary": 0, "Secondary": 1, "Tertiary": 2}
EMPLOYMENT_STATUS_MAP = {"Employed": 0, "Retired": 1, "Unemployed": 2}

# If you removed Country from training, do NOT include it anywhere here.
MAPPED_CATEGORICAL = {
    "Smoking_Status": SMOKING_STATUS_MAP,
    "Physical_Activity_Level": PHYSICAL_ACTIVITY_MAP,
    "Gender": GENDER_MAP,
    "Education_Level": EDUCATION_LEVEL_MAP,
    "Employment_Status": EMPLOYMENT_STATUS_MAP,
}

# -----------------------------
# Slider ranges from your min/max table
# Numerical => slider
# -----------------------------
RANGES = {
    "Age": (18, 89, 1),
    "BMI": (15.0, 40.0, 0.1),
    "Cholesterol": (150, 299, 1),
    "Systolic_BP": (90, 179, 1),
    "Diastolic_BP": (60, 119, 1),
    "Alcohol_Intake": (0.0, 30.0, 0.1),
    "Stress_Level": (1, 9, 1),
    "Salt_Intake": (2.0, 15.0, 0.1),
    "Sleep_Duration": (4.0, 10.0, 0.1),
    "Heart_Rate": (50, 99, 1),
    "LDL": (70, 189, 1),
    "HDL": (30, 99, 1),
    "Triglycerides": (50, 249, 1),
    "Glucose": (70, 199, 1),
    "AQI Value": (38.46, 152.96, 0.01),
    "CO AQI Value": (0.72, 5.38, 0.01),
    "Ozone AQI Value": (12.48, 88.32, 0.01),
    "NO2 AQI Value": (0.35, 8.54, 0.01),
    "PM2.5 AQI Value": (30.22, 149.46, 0.01),
}

# -----------------------------
# Streamlit setup
# -----------------------------
st.set_page_config(page_title="Hypertension Predictor", layout="wide")

st.title("🔗 Hypertension Risk Predictor")

st.set_page_config(
    page_title="Hypertension Risk Predictor",
    layout="wide"
)
st.caption("Fill the inputs once. The app predicts using **Random Forest** and **MLP**, and compares their risk probabilities.")

@st.cache_resource
def load_model(path: str):
    return joblib.load(path)

@st.cache_data
def load_feature_cols(path: str):
    with open(path, "r") as f:
        return json.load(f)

@st.cache_data
def load_ref_df(path: str, feature_cols: list[str]):
    df = pd.read_csv(path)
    if TARGET_COL in df.columns:
        df = df.drop(columns=[TARGET_COL])
    keep = [c for c in feature_cols if c in df.columns]
    return df[keep].copy()

def align_features(df: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in feature_cols:
        if c not in df.columns:
            df[c] = 0
    return df[feature_cols]

def safe_median_default(df_ref: pd.DataFrame, col: str):
    if col in df_ref.columns:
        s = pd.to_numeric(df_ref[col], errors="coerce").dropna()
        if not s.empty:
            return float(s.median())
    if col in RANGES:
        lo, hi, _ = RANGES[col]
        return float(lo + (hi - lo) / 2)
    return 0.0

def encoded_to_label(mapping: dict[str, int], encoded_value: int):
    for k, v in mapping.items():
        if int(v) == int(encoded_value):
            return k
    return list(mapping.keys())[0]

def render_mapped_dropdown(col_label: str, mapping: dict[str, int], default_encoded: int):
    labels = list(mapping.keys())
    default_label = encoded_to_label(mapping, default_encoded)
    idx = labels.index(default_label) if default_label in labels else 0
    choice = st.selectbox(col_label, labels, index=idx)
    return int(mapping[choice])

def render_slider(col_label: str, col_name: str, default_val: float):
    if col_name not in RANGES:
        return st.number_input(col_label, value=float(default_val), step=1.0)

    lo, hi, step = RANGES[col_name]
    lo_f, hi_f = float(lo), float(hi)
    val = min(max(float(default_val), lo_f), hi_f)

    is_int = (
        abs(float(step) - 1.0) < 1e-12
        and abs(lo_f - round(lo_f)) < 1e-12
        and abs(hi_f - round(hi_f)) < 1e-12
    )
    if is_int:
        return st.slider(col_label, int(round(lo_f)), int(round(hi_f)), int(round(val)), 1)
    return st.slider(col_label, lo_f, hi_f, float(val), float(step))

def pretty_label(col: str) -> str:
    return col.replace("_", " ")

def risk_badge_text(p: float, threshold: float) -> str:
    # simple “pretty” category label
    if p >= max(threshold, 0.7):
        return "High risk"
    if p >= threshold:
        return "Moderate risk"
    return "Low risk"

# -----------------------------
# Load models + schema
# -----------------------------
feature_cols = load_feature_cols(FEAT_PATH)
rf_model = load_model(RF_PATH)
mlp_model = load_model(MLP_PATH)
df_ref = load_ref_df(DATA_PATH, feature_cols)

threshold = 0.5

# -----------------------------
# Build default user row
# -----------------------------
user_row = {}
for c in feature_cols:
    if c == TARGET_COL:
        continue
    user_row[c] = safe_median_default(df_ref, c)

# -----------------------------
# Input UI (grouped + nicer)
# -----------------------------
demo_cols = {"Age", "Gender", "Education_Level", "Employment_Status"}
lifestyle_cols = {"Smoking_Status", "Physical_Activity_Level", "Alcohol_Intake", "Stress_Level", "Salt_Intake", "Sleep_Duration"}
medical_cols = {"BMI", "Systolic_BP", "Diastolic_BP", "Heart_Rate", "Family_History", "Diabetes"}
lab_cols = {"Cholesterol", "LDL", "HDL", "Triglycerides", "Glucose"}
env_cols = {"AQI Value", "CO AQI Value", "Ozone AQI Value", "NO2 AQI Value", "PM2.5 AQI Value"}

# Only display columns that exist in feature_cols (safety)
feature_set = set(feature_cols)
demo_cols = [c for c in demo_cols if c in feature_set]
lifestyle_cols = [c for c in lifestyle_cols if c in feature_set]
medical_cols = [c for c in medical_cols if c in feature_set]
lab_cols = [c for c in lab_cols if c in feature_set]
env_cols = [c for c in env_cols if c in feature_set]

def render_block(cols_list, title, icon=""):
    if not cols_list:
        return
    with st.expander(f"{icon} {title}", expanded=True):
        left, right = st.columns(2, gap="large")
        half = (len(cols_list) + 1) // 2
        a, b = cols_list[:half], cols_list[half:]

        def render_cols(subset, container):
            with container:
                for c in subset:
                    lab = pretty_label(c)

                    # Binary dropdowns for Family_History / Diabetes (False/True)
                    if c in {"Family_History", "Diabetes"}:
                        choice = st.selectbox(
                            lab,
                            ["False", "True"],
                            index=0 if int(user_row.get(c, 0)) == 0 else 1
                        )
                        user_row[c] = 1 if choice == "True" else 0
                        continue

                    # mapped categorical dropdowns
                    if c in MAPPED_CATEGORICAL:
                        user_row[c] = render_mapped_dropdown(lab, MAPPED_CATEGORICAL[c], int(round(user_row.get(c, 0))))
                        continue

                    # numeric sliders
                    user_row[c] = render_slider(lab, c, user_row.get(c, 0.0))

        render_cols(a, left)
        render_cols(b, right)

render_block(demo_cols, "Demographics", "👤")
render_block(medical_cols, "Vitals & Medical History", "❤️")
render_block(lifestyle_cols, "Lifestyle", "🏃")
render_block(lab_cols, "Lab Results", "🧪")
render_block(env_cols, "Environment (Air Quality)", "🌫️")


st.divider()

# -----------------------------
# Predict
# -----------------------------
if st.button("Predict Hypertension Risk", type="primary"):
    X_one = pd.DataFrame([user_row])
    X_one = align_features(X_one, feature_cols)

    rf_proba = float(rf_model.predict_proba(X_one)[:, 1][0])
    mlp_proba = float(mlp_model.predict_proba(X_one)[:, 1][0])

    rf_pred = int(rf_proba >= threshold)
    mlp_pred = int(mlp_proba >= threshold)

    st.subheader("Machine learning model")

    # --- Model result cards ---
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("### 🧠 MLP (Neural Network)")
        badge = risk_badge_text(mlp_proba, threshold)
        if mlp_pred == 1:
            st.success(
                f"The person **has** a risk of hypertension "
                f"(**{badge}**) with probability **{mlp_proba:.3f}**."
            )
        else:
            st.info(
                f"The person **does not have** a risk of hypertension "
                f"(**{badge}**) with probability **{mlp_proba:.3f}**."
            )

    with c2:
        st.markdown("### 🌳 Random Forest")
        badge = risk_badge_text(rf_proba, threshold)
        if rf_pred == 1:
            st.success(
                f"The person **has** a risk of hypertension "
                f"(**{badge}**) with probability **{rf_proba:.3f}**."
            )
        else:
            st.info(
                f"The person **does not have** a risk of hypertension "
                f"(**{badge}**) with probability **{rf_proba:.3f}**."
            )

    st.divider()

    chart_df = pd.DataFrame(
        {
            "Probability": [mlp_proba, rf_proba]
        },
        index=["MLP (Neural Network)", "Random Forest"]
    )

    st.subheader("📊 Probability comparison")
    st.bar_chart(chart_df)

    st.caption(f"Threshold = {threshold:.2f}. Probabilities shown are P(Hypertension = 1).")
