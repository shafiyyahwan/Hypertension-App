import streamlit as st
import plotly.graph_objects as go

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Home | Hypertension Risk Predictor",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Hide Streamlit built-in page nav (keep your custom sidebar)
# -----------------------------
st.markdown("""
<style>
  [data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Custom CSS (Quicksand + full Home UI)
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Quicksand', sans-serif;
    }

    .main { padding: 0rem 1rem; }

    /* Hero */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 4rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
        animation: pulse 15s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }

    .hero-section h1 {
        color: white;
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0 0 0.8rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.25);
        position: relative;
        z-index: 1;
    }

    .hero-section p {
        color: rgba(255,255,255,0.95);
        font-size: 1.2rem;
        margin: 0;
        position: relative;
        z-index: 1;
    }

    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 2rem;
        position: relative;
        z-index: 1;
        flex-wrap: wrap;
    }

    .hero-stat { text-align: center; min-width: 120px; }
    .hero-stat-value {
        font-size: 2.3rem;
        font-weight: 700;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.25);
    }
    .hero-stat-label {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.9);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Section header */
    .section-header {
        text-align: center;
        margin: 2.5rem 0 1.8rem 0;
    }
    .section-header h2 {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.4rem;
    }
    .section-header p {
        font-size: 1.05rem;
        color: #64748b;
        margin: 0;
    }

    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #0284c7;
        margin: 0.5rem 0 1.5rem 0;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    }
    .info-box h3 {
        color: #0c4a6e;
        margin-top: 0;
        font-size: 1.4rem;
    }
    .info-box p {
        color: #075985;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0;
    }

    /* Feature cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        transition: all 0.25s ease;
        height: 100%;
        border-left: 5px solid #667eea;
    }
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 10px 28px rgba(102, 126, 234, 0.25);
    }
    .feature-icon { font-size: 2.8rem; margin-bottom: 0.8rem; display: block; }
    .feature-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0.8rem 0; }
    .feature-description { color: #64748b; font-size: 1rem; line-height: 1.6; margin: 0; }

    /* Timeline */
    .timeline-item {
        background: white;
        padding: 1.3rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 0.8rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
        height: 100%;
    }
    .timeline-item h4 { color: #667eea; font-size: 1.15rem; margin: 0 0 0.4rem 0; }
    .timeline-item p { color: #64748b; margin: 0; line-height: 1.55; }

    /* Tech cards */
    .tech-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        transition: all 0.25s ease;
        height: 100%;
    }
    .tech-card:hover { transform: scale(1.03); }
    .tech-card h4 { color: #7c2d12; font-size: 1.1rem; font-weight: 700; margin: 0.4rem 0; }
    .tech-card p { color: #9a3412; font-size: 0.9rem; margin: 0; }

    /* Stat cards */
    .stat-card {
        background: white;
        padding: 1.8rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        transition: all 0.25s ease;
        height: 100%;
    }
    .stat-card:hover { transform: translateY(-5px); }
    .stat-number {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stat-label { color: #64748b; font-size: 1rem; margin-top: 0.3rem; }

    /* CTA */
    .cta-section {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2.6rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2.6rem 0;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
    .cta-section h2 {
        color: #1e293b;
        font-size: 1.9rem;
        font-weight: 800;
        margin: 0 0 0.6rem 0;
    }
    .cta-section p {
        color: #475569;
        font-size: 1.05rem;
        margin: 0 0 1.5rem 0;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        padding: 0.7rem 1.4rem;
        border-radius: 12px;
        border: none;
        font-size: 1.05rem;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(102, 126, 234, 0.35);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(102, 126, 234, 0.45);
    }

    hr {
        margin: 2.3rem 0;
        border: none;
        border-top: 2px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Your Custom Sidebar (STAYS)
# -----------------------------
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/0_Home.py")
    if st.button("🧠 Prediction", use_container_width=True):
        st.switch_page("pages/1_Prediction.py")
    if st.button("🔗 Association Rules", use_container_width=True):
        st.switch_page("pages/2_Association_Rules.py")

    st.markdown("---")
    st.markdown("### 📌 Quick Info")
    st.caption("ML risk prediction + association pattern discovery")

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero-section">
    <h1>🫀 Hypertension Risk Predictor</h1>
    <p>AI-powered risk screening with health + environment indicators</p>
    <div class="hero-stats">
        <div class="hero-stat">
            <div class="hero-stat-value">3</div>
            <div class="hero-stat-label">Models</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-value">30+</div>
            <div class="hero-stat-label">Features</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-value">5</div>
            <div class="hero-stat-label">Factor Groups</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# What is Hypertension
# -----------------------------
st.markdown("""
<div class="section-header">
    <h2>Understanding Hypertension</h2>
    <p>A silent but serious condition affecting long-term cardiovascular health</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="info-box">
        <h3>🩺 What is Hypertension?</h3>
        <p>
            Hypertension (high blood pressure) occurs when the force of blood against the artery walls
            is consistently too high. It often has no obvious symptoms, but it can increase the risk of
            heart disease, stroke, and kidney problems.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left-color: #d97706;">
        <h3>⚠️ Why It Matters</h3>
        <p>
            Because many people are unaware of their condition, early detection is important.
            This platform helps explore key risk factors and provides model-based screening outputs.
        </p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Features
# -----------------------------
st.markdown("""
<div class="section-header">
    <h2>🌟 Platform Features</h2>
    <p>Tools to support risk screening and pattern discovery</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="large")
with c1:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🧠</span>
        <div class="feature-title">Risk Prediction</div>
        <p class="feature-description">
            Compare predictions from Random Forest and MLP models using 30+ features.
        </p>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="feature-card" style="border-left-color:#f093fb;">
        <span class="feature-icon">🔗</span>
        <div class="feature-title">Association Rules</div>
        <p class="feature-description">
            Use Apriori to find frequent combinations of conditions linked to hypertension risk.
        </p>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="feature-card" style="border-left-color:#f5576c;">
        <span class="feature-icon">📊</span>
        <div class="feature-title">Interactive Visuals</div>
        <p class="feature-description">
            Charts and summaries to help explain results clearly.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3, gap="large")
with c4:
    st.markdown("""
    <div class="feature-card" style="border-left-color:#10b981;">
        <span class="feature-icon">⚡</span>
        <div class="feature-title">Fast Analysis</div>
        <p class="feature-description">
            Get instant model outputs after entering patient data.
        </p>
    </div>
    """, unsafe_allow_html=True)
with c5:
    st.markdown("""
    <div class="feature-card" style="border-left-color:#f59e0b;">
        <span class="feature-icon">🎯</span>
        <div class="feature-title">Holistic Factors</div>
        <p class="feature-description">
            Includes demographics, vitals, lifestyle, lab, and environmental air quality indicators.
        </p>
    </div>
    """, unsafe_allow_html=True)
with c6:
    st.markdown("""
    <div class="feature-card" style="border-left-color:#6366f1;">
        <span class="feature-icon">📱</span>
        <div class="feature-title">User-Friendly UI</div>
        <p class="feature-description">
            Structured sections, clear inputs, and easy navigation.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# How it works
# -----------------------------
st.markdown("""
<div class="section-header">
    <h2>🔄 How It Works</h2>
    <p>Simple steps for risk screening</p>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.columns(4, gap="medium")
with t1:
    st.markdown("""
    <div class="timeline-item">
        <h4>1️⃣ Input</h4>
        <p>Enter patient demographics, vitals, habits, lab values, and environment indicators.</p>
    </div>
    """, unsafe_allow_html=True)
with t2:
    st.markdown("""
    <div class="timeline-item">
        <h4>2️⃣ Predict</h4>
        <p>Models compute risk probability using learned patterns from training data.</p>
    </div>
    """, unsafe_allow_html=True)
with t3:
    st.markdown("""
    <div class="timeline-item">
        <h4>3️⃣ Compare</h4>
        <p>View model outputs side-by-side to understand agreement and confidence.</p>
    </div>
    """, unsafe_allow_html=True)
with t4:
    st.markdown("""
    <div class="timeline-item">
        <h4>4️⃣ Explore</h4>
        <p>Use association rules to find frequent risk factor combinations linked to hypertension.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# Technologies
# -----------------------------
st.markdown("""
<div class="section-header">
    <h2>🛠️ Technologies & Models</h2>
    <p>Machine learning + data mining tools used in this project</p>
</div>
""", unsafe_allow_html=True)

tc1, tc2, tc3, tc4, tc5 = st.columns(5, gap="medium")
with tc1:
    st.markdown("""<div class="tech-card"><h4>🌳 Random Forest</h4><p>Ensemble trees</p></div>""", unsafe_allow_html=True)
with tc2:
    st.markdown("""<div class="tech-card"><h4>🧠 MLP</h4><p>Neural Network</p></div>""", unsafe_allow_html=True)
with tc3:
    st.markdown("""<div class="tech-card"><h4>🔗 Apriori</h4><p>Association rules</p></div>""", unsafe_allow_html=True)
with tc4:
    st.markdown("""<div class="tech-card"><h4>📊 Plotly</h4><p>Interactive charts</p></div>""", unsafe_allow_html=True)
with tc5:
    st.markdown("""<div class="tech-card"><h4>🐍 Python</h4><p>Scikit-learn</p></div>""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# Radar chart
# -----------------------------
st.markdown("""
<div class="section-header">
    <h2>🎯 Risk Factor Categories</h2>
    <p>Multiple dimensions used in screening</p>
</div>
""", unsafe_allow_html=True)

categories = ["Demographics", "Vitals & Medical", "Lifestyle", "Lab Results", "Environment"]
values = [4, 6, 6, 5, 5]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=values,
    theta=categories,
    fill="toself",
    name="Factor Count"
))
fig.update_layout(
    showlegend=False,
    height=480,
    margin=dict(l=60, r=60, t=30, b=30),
    polar=dict(radialaxis=dict(range=[0, 8], visible=True))
)

cc1, cc2, cc3 = st.columns([1, 2, 1])
with cc2:
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# -----------------------------
# CTA
# -----------------------------
st.markdown("""
<div class="cta-section">
    <h2>🚀 Ready to Get Started?</h2>
    <p>Choose a module below to continue.</p>
</div>
""", unsafe_allow_html=True)

cta1, cta2, cta3 = st.columns([1, 2, 1])
with cta2:
    a, b = st.columns(2, gap="medium")
    with a:
        if st.button("🧠 Risk Prediction", use_container_width=True):
            st.switch_page("pages/1_Prediction.py")
    with b:
        if st.button("🔗 Association Rules", use_container_width=True):
            st.switch_page("pages/2_Association_Rules.py")

st.markdown("---")

# -----------------------------
# Disclaimer + Footer
# -----------------------------
st.markdown("""
<div style="background: #fff7ed; padding: 1.6rem; border-radius: 12px; border-left: 5px solid #f59e0b; margin: 1.5rem 0;">
    <h3 style="color: #92400e; margin-top: 0;">⚕️ Medical Disclaimer</h3>
    <p style="color: #9a3412; margin: 0; line-height: 1.6;">
        This tool is for educational and informational purposes only. It does not provide medical advice,
        diagnosis, or treatment. Please consult a healthcare professional for proper medical guidance.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1.5rem 0;">
    <p style="font-size: 1rem; margin-bottom: 0.4rem;"><strong>Hypertension Risk Predictor</strong></p>
    <p style="font-size: 0.9rem; margin: 0;">Powered by Machine Learning | Built with Streamlit</p>
    <p style="font-size: 0.85rem; margin-top: 0.8rem; color: #94a3b8;">© 2026 Hypertension Risk Predictor</p>
</div>
""", unsafe_allow_html=True)
