import pandas as pd
import streamlit as st

from utils.ui import inject_global_css
from utils.plotly_theme import apply_plotly_theme

st.set_page_config(
    page_title="Association Rules | Hypertension Risk Predictor",
    page_icon="🔗",
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

DATA_PATH = "data/assoc_data.csv"  # <-- change if your file name differs

# -----------------------------
# Sidebar (Your Own)
# -----------------------------
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/0_Home.py")
    if st.button("🧠 Prediction", use_container_width=True):
        st.switch_page("pages/1_Prediction.py")

    st.markdown("---")
    st.markdown("## ⚙️ Apriori Settings")
    min_support = st.slider("Min Support", 0.01, 0.30, 0.05, 0.01)
    min_conf = st.slider("Min Confidence", 0.10, 0.90, 0.50, 0.05)
    max_len = st.slider("Max Itemset Length", 2, 6, 3, 1)

    st.markdown("---")
    only_hypertension = st.checkbox("Show only rules -> Hypertension", value=True)
    top_k = st.slider("Top rules to display", 10, 200, 50, 10)

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="hero">
  <h1>🔗 Association Rules Mining</h1>
  <p>Discover frequent combinations of factors linked to hypertension using Apriori.</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_assoc_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Force 0/1 boolean-ish
    for c in df.columns:
        df[c] = (df[c].astype(float) > 0).astype(int)
    return df

try:
    assoc_df = load_assoc_data(DATA_PATH)
except Exception as e:
    st.error(f"⚠️ Cannot load {DATA_PATH}: {e}")
    st.stop()

st.markdown("## 📄 Dataset Preview")
st.dataframe(assoc_df.head(20), use_container_width=True)

run = st.button("🚀 Generate Rules", use_container_width=True)

if run:
    try:
        from mlxtend.frequent_patterns import apriori, association_rules
    except Exception:
        st.error("mlxtend not installed. Add `mlxtend` to requirements.txt and redeploy.")
        st.stop()

    with st.spinner("Mining frequent itemsets and rules..."):
        freq = apriori(assoc_df, min_support=min_support, use_colnames=True, max_len=max_len)

        if freq.empty:
            st.warning("No frequent itemsets found. Try lowering min_support or increasing max_len.")
            st.stop()

        rules = association_rules(freq, metric="confidence", min_threshold=min_conf)

        if rules.empty:
            st.warning("No rules found. Try lowering min_confidence or min_support.")
            st.stop()

        # Optional filter: consequents contain Hypertension
        if only_hypertension:
            rules = rules[rules["consequents"].apply(lambda s: "Hypertension" in set(s))]

        if rules.empty:
            st.warning("Rules exist, but none match the Hypertension filter. Untick the filter or adjust thresholds.")
            st.stop()

        rules = rules.sort_values(["lift", "confidence", "support"], ascending=False).reset_index(drop=True)

        # friendly display
        def set_to_str(x):
            return ", ".join(sorted(list(x)))

        out = rules.copy()
        out["antecedents"] = out["antecedents"].apply(set_to_str)
        out["consequents"] = out["consequents"].apply(set_to_str)

        out = out[["antecedents", "consequents", "support", "confidence", "lift"]].head(top_k)

    st.markdown("## ✅ Generated Rules")
    st.dataframe(out, use_container_width=True)

    st.markdown("""
    <div class="card">
      <h4>How to read the output</h4>
      <p style="margin-bottom:0;">
        <b>Antecedents → Consequents</b> shows the rule.<br>
        <b>Support</b>: how often the rule appears in the dataset.<br>
        <b>Confidence</b>: probability of consequent given antecedent.<br>
        <b>Lift</b>: strength compared to chance (greater than 1 means stronger than random).
      </p>
    </div>
    """, unsafe_allow_html=True)
