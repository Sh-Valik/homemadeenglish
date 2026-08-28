"""Profile page — statistics, star guide, and progress reset."""

import streamlit as st
from utils.session_state import (
    is_logged_in,
    get_stats,
    reset_all_progress,
    get_top_mistakes,
)


if not is_logged_in():
    st.warning("Пожалуйста, войдите на главной странице")
    if st.button("🏠 На главную"):
        st.switch_page("pages/home.py")
    st.stop()

st.markdown(f"# 👤 Профиль: {st.session_state.username}")

col_h1, col_h2 = st.columns([0.8, 0.2])
with col_h2:
    if st.button("🚪 Выйти"):
        # Just clear the local session — progress stays in the DB untouched.
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.practice = None
        st.session_state.mix_practice = None
        st.switch_page("pages/home.py")

st.divider()

# --- Statistics ---
stats = get_stats()

st.markdown("### 📊 Статистика")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        '<div class="stat-card">'
        '<div class="stat-icon">📚</div>'
        f'<div class="stat-value">{stats["topics_completed"]}</div>'
        '<div class="stat-label">Тем завершено</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        '<div class="stat-card">'
        '<div class="stat-icon">⭐</div>'
        f'<div class="stat-value">{stats["total_stars"]}</div>'
        f'<div class="stat-label">Звёзд из {stats["max_possible_stars"]}</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        '<div class="stat-card">'
        '<div class="stat-icon">✅</div>'
        f'<div class="stat-value">{stats["total_exercises_attempted"]}</div>'
        '<div class="stat-label">Упражнений решено</div></div>',
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        '<div class="stat-card">'
        '<div class="stat-icon">🎯</div>'
        f'<div class="stat-value">{stats["overall_accuracy"]}%</div>'
        '<div class="stat-label">Общая точность</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- Star Guide ---
with st.container(border=True):
    st.markdown("### 🌟 Как получить звёзды?")
    st.caption(
        "За каждую тему можно заработать максимум 9 звёзд "
        "(по 3 звезды за каждый этап практики)."
    )
    st.markdown("""
    - ⭐ **1 звезда:** от 50% правильных ответов
    - ⭐⭐ **2 звезды:** от 70% правильных ответов
    - ⭐⭐⭐ **3 звезды:** от 90% правильных ответов
    """)

# --- Top Mistakes ---
mistakes = get_top_mistakes(10)
if mistakes:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📉 Ваши частые ошибки", expanded=False):
        for m in mistakes:
            st.markdown(
                f'<div class="mistake-item">• {m["prompt"]} '
                f'<span class="mistake-count">({m["count"]} раз)</span></div>',
                unsafe_allow_html=True,
            )

# --- Danger Zone ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

with st.container(border=True):
    st.markdown("### ⚠️ Опасная зона")
    st.caption(
        "Удаление прогресса приведет к безвозвратной потере всей истории "
        "прохождения уроков и статистики."
    )
    if st.button("🗑️ Сбросить весь прогресс", type="primary"):
        reset_all_progress()
        st.toast("✅ Прогресс успешно очищен")
        st.rerun()
