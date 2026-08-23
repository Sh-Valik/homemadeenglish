"""Custom CSS styles for the Streamlit app — dark space theme."""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ===== Global ===== */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #0a0e17 0%, #0f172a 50%, #0a0e17 100%);
}

/* Hide default Streamlit header/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background: rgba(10, 14, 23, 0.8) !important;
    backdrop-filter: blur(10px);
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.15);
}

section[data-testid="stSidebar"] .stMarkdown h1 {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.4rem !important;
}

/* ===== Cards ===== */
.glass-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.glass-card:hover {
    border-color: rgba(99, 102, 241, 0.35);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
}

.glass-card.locked {
    opacity: 0.5;
    filter: grayscale(0.5);
    pointer-events: none;
}

.glass-card.completed {
    border-color: rgba(34, 197, 94, 0.3);
}

/* ===== Topic Card ===== */
.topic-card-inner {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.topic-icon-big {
    font-size: 2.2rem;
    min-width: 3rem;
    text-align: center;
}

.topic-title {
    font-weight: 700;
    font-size: 1.05rem;
    color: #e2e8f0;
    margin: 0;
}

.topic-subtitle {
    color: #94a3b8;
    font-size: 0.85rem;
    margin-top: 2px;
}

.topic-stars {
    font-size: 0.85rem;
    margin-top: 4px;
}

.topic-level {
    color: #64748b;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ===== Progress Bar ===== */
.progress-bar-custom {
    width: 100%;
    height: 6px;
    background: rgba(99, 102, 241, 0.1);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 6px;
}

.progress-fill-custom {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    transition: width 0.5s ease;
}

.progress-fill-custom.complete {
    background: linear-gradient(90deg, #22c55e, #16a34a);
}

/* ===== Hero Section ===== */
.hero-section {
    text-align: center;
    padding: 3rem 1rem;
}

.hero-emoji {
    font-size: 4rem;
    margin-bottom: 1rem;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto 2rem;
}

/* ===== Stat Cards ===== */
.stat-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 1rem;
    padding: 1.2rem;
    text-align: center;
}

.stat-icon {
    font-size: 1.8rem;
    margin-bottom: 0.3rem;
}

.stat-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #e2e8f0;
}

.stat-label {
    color: #94a3b8;
    font-size: 0.8rem;
    margin-top: 2px;
}

/* ===== Theory ===== */
.theory-section {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(99, 102, 241, 0.1);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}

.theory-formula {
    background: rgba(99, 102, 241, 0.1);
    border-left: 3px solid #6366f1;
    padding: 1rem 1.2rem;
    border-radius: 0 0.5rem 0.5rem 0;
    font-family: 'Courier New', monospace;
    color: #818cf8;
    margin: 1rem 0;
    white-space: pre-wrap;
}

.theory-tip {
    background: rgba(245, 158, 11, 0.1);
    border-left: 3px solid #f59e0b;
    padding: 0.8rem 1.2rem;
    border-radius: 0 0.5rem 0.5rem 0;
    color: #fbbf24;
    margin: 1rem 0;
    font-size: 0.9rem;
}

.example-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(99, 102, 241, 0.08);
    flex-wrap: wrap;
}

.example-en {
    color: #818cf8;
    font-weight: 600;
}

.example-ru {
    color: #94a3b8;
}

/* ===== Practice ===== */
.practice-prompt {
    font-size: 1.3rem;
    font-weight: 600;
    color: #e2e8f0;
    text-align: center;
    padding: 1rem;
    margin-bottom: 1rem;
}

.word-bank {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    margin: 1rem 0;
}

.answer-display {
    min-height: 50px;
    background: rgba(99, 102, 241, 0.05);
    border: 2px dashed rgba(99, 102, 241, 0.2);
    border-radius: 0.75rem;
    padding: 0.8rem 1rem;
    margin: 1rem 0;
    text-align: center;
    font-size: 1.1rem;
    color: #e2e8f0;
    font-weight: 500;
}

.fill-sentence {
    font-size: 1.2rem;
    color: #e2e8f0;
    text-align: center;
    padding: 1rem;
    line-height: 2;
}

.blank-slot {
    background: rgba(99, 102, 241, 0.15);
    border-bottom: 2px solid #6366f1;
    padding: 0.2rem 1.5rem;
    border-radius: 0.3rem;
    color: #818cf8;
    font-weight: 600;
}

/* ===== Feedback ===== */
.feedback-correct {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 0.75rem;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
}

.feedback-wrong {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 0.75rem;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
}

/* ===== Results ===== */
.results-screen {
    text-align: center;
    padding: 2rem 1rem;
}

.results-emoji {
    font-size: 4rem;
    margin-bottom: 0.5rem;
    animation: float 3s ease-in-out infinite;
}

.results-stars {
    font-size: 2rem;
    margin: 1rem 0;
}

/* ===== Mix Banner ===== */
.mix-banner {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 1rem;
    padding: 1.5rem;
    color: white;
    margin-bottom: 1.5rem;
}

.mix-banner h3 {
    margin: 0 0 0.3rem 0;
    color: white !important;
}

.mix-banner p {
    margin: 0;
    opacity: 0.9;
}

/* ===== Buttons ===== */
div.stButton > button {
    border-radius: 0.75rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2) !important;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    color: white !important;
}

/* ===== Option Buttons ===== */
.option-btn-correct {
    background: rgba(34, 197, 94, 0.2) !important;
    border-color: #22c55e !important;
    color: #22c55e !important;
}

.option-btn-wrong {
    background: rgba(239, 68, 68, 0.2) !important;
    border-color: #ef4444 !important;
    color: #ef4444 !important;
}

/* ===== Mistakes Section ===== */
.mistake-item {
    color: #f87171;
    padding: 0.3rem 0;
}

.mistake-count {
    color: #64748b;
    font-size: 0.8rem;
}

/* ===== Animations ===== */
@keyframes slideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-in {
    animation: slideIn 0.4s ease-out;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
    .hero-title { font-size: 1.8rem; }
    .hero-emoji { font-size: 3rem; }
}
</style>
"""


def inject_css():
    """Inject custom CSS into the Streamlit app."""
    st.markdown(_CSS, unsafe_allow_html=True)


def tts_button(text, key=None):
    """Render a TTS play button using browser speechSynthesis."""
    import streamlit.components.v1 as components
    escaped = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    html = f"""
    <button onclick="
        if(window.speechSynthesis){{
            window.speechSynthesis.cancel();
            var msg=new SpeechSynthesisUtterance('{escaped}');
            msg.lang='en-US';msg.rate=0.9;
            window.speechSynthesis.speak(msg);
        }}
    " style="
        background:none;border:1px solid rgba(99,102,241,0.3);
        border-radius:0.5rem;padding:0.3rem 0.6rem;cursor:pointer;
        color:#818cf8;font-size:0.9rem;transition:all 0.2s;
    " onmouseover="this.style.background='rgba(99,102,241,0.1)'"
       onmouseout="this.style.background='none'"
    >🔊</button>
    """
    components.html(html, height=40)
