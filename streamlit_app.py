"""HomeMade English — Streamlit entry point.

Run locally:  streamlit run streamlit_app.py
Deploy:       Push to GitHub → Streamlit Community Cloud
"""

import streamlit as st
from utils.db import init_db
from utils.session_state import init_session_state
from utils.styles import inject_css

st.set_page_config(
    page_title="HomeMade English",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database and Session State
init_db()
init_session_state()
inject_css()

# --- Sidebar branding ---
with st.sidebar:
    st.markdown("# 🌌 HomeMade English")
    st.caption("Пошаговое изучение английского")
    if st.session_state.username:
        st.markdown(f"👤 **{st.session_state.username}**")
    st.divider()

# --- Navigation ---
home = st.Page("pages/home.py", title="Главная", icon="🏠", default=True)
topics = st.Page("pages/topics.py", title="Темы", icon="📚")
theory = st.Page("pages/theory.py", title="Теория", icon="📖")
practice = st.Page("pages/practice.py", title="Практика", icon="🎯")
mix_page = st.Page("pages/mix_practice.py", title="Микс-тренировка", icon="🧠")
profile = st.Page("pages/profile.py", title="Профиль", icon="👤")

pg = st.navigation(
    {
        "Обучение": [home, topics, theory, practice, mix_page],
        "Аккаунт": [profile],
    }
)
pg.run()
