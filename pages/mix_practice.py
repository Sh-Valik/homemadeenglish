"""Mix practice page — mixed exercises from completed topics."""

import streamlit as st
from utils.content_loader import calculate_stars
from utils.session_state import (
    is_logged_in,
    log_exercise_result,
)
from utils.practice_logic import (
    prepare_mix_exercises,
    check_answer,
    STAGE_LABELS,
    STAGE_TYPE_MAP,
)
from utils.styles import tts_button


from utils.session_state import get_error_log


def _mix_advance(prac):
    """Advance to next exercise or show results."""
    prac["current_index"] += 1
    prac["selected_words"] = []
    prac["feedback"] = None
    if prac["current_index"] >= prac["total"]:
        prac["state"] = "results"
    else:
        prac["state"] = "showing"
    st.rerun()


if not is_logged_in():
    st.warning("Пожалуйста, войдите на главной странице")
    if st.button("🏠 На главную"):
        st.switch_page("pages/home.py")
    st.stop()

# --- Initialize mix session ---
prac = st.session_state.get("mix_practice")
if prac is None:
    # Need to fetch everything to pass to prepare_mix_exercises
    # Note: prepare_mix_exercises actually imports get_due_review_items directly
    # and we can rewrite it slightly, but here we just pass None for progress 
    # since we refactored prepare_mix_exercises to use DB directly inside it, 
    # wait, I should update prepare_mix_exercises first.
    # Let's just fix the call:
    exercises = prepare_mix_exercises()
    if not exercises:
        st.info("🎓 Пока нет пройденных тем для повторения.")
        st.caption("Завершите хотя бы одну тему, чтобы открыть микс-тренировку.")
        if st.button("📚 К темам"):
            st.switch_page("pages/topics.py")
        st.stop()

    st.session_state.mix_practice = {
        "exercises": exercises,
        "current_index": 0,
        "correct_count": 0,
        "total": len(exercises),
        "state": "showing",
        "feedback": None,
        "selected_words": [],
    }

prac = st.session_state.mix_practice

# --- RESULTS ---
if prac["state"] == "results":
    pct = round((prac["correct_count"] / prac["total"]) * 100) if prac["total"] > 0 else 0
    stars = calculate_stars(prac["correct_count"], prac["total"])
    emoji = "🎉" if stars == 3 else ("👏" if stars >= 2 else ("👍" if stars >= 1 else "💪"))
    msg = "Отлично!" if stars == 3 else ("Хорошо!" if stars >= 2 else ("Неплохо!" if stars >= 1 else "Попробуйте ещё"))

    st.markdown(
        f'<div class="results-screen animate-in">'
        f'<div class="results-emoji">{emoji}</div>'
        f"<h2>{msg}</h2>"
        f'<p style="color:#94a3b8">Микс-тренировка завершена</p>'
        f'<p style="font-size:1.3rem"><strong>{prac["correct_count"]}/{prac["total"]}</strong> правильных — <strong>{pct}%</strong></p>'
        f"</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Повторить микс", type="primary", use_container_width=True):
            st.session_state.mix_practice = None
            st.rerun()
    with c2:
        if st.button("📚 К темам", use_container_width=True):
            st.session_state.mix_practice = None
            st.switch_page("pages/topics.py")
    st.stop()

# --- EXERCISE ---
ex = prac["exercises"][prac["current_index"]]
current_stage = ex.get("stage", 1)
current_topic = ex.get("topic_id", "")

progress_pct = (prac["current_index"] / prac["total"]) * 100
st.progress(progress_pct / 100, text=f'🧠 Микс — {prac["current_index"] + 1} / {prac["total"]}')
st.caption(f'{STAGE_LABELS.get(current_stage, "Микс")}')

prompt = ex.get("prompt") or ex.get("sentence", "")

if current_stage == 1:
    # Word bank
    st.markdown(f'<div class="practice-prompt">{prompt}</div>', unsafe_allow_html=True)

    if prac["state"] == "showing":
        selected = prac["selected_words"]
        if selected:
            st.markdown(
                f'<div class="answer-display">{" ".join([w for _, w in selected])}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="answer-display" style="color:#64748b">Нажмите на слова</div>',
                unsafe_allow_html=True,
            )

        words = ex.get("words", [])
        selected_indices = {idx for idx, _ in selected}
        cols = st.columns(min(len(words), 5))
        for i, word in enumerate(words):
            with cols[i % min(len(words), 5)]:
                if st.button(word, key=f"mw_{i}", disabled=i in selected_indices, use_container_width=True):
                    prac["selected_words"].append((i, word))
                    st.rerun()

        bc1, bc2 = st.columns(2)
        with bc1:
            if selected and st.button("↩️ Убрать"):
                prac["selected_words"].pop()
                st.rerun()
        with bc2:
            if selected and st.button("✅ Проверить", type="primary"):
                user_answer = " ".join([w for _, w in prac["selected_words"]])
                result = check_answer(current_topic, current_stage, ex, user_answer)
                if result["correct"]:
                    prac["correct_count"] += 1
                log_exercise_result(current_topic, STAGE_TYPE_MAP[current_stage], result["correct"], prompt)
                prac["feedback"] = result
                prac["state"] = "answered"
                st.rerun()

    elif prac["state"] == "answered":
        fb = prac["feedback"]
        st.markdown(
            f'<div class="answer-display">{" ".join([w for _, w in prac["selected_words"]])}</div>',
            unsafe_allow_html=True,
        )
        if fb["correct"]:
            st.markdown('<div class="feedback-correct">✅ Правильно!</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="feedback-wrong">❌ Правильный ответ: <strong>{fb["correct_answer"]}</strong></div>',
                unsafe_allow_html=True,
            )
        if fb.get("explanation"):
            st.info(f'💡 {fb["explanation"]}')
        if st.button("Далее →", type="primary", use_container_width=True):
            _mix_advance(prac)

else:
    # Options (stage 2 or 3)
    if current_stage == 3:
        parts = prompt.split("___")
        display = " ___ ".join(parts)
        if prac["state"] == "answered" and prac["feedback"]:
            filled = prac["feedback"]["correct_answer"]
            color = "#22c55e" if prac["feedback"]["correct"] else "#ef4444"
            display = f'<span style="color:{color};font-weight:700">{filled}</span>'.join(parts)
        st.markdown(f'<div class="fill-sentence">{display}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="practice-prompt">{prompt}</div>', unsafe_allow_html=True)
        tts_button(prompt)

    options = ex.get("options", [])

    if prac["state"] == "showing":
        cols = st.columns(2)
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if st.button(opt, key=f"mo_{i}", use_container_width=True):
                    result = check_answer(current_topic, current_stage, ex, opt)
                    if result["correct"]:
                        prac["correct_count"] += 1
                    log_exercise_result(current_topic, STAGE_TYPE_MAP[current_stage], result["correct"], prompt)
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
                    st.button(opt, key=f"mo_d_{i}", disabled=True, use_container_width=True)

        if fb.get("explanation"):
            st.info(f'💡 {fb["explanation"]}')

        if st.button("Далее →", type="primary", use_container_width=True):
            _mix_advance(prac)
