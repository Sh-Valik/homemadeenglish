"""Practice page — handles all 3 practice stages with interactive exercises."""

import streamlit as st
from utils.content_loader import calculate_stars
from utils.session_state import (
    is_logged_in,
    get_progress,
    log_exercise_result,
    complete_stage,
    get_error_log,
)
from utils.practice_logic import (
    prepare_exercises,
    check_answer,
    STAGE_LABELS,
    STAGE_TYPE_MAP,
)
from utils.styles import tts_button


def _advance(prac, topic_id, stage):
    """Advance to next exercise or results."""
    prac["current_index"] += 1
    prac["selected_words"] = []
    prac["feedback"] = None

    if prac["current_index"] >= prac["total"]:
        stars = calculate_stars(prac["correct_count"], prac["total"])
        prac["stars"] = stars
        prac["state"] = "results"
        if not prac.get("is_mix"):
            complete_stage(topic_id, stage, prac["correct_count"], prac["total"], stars)
    else:
        prac["state"] = "showing"
    st.rerun()


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

stage = st.session_state.get("_practice_stage", 1)

# --- Initialize practice session ---
prac = st.session_state.get("practice")
if prac is None or prac.get("topic_id") != topic_id or prac.get("stage") != stage:
    error_log = get_error_log()
    exercises = prepare_exercises(
        topic_id, stage, error_log=error_log
    )
    if not exercises:
        st.error("Нет упражнений для этого этапа")
        if st.button("← Назад"):
            st.switch_page("pages/topics.py")
        st.stop()

    st.session_state.practice = {
        "topic_id": topic_id,
        "stage": stage,
        "exercises": exercises,
        "current_index": 0,
        "correct_count": 0,
        "total": len(exercises),
        "state": "showing",  # showing | answered | results
        "feedback": None,
        "selected_words": [],
        "stars": 0,
        "is_mix": False,
    }

prac = st.session_state.practice

# --- RESULTS SCREEN ---
if prac["state"] == "results":
    pct = round((prac["correct_count"] / prac["total"]) * 100) if prac["total"] > 0 else 0
    stars = prac["stars"]
    star_str = "⭐" * stars + "☆" * (3 - stars)
    emoji = "🎉" if stars == 3 else ("👏" if stars >= 2 else ("👍" if stars >= 1 else "💪"))
    msg = "Отлично!" if stars == 3 else ("Хорошо!" if stars >= 2 else ("Неплохо!" if stars >= 1 else "Попробуйте ещё раз"))

    st.markdown(
        f'<div class="results-screen animate-in">'
        f'<div class="results-emoji">{emoji}</div>'
        f"<h2>{msg}</h2>"
        f'<p style="color:#94a3b8">{STAGE_LABELS.get(stage, "Практика")} завершена</p>'
        f'<div class="results-stars">{star_str}</div>'
        f'<p style="font-size:1.3rem"><strong>{prac["correct_count"]}/{prac["total"]}</strong> правильных — <strong>{pct}%</strong> точность</p>'
        f"</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if stage < 3:
            if st.button("Следующий этап →", type="primary", use_container_width=True):
                st.session_state._practice_stage = stage + 1
                st.session_state.practice = None
                st.rerun()
        else:
            if st.button("🎓 Завершить", type="primary", use_container_width=True):
                st.switch_page("pages/topics.py")
    with c2:
        if st.button("🔄 Повторить", use_container_width=True):
            st.session_state.practice = None
            st.rerun()
    with c3:
        if st.button("📖 К теории", use_container_width=True):
            st.session_state.practice = None
            st.switch_page("pages/theory.py")
    st.stop()

# --- EXERCISE DISPLAY ---
ex = prac["exercises"][prac["current_index"]]

# Progress header
progress_pct = (prac["current_index"] / prac["total"]) * 100
st.progress(progress_pct / 100, text=f'{prac["current_index"] + 1} / {prac["total"]}')
st.markdown(f"**{STAGE_LABELS.get(stage, 'Практика')}**")

# --- STAGE 1: Russian → English (word bank) ---
if stage == 1:
    st.markdown(
        f'<div class="practice-prompt">{ex.get("prompt", "")}</div>',
        unsafe_allow_html=True,
    )

    if prac["state"] == "showing":
        # Display constructed answer
        selected = prac["selected_words"]
        if selected:
            answer_text = " ".join([w for _, w in selected])
            st.markdown(
                f'<div class="answer-display">{answer_text}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="answer-display" style="color:#64748b">Нажмите на слова ниже</div>',
                unsafe_allow_html=True,
            )

        # Word bank
        words = ex.get("words", [])
        selected_indices = {idx for idx, _ in selected}
        cols = st.columns(min(len(words), 5))
        for i, word in enumerate(words):
            with cols[i % min(len(words), 5)]:
                is_sel = i in selected_indices
                if st.button(
                    f"~~{word}~~" if is_sel else word,
                    key=f"w_{i}",
                    disabled=is_sel,
                    use_container_width=True,
                ):
                    prac["selected_words"].append((i, word))
                    st.rerun()

        # Remove last word
        bc1, bc2 = st.columns(2)
        with bc1:
            if selected and st.button("↩️ Убрать последнее слово"):
                prac["selected_words"].pop()
                st.rerun()
        with bc2:
            if selected and st.button("✅ Проверить", type="primary"):
                user_answer = " ".join([w for _, w in prac["selected_words"]])
                result = check_answer(topic_id, stage, ex, user_answer)
                if result["correct"]:
                    prac["correct_count"] += 1
                log_exercise_result(
                    topic_id, STAGE_TYPE_MAP[stage], result["correct"], ex.get("prompt", "")
                )
                prac["feedback"] = result
                prac["state"] = "answered"
                st.rerun()

    elif prac["state"] == "answered":
        # Show answer
        answer_text = " ".join([w for _, w in prac["selected_words"]])
        st.markdown(
            f'<div class="answer-display">{answer_text}</div>',
            unsafe_allow_html=True,
        )
        fb = prac["feedback"]
        if fb["correct"]:
            st.markdown(
                '<div class="feedback-correct">✅ Правильно!</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="feedback-wrong">❌ Неправильно<br>'
                f'Правильный ответ: <strong>{fb["correct_answer"]}</strong></div>',
                unsafe_allow_html=True,
            )
        if fb.get("explanation"):
            st.info(f'💡 {fb["explanation"]}')
        if fb.get("correct_answer"):
            tts_button(fb["correct_answer"])

        if st.button("Далее →", type="primary", use_container_width=True):
            _advance(prac, topic_id, stage)

# --- STAGE 2: English → Russian (options) ---
elif stage == 2:
    st.markdown(
        f'<div class="practice-prompt">{ex.get("prompt", "")}</div>',
        unsafe_allow_html=True,
    )
    tts_button(ex.get("prompt", ""))

    options = ex.get("options", [])

    if prac["state"] == "showing":
        cols = st.columns(2)
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if st.button(opt, key=f"opt_{i}", use_container_width=True):
                    result = check_answer(topic_id, stage, ex, opt)
                    if result["correct"]:
                        prac["correct_count"] += 1
                    log_exercise_result(
                        topic_id, STAGE_TYPE_MAP[stage], result["correct"], ex.get("prompt", "")
                    )
                    prac["feedback"] = result
                    prac["feedback"]["user_answer"] = opt
                    prac["state"] = "answered"
                    st.rerun()

    elif prac["state"] == "answered":
        fb = prac["feedback"]
        cols = st.columns(2)
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if opt == fb["correct_answer"]:
                    st.success(f"✅ {opt}")
                elif opt == fb.get("user_answer") and not fb["correct"]:
                    st.error(f"❌ {opt}")
                else:
                    st.button(opt, key=f"opt_d_{i}", disabled=True, use_container_width=True)

        if fb.get("explanation"):
            st.info(f'💡 {fb["explanation"]}')

        if st.button("Далее →", type="primary", use_container_width=True):
            _advance(prac, topic_id, stage)

# --- STAGE 3: Fill in the blank (options) ---
elif stage == 3:
    sentence = ex.get("sentence", "")
    parts = sentence.split("___")
    display = " ___ ".join(parts)

    if prac["state"] == "answered" and prac["feedback"]:
        filled = prac["feedback"]["correct_answer"]
        color = "#22c55e" if prac["feedback"]["correct"] else "#ef4444"
        display = f'<span style="color:{color};font-weight:700">{filled}</span>'.join(parts)

    st.markdown(
        f'<div class="fill-sentence">{display}</div>',
        unsafe_allow_html=True,
    )

    options = ex.get("options", [])

    if prac["state"] == "showing":
        cols = st.columns(2)
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if st.button(opt, key=f"fb_{i}", use_container_width=True):
                    result = check_answer(topic_id, stage, ex, opt)
                    if result["correct"]:
                        prac["correct_count"] += 1
                    log_exercise_result(
                        topic_id, STAGE_TYPE_MAP[stage], result["correct"], ex.get("sentence", "")
                    )
                    prac["feedback"] = result
                    prac["feedback"]["user_answer"] = opt
                    prac["state"] = "answered"
                    st.rerun()

    elif prac["state"] == "answered":
        fb = prac["feedback"]
        cols = st.columns(2)
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if opt == fb["correct_answer"]:
                    st.success(f"✅ {opt}")
                elif opt == fb.get("user_answer") and not fb["correct"]:
                    st.error(f"❌ {opt}")
                else:
                    st.button(opt, key=f"fb_d_{i}", disabled=True, use_container_width=True)

        if fb.get("explanation"):
            st.info(f'💡 {fb["explanation"]}')
        if fb.get("correct_answer"):
            tts_button(fb["correct_answer"])

        if st.button("Далее →", type="primary", use_container_width=True):
            _advance(prac, topic_id, stage)
