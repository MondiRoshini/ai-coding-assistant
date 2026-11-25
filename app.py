import streamlit as st

from database.db import (
    create_tables,
    save_skill_level,
    load_skill_level
)

from modules import query
from modules import code_generator
from modules import error_detector
from modules import code_explainer

# Create database tables
create_tables()

st.set_page_config(
    page_title="AI Coding Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom Professional CSS Styling Injection
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* Apply modern typography */
html, body, [class*="css"], .stMarkdown, p, span, label, input, select, textarea {
    font-family: 'Outfit', sans-serif !important;
}

code, pre, [style*="font-family:monospace"], .stCodeBlock, div[data-testid="stMarkdownContainer"] pre {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13.5px !important;
}

/* Gradient Header */
.main-header {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.8rem;
    margin-bottom: 0.1rem;
    letter-spacing: -0.02em;
}

.sub-header-caption {
    color: #64748b;
    font-size: 1.1rem;
    font-weight: 400;
    margin-bottom: 2rem;
}

/* Premium Card Style (Glassmorphism inspired) */
.premium-card {
    background-color: rgba(99, 102, 241, 0.05) !important;
    border: 1px solid rgba(168, 85, 247, 0.2) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    margin: 16px 0 !important;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05) !important;
}

/* Style standard Streamlit buttons with modern gradients and animations */
div.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 10px 24px !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    transition: all 0.25s ease !important;
    width: auto !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4) !important;
    background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%) !important;
    color: #ffffff !important;
}

div.stButton > button:active {
    transform: translateY(1px) !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3) !important;
}

/* Style text inputs & textareas */
div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1px solid rgba(168, 85, 247, 0.2) !important;
    transition: border-color 0.2s ease !important;
}

/* Styled level badge */
.level-badge {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 10px;
    padding: 8px 12px;
    font-weight: 600;
    color: #8b5cf6;
    display: inline-block;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# Load saved skill level
if "skill_level" not in st.session_state:
    st.session_state.skill_level = load_skill_level()

# Header
st.markdown('<div class="main-header">🤖 AI Coding Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header-caption">Learn • Build • Improve • Debug</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🎯 Adaptive Learning")

    level = st.selectbox(
        "Select Your Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ],
        index=[
            "Beginner",
            "Intermediate",
            "Advanced"
        ].index(st.session_state.skill_level)
    )

    if level != st.session_state.skill_level:
        st.session_state.skill_level = level
        save_skill_level(level)

    st.markdown(f'<div class="level-badge">Current Level: {level}</div>', unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "📚 Select Module",
        [
            "Query Interface",
            "Code Generator",
            "Error Detector",
            "Code Explainer"
        ]
    )

# Main Content Area

if page == "Query Interface":
    query.run()

elif page == "Code Generator":
    code_generator.run()

elif page == "Error Detector":
    error_detector.run()

elif page == "Code Explainer":
    code_explainer.run()