"""Theory page — displays theory sections for the selected topic."""

import streamlit as st
from utils.content_loader import load_topic_content
from utils.session_state import (
    is_logged_in,
    get_progress,
    complete_theory as mark_theory_done,
)
from utils.styles import tts_button


if not is_logged_in():
    st.warning("Пожалуйста, войдите на главной странице")
    if st.button("🏠 На главную"):
        st.switch_page("pages/home.py")
    st.stop()

topic_id = st.session_state.get("selected_topic_id")
if not topic_id:
    st.info("Выберите тему из списка")
    if st.button("📚 К списку тем"):
        st.switch_page("pages/topics.py")
    st.stop()

content = load_topic_content(topic_id)
if content is None:
    st.error("Тема не найдена")
    st.stop()

prog = get_progress(topic_id)
theory_done = prog.get("theory_completed", False)

# --- Header ---
col1, col2 = st.columns([0.07, 0.93])
with col1:
    if st.button("←"):
        st.switch_page("pages/topics.py")
with col2:
    st.markdown(
        f'### {content.get("icon", "📘")} {content["title"]}'
    )
    st.caption(content.get("title_ru", ""))

st.divider()

# --- Theory Sections ---
sections = content.get("theory", {}).get("sections", [])

for section in sections:
    st.markdown(
        f'<div class="theory-section"><h4>{section["title"]}</h4>',
        unsafe_allow_html=True,
    )

    if section.get("content"):
        st.markdown(section["content"])

    if section.get("formula"):
        st.markdown(
            f'<div class="theory-formula">{section["formula"]}</div>',
            unsafe_allow_html=True,
        )

    if section.get("examples"):
        examples_html = ""
        for ex in section["examples"]:
            examples_html += (
                f'<div class="example-item">'
                f'<span class="example-en">{ex["en"]}</span>'
                f'<span class="example-divider" style="color:#64748b;margin:0 0.5rem">—</span>'
                f'<span class="example-ru">{ex["ru"]}</span>'
                f'</div>'
            )
        st.markdown(examples_html, unsafe_allow_html=True)

    if section.get("tip"):
        st.markdown(
            f'<div class="theory-tip">💡 {section["tip"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# --- Actions ---
st.divider()

col1, col2 = st.columns(2)
with col1:
    if not theory_done:
        if st.button("✅ Теорию изучил — к практике!", type="primary", use_container_width=True):
            mark_theory_done(topic_id)
            # Init practice for stage 1
            st.session_state.practice = None
            st.session_state._practice_stage = 1
            st.switch_page("pages/practice.py")
    else:
        if st.button("🎯 Перейти к практике", type="primary", use_container_width=True):
            st.session_state.practice = None
            st.session_state._practice_stage = 1
            st.switch_page("pages/practice.py")

with col2:
    if st.button("← К списку тем", use_container_width=True):
        st.switch_page("pages/topics.py")
