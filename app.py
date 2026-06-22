"""
app.py — AI Scholarship Assistant PRO
Main Streamlit Application — Production-Level UI
"""

import streamlit as st
import time
import io
import os
import sys
from typing import Optional

# ─── Page Config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="AI Scholarship Assistant PRO",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "AI Scholarship Assistant PRO — Final Year Project",
    },
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
    --primary: #6C63FF;
    --primary-light: #8B85FF;
    --secondary: #00D4AA;
    --accent: #FF6B6B;
    --accent2: #FFD166;
    --bg-dark: #0D0E1A;
    --bg-card: #161728;
    --bg-card2: #1E2035;
    --border: rgba(108, 99, 255, 0.25);
    --text-primary: #F0F2FF;
    --text-secondary: #9EA3C0;
    --glass: rgba(22, 23, 40, 0.85);
    --radius: 16px;
    --radius-sm: 10px;
    --shadow: 0 8px 32px rgba(108, 99, 255, 0.15);
    --shadow-lg: 0 20px 60px rgba(0,0,0,0.5);
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary);
}

.stApp {
    background: linear-gradient(135deg, #0D0E1A 0%, #12132A 50%, #0D0E1A 100%) !important;
}

/* ── Hide Streamlit Branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111228 0%, #0D0E1A 100%) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* ── Custom Header ── */
.app-header {
    background: linear-gradient(135deg, rgba(108,99,255,0.15) 0%, rgba(0,212,170,0.08) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}

.app-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
    border-radius: var(--radius) var(--radius) 0 0;
}

.header-icon {
    font-size: 3rem;
    filter: drop-shadow(0 0 20px rgba(108,99,255,0.6));
}

.header-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #00D4AA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}

.header-subtitle {
    color: var(--text-secondary);
    font-size: 0.85rem;
    font-weight: 400;
    margin: 0;
}

/* ── Section Title ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Metric Cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 1rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.metric-card:hover::after { transform: scaleX(1); }
.metric-card:hover { border-color: var(--primary); transform: translateY(-2px); box-shadow: var(--shadow); }

.metric-value {
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    font-size: 0.7rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
    margin-top: 0.25rem;
}

/* ── Chat Messages ── */
.chat-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    max-height: 480px;
    overflow-y: auto;
    margin-bottom: 1rem;
    scrollbar-width: thin;
    scrollbar-color: var(--primary) transparent;
}

.chat-container::-webkit-scrollbar { width: 4px; }
.chat-container::-webkit-scrollbar-track { background: transparent; }
.chat-container::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 2px; }

/* ── Streamlit Native Chat Overrides ── */
div[data-testid="stChatMessage"] {
    background-color: transparent !important;
    padding: 0.5rem 0;
}

/* User Messages: Right Aligned */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatAvatarIcon-user"]) {
    flex-direction: row-reverse;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] {
    background: linear-gradient(135deg, var(--primary), var(--primary-light));
    color: white;
    padding: 0.75rem 1.2rem;
    border-radius: 18px 18px 4px 18px;
    display: inline-block;
    text-align: left;
    box-shadow: 0 4px 12px rgba(108,99,255,0.3);
}

/* AI Messages: Left Aligned */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatAvatarIcon-assistant"]) [data-testid="stMarkdownContainer"] {
    background: var(--bg-card2);
    border: 1px solid var(--border);
    color: var(--text-primary);
    padding: 0.75rem 1.2rem;
    border-radius: 18px 18px 18px 4px;
    display: inline-block;
    text-align: left;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.avatar-user { background: linear-gradient(135deg, var(--primary), var(--primary-light)); }
.avatar-ai { background: linear-gradient(135deg, var(--secondary), #00A896); }

/* ── Insight Cards ── */
.insight-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--primary);
    border-radius: var(--radius-sm);
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
    line-height: 1.6;
    color: var(--text-primary);
    transition: all 0.2s ease;
}

.insight-card:hover {
    border-left-color: var(--secondary);
    background: var(--bg-card2);
    transform: translateX(3px);
}

.insight-tag {
    display: inline-block;
    background: rgba(108,99,255,0.15);
    color: var(--primary-light);
    border: 1px solid rgba(108,99,255,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}

.tag-amount { background: rgba(0,212,170,0.1); color: var(--secondary); border-color: rgba(0,212,170,0.3); }
.tag-deadline { background: rgba(255,107,107,0.1); color: var(--accent); border-color: rgba(255,107,107,0.3); }
.tag-type { background: rgba(255,209,102,0.1); color: var(--accent2); border-color: rgba(255,209,102,0.3); }
.tag-doc { background: rgba(108,99,255,0.1); color: var(--primary-light); border-color: rgba(108,99,255,0.3); }

/* ── Score Gauge ── */
.score-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
}

.score-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
    font-size: 2rem;
    font-weight: 800;
    position: relative;
}

/* ── Upload Zone ── */
.upload-zone {
    border: 2px dashed var(--border);
    border-radius: var(--radius);
    padding: 2rem;
    text-align: center;
    background: var(--bg-card);
    transition: all 0.3s ease;
    cursor: pointer;
}

.upload-zone:hover {
    border-color: var(--primary);
    background: rgba(108,99,255,0.05);
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(108,99,255,0.3) !important;
    letter-spacing: 0.02em !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(108,99,255,0.5) !important;
}

.stButton > button:active { transform: translateY(0) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.2) !important;
}

/* ── Slider ── */
.stSlider > div > div > div { background: var(--primary) !important; }

/* ── Progress Bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0.3rem !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s !important;
}

.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
}

/* ── Divider ── */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
}

/* ── Status Badges ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}

.badge-success { background: rgba(0,212,170,0.15); color: var(--secondary); border: 1px solid rgba(0,212,170,0.3); }
.badge-warning { background: rgba(255,209,102,0.15); color: var(--accent2); border: 1px solid rgba(255,209,102,0.3); }
.badge-error { background: rgba(255,107,107,0.15); color: var(--accent); border: 1px solid rgba(255,107,107,0.3); }
.badge-info { background: rgba(108,99,255,0.15); color: var(--primary-light); border: 1px solid rgba(108,99,255,0.3); }

/* ── Sidebar Labels ── */
[data-testid="stSidebar"] label {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* ── Alert / Info boxes ── */
.stAlert {
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--bg-card2) !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

/* ── Scrollbar Global ── */
* { scrollbar-width: thin; scrollbar-color: var(--primary) transparent; }
*::-webkit-scrollbar { width: 5px; height: 5px; }
*::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 3px; }

/* ── Glow Pulse Animation ── */
@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 15px rgba(108,99,255,0.3); }
    50% { box-shadow: 0 0 30px rgba(108,99,255,0.6); }
}

.glow-active { animation: glow-pulse 2s infinite; }

/* ── Typing Indicator ── */
@keyframes typing-dot {
    0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
    40% { opacity: 1; transform: scale(1); }
}

.typing-indicator span {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--primary);
    margin: 0 2px;
    animation: typing-dot 1.2s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

/* ── Search Highlight ── */
.search-result {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 1rem;
    margin-bottom: 0.75rem;
    font-size: 0.87rem;
    line-height: 1.7;
}

mark, .highlight { background: rgba(255,209,102,0.25); color: var(--accent2); border-radius: 3px; padding: 0 2px; }

/* ── Sidebar Logo Area ── */
.sidebar-logo {
    text-align: center;
    padding: 0.5rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}

.sidebar-logo-icon {
    font-size: 2.5rem;
    display: block;
    margin-bottom: 0.3rem;
    filter: drop-shadow(0 0 12px rgba(108,99,255,0.5));
}

.sidebar-logo-text {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.05em;
}

.sidebar-logo-sub {
    font-size: 0.7rem;
    color: var(--text-secondary);
}

/* ── Download Button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--secondary), #00A896) !important;
    color: #0D0E1A !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0,212,170,0.3) !important;
}

.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0,212,170,0.5) !important;
}

/* ── Score Colors ── */
.score-excellent { color: #00D4AA; }
.score-good { color: #6C63FF; }
.score-moderate { color: #FFD166; }
.score-low { color: #FF6B6B; }

/* ── File uploader ── */
[data-testid="stFileUploaderDropzone"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--primary) !important;
    background: rgba(108,99,255,0.05) !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ─────────────────────────────────────────────
def init_session_state():
    defaults = {
        "pdf_result": None,
        "rag": None,
        "llm": None,
        "insights": None,
        "match_result": None,
        "chat_messages": [],
        "processing": False,
        "pdf_name": "",
        "search_results": [],
        "search_query": "",
        "models_loaded": False,
        "llm_status": "",
        "active_tab": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ─── Lazy Model Loading ────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_rag_pipeline():
    """Load and cache RAG pipeline (SentenceTransformer)."""
    from rag_pipeline import RAGPipeline
    return RAGPipeline(model_name="all-MiniLM-L6-v2")


@st.cache_resource(show_spinner=False)
def load_llm():
    """Load and cache LLM."""
    from granite_ai import ScholarshipLLM
    return ScholarshipLLM(model_name="google/flan-t5-base")


# ─── Helper: Score Color ───────────────────────────────────────────────────────
def get_score_color(score: int) -> str:
    if score >= 80: return "#00D4AA"
    if score >= 60: return "#6C63FF"
    if score >= 40: return "#FFD166"
    return "#FF6B6B"


def get_score_emoji(score: int) -> str:
    if score >= 80: return "🏆"
    if score >= 60: return "✅"
    if score >= 40: return "⚠️"
    return "❌"


# ─── Sidebar: Student Profile ─────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <span class="sidebar-logo-icon">🎓</span>
            <div class="sidebar-logo-text">Scholarship AI PRO</div>
            <div class="sidebar-logo-sub">Final Year Project</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">👤 Student Profile</div>', unsafe_allow_html=True)

        name = st.text_input("Full Name", value="", placeholder="Enter your name", key="p_name")
        course = st.text_input("Course / Program", value="", placeholder="e.g. B.Tech CSE", key="p_course")

        col1, col2 = st.columns(2)
        with col1:
            cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0,
                                   value=7.5, step=0.1, format="%.1f", key="p_cgpa")
        with col2:
            category = st.selectbox("Category", ["General", "SC", "ST", "OBC", "EWS", "Minority"],
                                    key="p_category")

        income = st.number_input(
            "Annual Family Income (₹)",
            min_value=0, max_value=10000000, value=400000, step=10000, key="p_income"
        )
        income_display = f"₹{income:,}"
        st.caption(f"📊 Income: {income_display}/year")

        state = st.selectbox(
            "State",
            ["", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
             "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
             "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
             "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
             "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
             "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Other"],
            key="p_state"
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Model Status
        st.markdown('<div class="section-title">🤖 Model Status</div>', unsafe_allow_html=True)
        status_text = st.session_state.get("llm_status", "Not loaded")
        if "✅" in status_text:
            st.markdown(f'<div class="status-badge badge-success">{status_text}</div>', unsafe_allow_html=True)
        elif "⚠️" in status_text:
            st.markdown(f'<div class="status-badge badge-warning">{status_text}</div>', unsafe_allow_html=True)
        elif status_text:
            st.markdown(f'<div class="status-badge badge-info">🔄 {status_text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge badge-info">⏳ Awaiting PDF upload</div>', unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Quick Tips
        with st.expander("💡 How to Use", expanded=False):
            st.markdown("""
            1. **Upload** a scholarship PDF
            2. Wait for **AI processing**
            3. View **insights & match score**
            4. **Chat** with the AI about it
            5. **Export** your analysis report
            """)

        return {
            "name": name,
            "course": course,
            "cgpa": cgpa,
            "category": category,
            "income": income,
            "state": state,
        }


# ─── Header ───────────────────────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="app-header">
        <div class="header-icon">🎓</div>
        <div>
            <h1 class="header-title">AI Scholarship Assistant PRO</h1>
            <p class="header-subtitle">
                Powered by RAG + FLAN-T5 · SentenceTransformers · FAISS · Production Ready
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── PDF Upload & Processing ──────────────────────────────────────────────────
def render_pdf_upload():
    st.markdown('<div class="section-title">📄 Upload Scholarship PDF</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your scholarship PDF here",
        type=["pdf"],
        help="Upload any scholarship brochure, circular, or notification PDF",
        key="pdf_uploader",
    )

    if uploaded_file is not None:
        if (st.session_state.pdf_name != uploaded_file.name or
                st.session_state.pdf_result is None):

            # New file detected
            st.session_state.pdf_name = uploaded_file.name
            pdf_bytes = uploaded_file.read()

            with st.spinner("🔍 Extracting and processing PDF..."):
                progress = st.progress(0, text="Reading PDF...")
                time.sleep(0.2)

                # PDF extraction
                from pdf_loader import process_pdf
                progress.progress(20, text="Cleaning text...")
                pdf_result = process_pdf(pdf_bytes)
                progress.progress(40, text="Building embeddings...")

                if pdf_result.get("error") and not pdf_result.get("chunks"):
                    st.error(f"❌ PDF Error: {pdf_result['error']}")
                    progress.empty()
                    return

                if not pdf_result.get("chunks"):
                    st.warning("⚠️ No text extracted. The PDF may be scanned/image-based.")
                    progress.empty()
                    return

                st.session_state.pdf_result = pdf_result

                # Load RAG + build index
                progress.progress(50, text="Loading embedding model...")
                try:
                    rag = load_rag_pipeline()
                    progress.progress(65, text="Building FAISS index...")
                    index_stats = rag.build_index(pdf_result["chunks"])
                    rag.clear_memory()
                    st.session_state.rag = rag
                except Exception as e:
                    st.error(f"❌ RAG Pipeline Error: {e}")
                    progress.empty()
                    return

                # Load LLM
                progress.progress(75, text="Loading LLM model...")
                try:
                    llm = load_llm()
                    llm.clear_history()
                    st.session_state.llm = llm
                    st.session_state.llm_status = llm.model_status()
                except Exception as e:
                    st.session_state.llm_status = "⚠️ Context-only mode"

                # Extract insights
                progress.progress(85, text="Extracting scholarship insights...")
                from utils import extract_all_insights
                insights = extract_all_insights(pdf_result["clean_text"])
                st.session_state.insights = insights

                # Clear old chat
                st.session_state.chat_messages = []

                progress.progress(100, text="✅ Done!")
                time.sleep(0.4)
                progress.empty()

            st.success(f"✅ **{uploaded_file.name}** processed successfully! "
                       f"({pdf_result['metadata'].get('num_chunks', 0)} chunks · "
                       f"{pdf_result['metadata'].get('page_count', 0)} pages)")

    return uploaded_file


# ─── Document Dashboard ───────────────────────────────────────────────────────
def render_dashboard():
    result = st.session_state.pdf_result
    if not result:
        st.markdown("""
        <div style="text-align:center; padding: 3rem; color: var(--text-secondary, #9EA3C0);">
            <div style="font-size:3rem; margin-bottom:1rem;">📤</div>
            <div style="font-size:1rem; font-weight:600;">Upload a scholarship PDF to get started</div>
            <div style="font-size:0.8rem; margin-top:0.5rem;">Supports multi-page PDFs up to 50MB</div>
        </div>
        """, unsafe_allow_html=True)
        return

    meta = result["metadata"]

    # ── Metric Cards
    st.markdown('<div class="section-title">📊 Document Statistics</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    metrics = [
        ("📄", f"{meta.get('page_count', 0)}", "Pages"),
        ("📝", f"{meta.get('word_count', 0):,}", "Words"),
        ("🔤", f"{meta.get('char_count', 0):,}", "Chars"),
        ("💾", f"{meta.get('file_size_kb', 0):.1f} KB", "Size"),
        ("🧩", f"{meta.get('num_chunks', 0)}", "Chunks"),
        ("🔢", f"{meta.get('num_chunks', 0)}", "Embeddings"),
    ]

    for col, (icon, val, label) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.4rem; margin-bottom:0.25rem;">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Insights Panel
    insights = st.session_state.insights
    if insights:
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔍 Extracted Scholarship Intelligence</div>', unsafe_allow_html=True)

        ic1, ic2 = st.columns(2)

        with ic1:
            # Type + Amounts
            stype = insights.get("scholarship_type", "General")
            st.markdown(f"""
            <div class="insight-card">
                <div style="margin-bottom:0.5rem;">
                    <span class="insight-tag tag-type">📋 TYPE</span>
                </div>
                <strong style="font-size:1.1rem;">{stype} Scholarship</strong>
            </div>
            """, unsafe_allow_html=True)

            amounts = insights.get("amounts", [])
            if amounts:
                amt_html = "".join(f'<span class="insight-tag tag-amount">{a}</span>' for a in amounts[:5])
                st.markdown(f"""
                <div class="insight-card">
                    <div style="margin-bottom:0.5rem;"><span class="insight-tag tag-amount">💰 AMOUNT</span></div>
                    {amt_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="insight-card"><span class="insight-tag">💰 AMOUNT</span> Not mentioned</div>',
                            unsafe_allow_html=True)

            deadlines = insights.get("deadlines", [])
            if deadlines:
                dl_html = "".join(f'<div style="padding:0.2rem 0; color:#FF6B6B;">📅 {d}</div>' for d in deadlines)
                st.markdown(f"""
                <div class="insight-card">
                    <div style="margin-bottom:0.5rem;"><span class="insight-tag tag-deadline">📅 DEADLINE</span></div>
                    {dl_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="insight-card"><span class="insight-tag tag-deadline">📅 DEADLINE</span> Not found</div>',
                            unsafe_allow_html=True)

        with ic2:
            # Eligibility
            eligibility = insights.get("eligibility", [])
            if eligibility:
                el_items = "".join(f'<li style="margin-bottom:0.4rem;">{e}</li>' for e in eligibility[:4])
                st.markdown(f"""
                <div class="insight-card" style="height:auto;">
                    <div style="margin-bottom:0.5rem;"><span class="insight-tag">✅ ELIGIBILITY</span></div>
                    <ul style="margin:0; padding-left:1.2rem; font-size:0.85rem; color:#9EA3C0;">
                        {el_items}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # Documents
            docs = insights.get("required_documents", [])
            if docs:
                doc_items = "".join(f'<li style="margin-bottom:0.4rem;">{d}</li>' for d in docs[:3])
                st.markdown(f"""
                <div class="insight-card">
                    <div style="margin-bottom:0.5rem;"><span class="insight-tag tag-doc">📋 DOCUMENTS</span></div>
                    <ul style="margin:0; padding-left:1.2rem; font-size:0.85rem; color:#9EA3C0;">
                        {doc_items}
                    </ul>
                </div>
                """, unsafe_allow_html=True)


# ─── Match Score Engine UI ────────────────────────────────────────────────────
def render_match_score(profile: dict):
    st.markdown('<div class="section-title">🎯 Scholarship Match Score</div>', unsafe_allow_html=True)

    if not st.session_state.pdf_result:
        st.info("📤 Upload a PDF first to calculate your match score.")
        return

    if st.button("🔄 Calculate Match Score", use_container_width=True, key="calc_score"):
        from utils import compute_match_score
        with st.spinner("Analyzing your profile..."):
            result = compute_match_score(
                profile,
                st.session_state.insights or {},
                st.session_state.pdf_result.get("clean_text", ""),
            )
            st.session_state.match_result = result
        st.success("✅ Match score calculated!")

    match = st.session_state.match_result
    if not match:
        st.caption("Click above to calculate your personalized match score.")
        return

    score = match["total_score"]
    color = get_score_color(score)
    emoji = get_score_emoji(score)

    # Score Display
    st.markdown(f"""
    <div class="score-container">
        <div class="score-circle" style="
            background: conic-gradient({color} {score * 3.6}deg, rgba(30,32,53,0.8) 0deg);
            box-shadow: 0 0 30px {color}40;
        ">
            <div style="
                width:90px; height:90px; border-radius:50%;
                background: #161728;
                display:flex; align-items:center; justify-content:center;
                flex-direction:column;
            ">
                <span style="font-size:1.8rem; font-weight:800; color:{color};">{score}</span>
                <span style="font-size:0.6rem; color:#9EA3C0; font-weight:500;">/ 100</span>
            </div>
        </div>
        <div style="font-size:1.2rem; font-weight:700; color:{color};">{emoji} {match['grade']} Match</div>
        <div style="font-size:0.85rem; color:#9EA3C0; margin-top:0.5rem;">{match['recommendation']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Breakdown
    st.markdown("**Score Breakdown:**")
    for factor, data in match["breakdown"].items():
        factor_score = data["score"]
        factor_max = data["max"]
        pct = int((factor_score / factor_max) * 100) if factor_max else 0
        st.markdown(f"**{factor}** — {factor_score}/{factor_max}")
        st.progress(pct / 100)
        st.caption(data["reason"])


# ─── Chat Interface ───────────────────────────────────────────────────────────
def render_chat():
    st.markdown('<div class="section-title">💬 AI Scholarship Chatbot</div>', unsafe_allow_html=True)

    if not st.session_state.pdf_result:
        st.info("📤 Upload a scholarship PDF to start chatting with the AI.")
        return

    if not st.session_state.rag or not st.session_state.llm:
        st.warning("⚙️ AI models are still loading. Please wait.")
        return

    # Chat Actions (Clear & Export)
    action_col1, action_col2, action_col3 = st.columns([2, 1, 1])
    with action_col2:
        if st.session_state.chat_messages:
            export_text = "AI Scholarship Assistant PRO - Chat History\n" + "="*45 + "\n\n"
            for msg in st.session_state.chat_messages:
                export_text += f"[{msg.get('timestamp', '')}] {msg['role'].upper()}:\n{msg['content']}\n\n"
            st.download_button("💾 Export (TXT)", data=export_text, file_name="chat_history.txt", mime="text/plain", use_container_width=True)
    with action_col3:
        if st.session_state.chat_messages:
            if st.button("🗑️ Clear Chat", key="clear_chat", use_container_width=True):
                st.session_state.chat_messages = []
                if st.session_state.llm:
                    st.session_state.llm.clear_history()
                if st.session_state.rag:
                    st.session_state.rag.clear_memory()
                st.rerun()

    # Suggested questions
    st.markdown("**💡 Suggested Questions:**")
    sugg_cols = st.columns(3)
    suggestions = [
        "What is the scholarship amount?",
        "Who is eligible to apply?",
        "What documents are required?",
        "What is the application deadline?",
        "What is the selection criteria?",
        "How to apply for this scholarship?",
    ]
    for i, (col, q) in enumerate(zip(sugg_cols * 2, suggestions)):
        with col:
            if st.button(q, key=f"sugg_{i}", use_container_width=True):
                st.session_state.pending_query = q
                st.rerun()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Render Chat History
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg['content'])
            if 'timestamp' in msg:
                st.caption(msg['timestamp'])

    # Handle pending query from suggestions
    if "pending_query" in st.session_state:
        query = st.session_state.pending_query
        del st.session_state.pending_query
        _process_chat_query(query)

    # Chat Input
    if user_input := st.chat_input("Ask me anything about this scholarship..."):
        _process_chat_query(user_input)


def _process_chat_query(query: str):
    """Core chat logic: RAG retrieval → LLM → update history."""
    rag = st.session_state.rag
    llm = st.session_state.llm

    if not rag or not llm:
        return

    import datetime
    timestamp = datetime.datetime.now().strftime("%I:%M %p")

    # Add user message to state
    st.session_state.chat_messages.append({"role": "user", "content": query, "timestamp": timestamp})
    
    # Render user message immediately
    with st.chat_message("user"):
        st.markdown(query)
        st.caption(timestamp)

    # Generate and render AI response
    with st.chat_message("assistant"):
        with st.spinner("🤖 AI is thinking..."):
            context = rag.get_context(query, top_k=4)
            answer = llm.answer(query, context)
        
        st.markdown(answer)
        st.caption(timestamp)

    # Add AI response to state
    st.session_state.chat_messages.append({"role": "assistant", "content": answer, "timestamp": timestamp})


# ─── Smart Search ─────────────────────────────────────────────────────────────
def render_smart_search():
    st.markdown('<div class="section-title">🔍 Smart Document Search</div>', unsafe_allow_html=True)

    if not st.session_state.pdf_result:
        st.info("📤 Upload a PDF to use smart search.")
        return

    search_col1, search_col2, search_col3 = st.columns([4, 1, 1])

    with search_col1:
        keyword = st.text_input(
            "Search keyword",
            placeholder="e.g. income, deadline, eligibility, documents...",
            label_visibility="collapsed",
            key="search_keyword",
        )
    with search_col2:
        search_type = st.selectbox("Mode", ["Keyword", "Semantic", "Hybrid"],
                                   label_visibility="collapsed", key="search_mode")
    with search_col3:
        search_btn = st.button("🔍 Search", use_container_width=True, key="search_btn")

    if search_btn and keyword:
        rag = st.session_state.rag
        if not rag:
            st.warning("RAG pipeline not ready.")
            return

        with st.spinner("Searching..."):
            if search_type == "Keyword":
                results = rag.keyword_search(keyword, top_n=5)
                for i, r in enumerate(results):
                    display_text = r.get("highlighted", r["chunk"])
                    display_text = display_text.replace("**", "<mark>", 1)
                    # Replace closing ** properly
                    import re as _re
                    display_text = _re.sub(r'\*\*([^*]+)\*\*', r'<mark>\1</mark>', r["chunk"])
                    display_text = display_text.replace(
                        keyword,
                        f'<mark>{keyword}</mark>',
                    )
                    st.markdown(f"""
                    <div class="search-result">
                        <div style="margin-bottom:0.4rem;">
                            <span class="insight-tag">Result {i+1}</span>
                            <span class="insight-tag tag-amount">{r['match_count']} match(es)</span>
                        </div>
                        {display_text}
                    </div>
                    """, unsafe_allow_html=True)

            elif search_type == "Semantic":
                results = rag.retrieve(keyword, top_k=5)
                for i, r in enumerate(results):
                    score_pct = int(r["score"] * 100)
                    st.markdown(f"""
                    <div class="search-result">
                        <div style="margin-bottom:0.4rem;">
                            <span class="insight-tag">Result {i+1}</span>
                            <span class="insight-tag tag-amount">Score: {score_pct}%</span>
                        </div>
                        {r['chunk']}
                    </div>
                    """, unsafe_allow_html=True)

            else:  # Hybrid
                results = rag.hybrid_search(keyword, keyword=keyword, top_k=5)
                for i, r in enumerate(results):
                    score_pct = int(r["score"] * 100)
                    kw_badge = '<span class="insight-tag tag-amount">🔑 Keyword Match</span>' \
                               if r.get("keyword_match") else ''
                    st.markdown(f"""
                    <div class="search-result">
                        <div style="margin-bottom:0.4rem;">
                            <span class="insight-tag">Result {i+1}</span>
                            <span class="insight-tag">Score: {score_pct}%</span>
                            {kw_badge}
                        </div>
                        {r['chunk']}
                    </div>
                    """, unsafe_allow_html=True)

        if not results:
            st.info(f"No results found for '{keyword}'.")


# ─── Export Panel ─────────────────────────────────────────────────────────────
def render_export(profile: dict):
    st.markdown('<div class="section-title">📥 Export Reports</div>', unsafe_allow_html=True)

    if not st.session_state.pdf_result:
        st.info("📤 Upload a PDF first to enable exports.")
        return

    from utils import export_summary_txt, export_eligibility_report_txt

    pdf_name = st.session_state.pdf_name
    meta = st.session_state.pdf_result.get("metadata", {})
    insights = st.session_state.insights or {}
    match_result = st.session_state.match_result

    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        # Full Summary Report
        summary_bytes = export_summary_txt(
            filename=pdf_name,
            metadata=meta,
            insights=insights,
            match_result=match_result,
            profile=profile if profile.get("name") else None,
        )
        st.download_button(
            label="📄 Download Full Analysis Report",
            data=summary_bytes,
            file_name=f"scholarship_analysis_{pdf_name.replace('.pdf', '')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_summary",
        )
        st.caption("Complete analysis: stats, insights, match score, profile")

    with exp_col2:
        # Eligibility Report
        elig_bytes = export_eligibility_report_txt(
            insights=insights,
            match_result=match_result,
            profile=profile if profile.get("name") else None,
        )
        st.download_button(
            label="✅ Download Eligibility Report",
            data=elig_bytes,
            file_name=f"eligibility_report_{pdf_name.replace('.pdf', '')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_elig",
        )
        st.caption("Focused eligibility criteria & document checklist")

    # Chat History Export
    if st.session_state.chat_messages:
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        chat_lines = [f"AI Scholarship Assistant PRO — Chat History", "=" * 50, ""]
        for msg in st.session_state.chat_messages:
            role = "You" if msg["role"] == "user" else "AI Assistant"
            chat_lines.append(f"[{role}]: {msg['content']}")
            chat_lines.append("")

        chat_bytes = "\n".join(chat_lines).encode("utf-8")
        st.download_button(
            label="💬 Download Chat History",
            data=chat_bytes,
            file_name=f"chat_history_{pdf_name.replace('.pdf', '')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_chat",
        )


# ─── Raw Text Viewer ──────────────────────────────────────────────────────────
def render_raw_text():
    if not st.session_state.pdf_result:
        return

    with st.expander("📖 View Extracted Text (First 3000 chars)", expanded=False):
        text = st.session_state.pdf_result.get("clean_text", "")
        st.text_area(
            "Extracted PDF Content",
            value=text[:3000] + ("..." if len(text) > 3000 else ""),
            height=300,
            disabled=True,
            key="raw_text_viewer",
        )
        st.caption(f"Showing first 3,000 of {len(text):,} characters")


# ─── Main App Layout ──────────────────────────────────────────────────────────
def main():
    profile = render_sidebar()
    render_header()

    if not st.session_state.pdf_result:
        # Landing State
        uploaded = render_pdf_upload()

        if not uploaded:
            # Feature Cards
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown("### ✨ What this system does")
            feat_cols = st.columns(4)
            features = [
                ("🔍", "RAG Pipeline", "Semantic search across scholarship documents using FAISS & SentenceTransformers"),
                ("🤖", "AI Chatbot", "FLAN-T5 powered Q&A with strict context-only answers — no hallucinations"),
                ("🎯", "Match Scoring", "Smart 0-100 match score based on income, CGPA, category & state"),
                ("📊", "Intelligence", "Auto-extracts amounts, deadlines, eligibility, and required documents"),
            ]
            for col, (icon, title, desc) in zip(feat_cols, features):
                with col:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align:left; padding:1.5rem;">
                        <div style="font-size:2rem; margin-bottom:0.75rem;">{icon}</div>
                        <div style="font-weight:700; font-size:1rem; margin-bottom:0.5rem;">{title}</div>
                        <div style="font-size:0.8rem; color:#9EA3C0; line-height:1.5;">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        # Main Workflow — Tabbed Interface
        render_pdf_upload()
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard",
            "🎯 Match Score",
            "💬 AI Chat",
            "🔍 Search",
            "📥 Export",
        ])

        with tab1:
            render_dashboard()
            render_raw_text()

        with tab2:
            render_match_score(profile)

        with tab3:
            render_chat()

        with tab4:
            render_smart_search()

        with tab5:
            render_export(profile)


if __name__ == "__main__":
    main()
