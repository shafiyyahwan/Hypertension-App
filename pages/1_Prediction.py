import json
import joblib
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.ui import inject_global_css
from utils.plotly_theme import apply_plotly_theme

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Prediction | Hypertension Risk Predictor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit built-in page navigation (keep your own sidebar)
st.markdown("""
<style>
  [data-testid="stSidebarNav"] { display: none; }
  [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

inject_global_css()
apply_plotly_theme()

# -----------------------------
# Paths
# -----------------------------
DATA_PATH = "data/V1_label.csv"
FEAT_PATH = "model/feature_columns.json"
RF_PATH = "model/pipeline_rf.pkl"
MLP_PATH = "model/pipeline_mlp.pkl"
TARGET_COL = "Hypertension"

# -----------------------------
# Categorical label mappings
# -----------------------------
SMOKING_STATUS_MAP = {"Current": 0, "Former": 1, "Never": 2}
PHYSICAL_ACTIVITY_MAP = {"High": 0, "Low": 1, "Moderate": 2}
GENDER_MAP = {"Female": 0, "Male": 1}
EDUCATION_LEVEL_MAP = {"Primary": 0, "Secondary": 1, "Tertiary": 2}
EMPLOYMENT_STATUS_MAP = {"Employed": 0, "Retired": 1, "Unemployed": 2}

MAPPED_CATEGORICAL = {
    "Smoking_Status": SMOKING_STATUS_MAP,
    "Physical_Activity_Level": PHYSICAL_ACTIVITY_MAP,
    "Gender": GENDER_MAP,
    "Education_Level": EDUCATION_LEVEL_MAP,
    "Employment_Status": EMPLOYMENT_STATUS_MAP,
}

# -----------------------------
# Slider ranges
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
# Helper functions
# -----------------------------
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
    return col.replace("_", " ").title()


def risk_badge_text(p: float, threshold: float) -> str:
    if p >= max(threshold, 0.7):
        return "High Risk"
    if p >= threshold:
        return "Moderate Risk"
    return "Low Risk"


def risk_badge_class(p: float, threshold: float) -> str:
    if p >= max(threshold, 0.7):
        return "badge-high"
    if p >= threshold:
        return "badge-mid"
    return "badge-low"


def create_gauge_chart(probability: float, model_name: str, threshold: float):
    if probability >= 0.7:
        color = "#dc2626"
    elif probability >= 0.5:
        color = "#d97706"
    else:
        color = "#16a34a"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability * 100,
        title={"text": model_name},
        number={"suffix": "%", "font": {"size": 40, "color": color}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 50], "color": "#dcfce7"},
                {"range": [50, 70], "color": "#fef3c7"},
                {"range": [70, 100], "color": "#fee2e2"},
            ],
            "threshold": {
                "line": {"color": "#64748b", "width": 4},
                "value": threshold * 100
            }
        }
    ))
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def create_comparison_chart(mlp_proba: float, rf_proba: float, threshold: float):
    fig = go.Figure()
    models = ["MLP (Neural Network)", "Random Forest"]
    probs = [mlp_proba * 100, rf_proba * 100]

    fig.add_trace(go.Bar(
        y=models,
        x=probs,
        orientation="h",
        text=[f"{p:.1f}%" for p in probs],
        textposition="auto",
        hovertemplate="<b>%{y}</b><br>Probability: %{x:.1f}%<extra></extra>"
    ))

    fig.update_layout(
        height=320,
        title="Model Comparison",
        xaxis=dict(title="Hypertension Risk Probability (%)", range=[0, 100]),
        margin=dict(l=20, r=20, t=50, b=30),
    )

    fig.add_vline(
        x=threshold * 100,
        line_dash="dash",
        line_color="#64748b",
        line_width=2,
        annotation_text="Threshold",
        annotation_position="top"
    )

    return fig


# -----------------------------
# SIDEBAR (Your Own)
# -----------------------------
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/0_Home.py")
    if st.button("🔗 Association Rules", use_container_width=True):
        st.switch_page("pages/2_Association_Rules.py")

    st.markdown("---")
    st.markdown("## ⚙️ Settings")
    threshold = st.slider("Risk Threshold", 0.30, 0.70, 0.50, 0.05)

    st.markdown("---")
    st.markdown("## ℹ️ About")
    st.caption("Predict hypertension risk using Random Forest and MLP models.")

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class="hero">
  <h1>🧠 Hypertension Risk Prediction</h1>
  <p>Fill in patient information and compare Random Forest vs MLP predictions.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Load models
# -----------------------------
try:
    feature_cols = load_feature_cols(FEAT_PATH)
    rf_model = load_model(RF_PATH)
    mlp_model = load_model(MLP_PATH)
    df_ref = load_ref_df(DATA_PATH, feature_cols)
except Exception as e:
    st.error(f"⚠️ Error loading models/files: {str(e)}")
    st.stop()

# -----------------------------
# Initialize defaults
# -----------------------------
user_row = {}
for c in feature_cols:
    if c == TARGET_COL:
        continue
    user_row[c] = safe_median_default(df_ref, c)

# -----------------------------
# Input sections
# -----------------------------
demo_cols = {"Age", "Gender", "Education_Level", "Employment_Status"}
lifestyle_cols = {"Smoking_Status", "Physical_Activity_Level", "Alcohol_Intake",
                  "Stress_Level", "Salt_Intake", "Sleep_Duration"}
medical_cols = {"BMI", "Systolic_BP", "Diastolic_BP", "Heart_Rate",
                "Family_History", "Diabetes"}
lab_cols = {"Cholesterol", "LDL", "HDL", "Triglycerides", "Glucose"}
env_cols = {"AQI Value", "CO AQI Value", "Ozone AQI Value", "NO2 AQI Value", "PM2.5 AQI Value"}

feature_set = set(feature_cols)
demo_cols = [c for c in demo_cols if c in feature_set]
lifestyle_cols = [c for c in lifestyle_cols if c in feature_set]
medical_cols = [c for c in medical_cols if c in feature_set]
lab_cols = [c for c in lab_cols if c in feature_set]
env_cols = [c for c in env_cols if c in feature_set]


def render_block(cols_list, title, icon="", description=""):
    if not cols_list:
        return

    with st.expander(f"{icon} {title}", expanded=True):
        if description:
            st.markdown(f"*{description}*")
            st.markdown("")

        left, right = st.columns(2, gap="large")
        half = (len(cols_list) + 1) // 2
        a, b = cols_list[:half], cols_list[half:]

        def render_cols(subset, container):
            with container:
                for c in subset:
                    lab = pretty_label(c)

                    if c in {"Family_History", "Diabetes"}:
                        choice = st.selectbox(lab, ["No", "Yes"],
                                              index=0 if int(user_row.get(c, 0)) == 0 else 1)
                        user_row[c] = 1 if choice == "Yes" else 0
                        continue

                    if c in MAPPED_CATEGORICAL:
                        user_row[c] = render_mapped_dropdown(
                            lab,
                            MAPPED_CATEGORICAL[c],
                            int(round(user_row.get(c, 0)))
                        )
                        continue

                    user_row[c] = render_slider(lab, c, user_row.get(c, 0.0))

        render_cols(a, left)
        render_cols(b, right)


st.markdown("## 📝 Patient Information")
st.markdown("Please fill in the following information to assess hypertension risk.")

render_block(demo_cols, "Demographics", "👤", "Basic demographic information")
render_block(medical_cols, "Vitals & Medical History", "❤️", "Vital signs and medical background")
render_block(lifestyle_cols, "Lifestyle Factors", "🏃", "Daily habits and lifestyle choices")
render_block(lab_cols, "Laboratory Results", "🧪", "Clinical lab test results")
render_block(env_cols, "Environmental Factors", "🌫️", "Air quality and environmental exposure")

st.markdown("---")

# -----------------------------
# Prediction button
# -----------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    predict_btn = st.button("🔍 Analyze Hypertension Risk", use_container_width=True)

if predict_btn:
    with st.spinner("🔄 Analyzing patient data..."):
        X_one = pd.DataFrame([user_row])
        X_one = align_features(X_one, feature_cols)

        rf_proba = float(rf_model.predict_proba(X_one)[:, 1][0])
        mlp_proba = float(mlp_model.predict_proba(X_one)[:, 1][0])

    st.markdown("## 📊 Analysis Results")

    colA, colB = st.columns(2, gap="large")

    with colA:
        st.plotly_chart(create_gauge_chart(mlp_proba, "MLP Neural Network", threshold),
                        use_container_width=True)
        badge_text = risk_badge_text(mlp_proba, threshold)
        badge_class = risk_badge_class(mlp_proba, threshold)
        st.markdown(
            f"""
            <div class="card">
              <h3>MLP Result</h3>
              <span class="badge {badge_class}">{badge_text}</span>
              <p style="margin-top:0.75rem;margin-bottom:0;">
                Predicted probability: <b>{mlp_proba:.1%}</b>
              </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colB:
        st.plotly_chart(create_gauge_chart(rf_proba, "Random Forest", threshold),
                        use_container_width=True)
        badge_text = risk_badge_text(rf_proba, threshold)
        badge_class = risk_badge_class(rf_proba, threshold)
        st.markdown(
            f"""
            <div class="card">
              <h3>Random Forest Result</h3>
              <span class="badge {badge_class}">{badge_text}</span>
              <p style="margin-top:0.75rem;margin-bottom:0;">
                Predicted probability: <b>{rf_proba:.1%}</b>
              </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 📈 Model Comparison")
    st.plotly_chart(create_comparison_chart(mlp_proba, rf_proba, threshold),
                    use_container_width=True)

    st.markdown("""
    <div class="card">
      <h4>⚕️ Disclaimer</h4>
      <p style="margin-bottom:0;">
        Educational tool only. Not medical advice. Please consult a healthcare professional for diagnosis.
      </p>
    </div>
    """, unsafe_allow_html=True)
