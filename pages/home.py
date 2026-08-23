"""Home page — hero section with stats and authentication."""

import streamlit as st
from utils.session_state import get_stats, is_logged_in
from utils.db import get_db_session, User


def _auth_form():
    """Authentication form for Login and Registration."""
    st.markdown(
        '<div class="hero-section"><div class="hero-emoji">🌌</div>'
        '<div class="hero-title">HomeMade English</div>'
        '<p class="hero-subtitle">Пошаговое изучение английского языка</p></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            tab_login, tab_reg = st.tabs(["Вход", "Регистрация"])
            
            with tab_login:
                st.subheader("С возвращением!")
                l_username = st.text_input("Логин", key="login_user")
                l_password = st.text_input("Пароль", type="password", key="login_pass")
                if st.button("🚪 Войти", type="primary", use_container_width=True):
                    if not l_username or not l_password:
                        st.warning("Введите логин и пароль")
                    else:
                        with next(get_db_session()) as db:
                            user = db.query(User).filter_by(username=l_username).first()
                            if user and user.check_password(l_password):
                                st.session_state.user_id = user.id
                                st.session_state.username = user.username
                                st.rerun()
                            else:
                                st.error("Неверный логин или пароль")

            with tab_reg:
                st.subheader("Создать профиль")
                r_username = st.text_input("Новый логин", key="reg_user")
                r_password = st.text_input("Пароль", type="password", key="reg_pass")
                if st.button("📝 Зарегистрироваться", type="primary", use_container_width=True):
                    if not r_username or not r_password:
                        st.warning("Введите логин и пароль")
                    elif len(r_password) < 6:
                        st.warning("Пароль должен быть не короче 6 символов")
                    else:
                        with next(get_db_session()) as db:
                            if db.query(User).filter_by(username=r_username).first():
                                st.error("Пользователь с таким логином уже существует")
                            else:
                                new_user = User(username=r_username)
                                new_user.set_password(r_password)
                                db.add(new_user)
                                db.commit()
                                db.refresh(new_user)
                                
                                st.session_state.user_id = new_user.id
                                st.session_state.username = new_user.username
                                st.success("Профиль успешно создан!")
                                st.rerun()


def _home_content():
    """Main home page with stats."""
    stats = get_stats()

    st.markdown(
        '<div class="hero-section animate-in">'
        '<div class="hero-emoji">🌌</div>'
        '<div class="hero-title">HomeMade English</div>'
        '<p class="hero-subtitle">Пошаговое изучение английского языка. '
        "Теория, практика и упражнения — всё в одном месте.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # CTA button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Продолжить обучение", type="primary", use_container_width=True):
            st.switch_page("pages/topics.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            '<div class="stat-card animate-in">'
            '<div class="stat-icon">📚</div>'
            f'<div class="stat-value">{stats["topics_completed"]}</div>'
            '<div class="stat-label">Тем пройдено</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="stat-card animate-in">'
            '<div class="stat-icon">⭐</div>'
            f'<div class="stat-value">{stats["total_stars"]}</div>'
            '<div class="stat-label">Звёзд собрано</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="stat-card animate-in">'
            '<div class="stat-icon">✅</div>'
            f'<div class="stat-value">{stats["total_exercises_attempted"]}</div>'
            '<div class="stat-label">Упражнений</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            '<div class="stat-card animate-in">'
            '<div class="stat-icon">🎯</div>'
            f'<div class="stat-value">{stats["overall_accuracy"]}%</div>'
            '<div class="stat-label">Точность</div></div>',
            unsafe_allow_html=True,
        )


# --- Page entry ---
if not is_logged_in():
    _auth_form()
else:
    _home_content()
