"""Topics page — list of all topics with progress, unlock status, and stars."""

import streamlit as st
from utils.content_loader import load_topics_list
from utils.session_state import (
    get_progress,
    is_logged_in,
    is_topic_unlocked,
    get_top_mistakes,
)


def _calc_progress_pct(prog):
    if not prog or (not prog.get("theory_completed") and prog.get("practice_stage", 0) == 0):
        return 0
    p = 0
    if prog.get("theory_completed"):
        p += 25
    p += prog.get("practice_stage", 0) * 25
    return min(p, 100)


if not is_logged_in():
    st.warning("Пожалуйста, войдите на главной странице")
    if st.button("🏠 На главную"):
        st.switch_page("pages/home.py")
    st.stop()

topics_meta = load_topics_list()

# --- Header ---
st.markdown("# 📚 Темы")
st.caption("Изучайте темы последовательно — от простого к сложному")

# --- Mix Banner ---
st.markdown(
    '<div class="mix-banner">'
    "<h3>🧠 Повторить сегодня</h3>"
    "<p>Микс-тренировка по пройденным темам для закрепления</p>"
    "</div>",
    unsafe_allow_html=True,
)
if st.button("🧠 Начать микс-тренировку", use_container_width=True):
    st.switch_page("pages/mix_practice.py")

st.divider()

# --- Mistakes Section ---
mistakes = get_top_mistakes(5)
if mistakes:
    with st.expander("📉 Ваши частые ошибки", expanded=False):
        for m in mistakes:
            st.markdown(
                f'<div class="mistake-item">• {m["prompt"]} '
                f'<span class="mistake-count">({m["count"]} раз)</span></div>',
                unsafe_allow_html=True,
            )

# --- Topics Grid ---
topics = topics_meta["topics"]
for i in range(0, len(topics), 2):
    cols = st.columns(2)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= len(topics):
            break
        topic = topics[idx]
        topic_id = topic["id"]
        prog = get_progress(topic_id)
        unlocked = is_topic_unlocked(topic_id, topics_meta)
        completed = prog.get("completed", False)
        total_stars = prog.get("stars_ru_en", 0) + prog.get("stars_en_ru", 0) + prog.get("stars_fill_blank", 0)
        progress_pct = _calc_progress_pct(prog)

        with col:
            status_class = "locked" if not unlocked else ("completed" if completed else "")
            icon = "🔒" if not unlocked else topic.get("icon", "📘")
            stars_html = f'<div class="topic-stars">{"⭐" * min(total_stars, 9)}</div>' if unlocked and total_stars > 0 else ""
            progress_bar = ""
            if unlocked:
                fill_class = "complete" if completed else ""
                progress_bar = (
                    f'<div class="progress-bar-custom">'
                    f'<div class="progress-fill-custom {fill_class}" style="width:{progress_pct}%"></div>'
                    f"</div>"
                )

            st.markdown(
                f'<div class="glass-card {status_class}">'
                f'<div class="topic-card-inner">'
                f'<div class="topic-icon-big">{icon}</div>'
                f"<div>"
                f'<div class="topic-title">{topic["title"]}</div>'
                f'<div class="topic-subtitle">{topic["title_ru"]}</div>'
                f"{progress_bar}"
                f"{stars_html}"
                f"</div>"
                f'<div style="margin-left:auto"><div class="topic-level">Ур. {topic.get("level", idx + 1)}</div></div>'
                f"</div></div>",
                unsafe_allow_html=True,
            )

            if unlocked:
                if st.button(
                    f"{'📖 Повторить' if completed else '📖 Изучить'} {topic['title']}",
                    key=f"topic_{topic_id}",
                    use_container_width=True,
                ):
                    st.session_state.selected_topic_id = topic_id
                    st.switch_page("pages/theory.py")
