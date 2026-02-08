import streamlit as st

def inject_global_css():
    st.markdown("""
    <style>
    /* Hide Streamlit built-in page navigation ONLY */
    [data-testid="stSidebarNav"] { display: none; }

    /* Base layout */
    .main { padding: 1.5rem; }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 3rem;
        border-radius: 18px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
    }

    .hero h1 { font-size: 3rem; margin-bottom: 0.5rem; }
    .hero p { font-size: 1.2rem; opacity: 0.95; }

    /* Chips */
    .chip-wrap { margin-top: 1.2rem; }
    .chip {
        display: inline-block;
        padding: 0.4rem 1rem;
        margin: 0.2rem;
        background: rgba(255,255,255,0.2);
        border-radius: 999px;
        font-size: 0.9rem;
    }

    /* Cards */
    .card {
        background: white;
        padding: 1.8rem;
        border-radius: 14px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #f8fafc;
        padding-top: 1rem;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
