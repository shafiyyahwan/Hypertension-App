import streamlit as st
import plotly.graph_objects as go

from utils.ui import inject_global_css
from utils.plotly_theme import apply_plotly_theme

st.set_page_config(
    page_title="Home | Hypertension Risk Predictor",
    page_icon="🫀",
    layout="wide",
)

inject_global_css()
apply_plotly_theme()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/0_Home.py")
    if st.button("🧠 Prediction", use_container_width=True):
        st.switch_page("pages/1_Prediction.py")
    if st.button("🔗 Association Rules", use_container_width=True):
        st.switch_page("pages/2_Association_Rules.py")

    st.markdown("---")
    st.markdown("Hypertension ML Project")

# ---------------- Hero ----------------
st.markdown("""
<div class="hero">
  <h1>🫀 Hypertension Risk Predictor</h1>
  <p>ML-based risk screening & association pattern discovery</p>
  <div class="chip-wrap">
    <span class="chip">2 ML Models</span>
    <span class="chip">Health + Environment</span>
    <span class="chip">Explainable Results</span>
  </div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([1.4, 1], gap="large")

with c1:
    st.markdown("""
    <div class="card">
      <h3>Why hypertension matters</h3>
      <p>
        Hypertension is known as a <b>silent killer</b> because it can remain undetected
        for years. Early detection helps reduce long-term complications such as
        heart disease and stroke.
      </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card">
      <h3>Get started</h3>
      <p>Choose a module from the sidebar or buttons below.</p>
    </div>
    """, unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        if st.button("🧠 Prediction", use_container_width=True):
            st.switch_page("pages/1_Prediction.py")
    with b2:
        if st.button("🔗 Assoc Rules", use_container_width=True):
            st.switch_page("pages/2_Association_Rules.py")

# ---------------- Radar ----------------
st.markdown("### 📌 Risk factor categories")

cats = ["Demographics", "Vitals", "Lifestyle", "Lab", "Environment"]
vals = [4, 6, 6, 5, 5]

fig = go.Figure(go.Scatterpolar(
    r=vals, theta=cats, fill="toself"
))
fig.update_layout(
    height=420,
    showlegend=False,
    polar=dict(radialaxis=dict(range=[0, 8], visible=True))
)

st.plotly_chart(fig, use_container_width=True)
st.caption("Educational use only — not medical advice.")
