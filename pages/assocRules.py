import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

st.set_page_config(page_title="Association Rules (Apriori)", layout="wide")
st.title("🔗 Association Rules (Apriori)")
st.caption("Generate and explore association rules using the Apriori algorithm.")

DATA_PATH = "data/assoc_data.csv"   # <-- your transaction dataset

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

try:
    assoc_data = load_data(DATA_PATH)
except FileNotFoundError:
    st.error("Transaction dataset not found.")
    st.stop()

# -----------------------------
# User controls
# -----------------------------
st.subheader("Apriori Parameters")

c1, c2, c3 = st.columns(3)
with c1:
    min_support = st.slider("Min support", 0.01, 0.50, 0.10, 0.01)
with c2:
    min_conf = st.slider("Min confidence", 0.10, 1.00, 0.50, 0.05)
with c3:
    max_len = st.slider("Max itemset length", 2, 5, 3, 1)

run = st.button("🚀 Run Apriori")

# -----------------------------
# Apriori + rules (cached)
# -----------------------------
@st.cache_data
def run_apriori(df, min_support, min_conf, max_len):
    freq = apriori(
        df,
        min_support=min_support,
        use_colnames=True,
        max_len=max_len
    )

    rules = association_rules(
        freq,
        metric="confidence",
        min_threshold=min_conf
    )

    # Optional: keep only rules predicting Hypertension
    if "consequents" in rules.columns:
        rules = rules[rules["consequents"].apply(lambda x: "Hypertension" in x)]

    # Make readable
    rules["IF (Antecedents)"] = rules["antecedents"].apply(
        lambda x: ", ".join(sorted(list(x)))
    )
    rules["THEN (Consequent)"] = rules["consequents"].apply(
        lambda x: ", ".join(sorted(list(x)))
    )

    return rules.sort_values("lift", ascending=False)

# -----------------------------
# Run when button clicked
# -----------------------------
if run:
    with st.spinner("Running Apriori… this may take a moment"):
        rules = run_apriori(assoc_data, min_support, min_conf, max_len)

    if rules.empty:
        st.warning("No rules found. Try lowering support or confidence.")
        st.stop()

    st.success(f"Generated {len(rules)} rules")

    # -----------------------------
    # Display rules
    # -----------------------------
    show_cols = ["IF (Antecedents)", "THEN (Consequent)", "support", "confidence", "lift"]
    st.dataframe(rules[show_cols].head(50), use_container_width=True)

    # -----------------------------
    # Visualization
    # -----------------------------
    st.subheader("📊 Top Rules by Lift")
    top = rules.head(10).copy()
    top.index = top["IF (Antecedents)"] + " → " + top["THEN (Consequent)"]
    st.bar_chart(top[["lift"]])