/**
 * Main application module — orchestrates routing and page rendering.
 */
const App = {
    router: null,
    currentUser: null,

    async init() {
        this._createStarfield();
        this.router = new Router();
        
        // Try to fetch current user
        try {
            const r = await fetch('/api/me');
            if (r.ok) {
                const data = await r.json();
                this.currentUser = data.user;
            }
        } catch (e) {}
        
        this._updateNavVisibility();

        this.router
            .on('/', () => this.showHome())
            .on('/login', () => this.showLogin())
            .on('/register', () => this.showRegister())
            .on('/profile', () => this.showProfile())
            .on('/topics', () => this.checkAuth(() => this.showTopics()))
            .on('/topics/:id', (id) => this.checkAuth(() => this.showTopic(id)))
            .on('/topics/:id/practice/:stage', (id, stage) => this.checkAuth(() => this.showPractice(id, parseInt(stage))))
            .on('/mix', () => this.checkAuth(() => this.showPractice('mix', 'mix')))
            .on('/stats', () => this.checkAuth(() => this.showProfile()));

        this.router.resolve();
    },

    checkAuth(callback) {
        if (!this.currentUser) {
            window.location.hash = '#/login';
            return;
        }
        callback();
    },

    _updateNavVisibility() {
        const navProfile = document.getElementById('nav-profile');
        const navLogin = document.getElementById('nav-login');
        if (this.currentUser) {
            if (navProfile) navProfile.style.display = 'flex';
            if (navLogin) navLogin.style.display = 'none';
        } else {
            if (navProfile) navProfile.style.display = 'none';
            if (navLogin) navLogin.style.display = 'flex';
        }
    },

    _createStarfield() {
        const sf = document.getElementById('starfield');
        if (!sf) return;
        const count = 80;
        for (let i = 0; i < count; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            const size = Math.random() * 2.5 + 0.5;
            star.style.cssText = `
                width:${size}px;height:${size}px;
                top:${Math.random()*100}%;left:${Math.random()*100}%;
                --dur:${Math.random()*3+2}s;
                animation-delay:${Math.random()*3}s;
                opacity:${Math.random()*0.5+0.2};
            `;
            sf.appendChild(star);
        }
    },

    _setContent(html) {
        document.getElementById('app').innerHTML = html;
        window.scrollTo({top: 0, behavior: 'smooth'});
    },

    _showLoading() {
        this._setContent('<div class="loading-screen"><div class="loading-spinner"></div><p>Загрузка...</p></div>');
    },

    toast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    },

    // ===== HOME PAGE =====
    async showHome() {
        let stats = {topics_completed: 0, total_stars: 0, total_exercises_attempted: 0, overall_accuracy: 0};
        try {
            const r = await fetch('/api/stats');
            stats = await r.json();
        } catch (e) {}

        this._setContent(`
            <div class="hero">
                <div class="hero-emoji">🌌</div>
                <h1>English Learner</h1>
                <p>Пошаговое изучение английского языка. Теория, практика и упражнения — всё в одном месте.</p>
                <a href="#/topics" class="btn-primary">🚀 Начать обучение</a>
                <div class="hero-stats">
                    <div class="hero-stat">
                        <div class="stat-value">${stats.topics_completed}</div>
                        <div class="stat-label">Тем пройдено</div>
                    </div>
                    <div class="hero-stat">
                        <div class="stat-value">⭐ ${stats.total_stars}</div>
                        <div class="stat-label">Звёзд собрано</div>
                    </div>
                    <div class="hero-stat">
                        <div class="stat-value">${stats.total_exercises_attempted}</div>
                        <div class="stat-label">Упражнений</div>
                    </div>
                    <div class="hero-stat">
                        <div class="stat-value">${stats.overall_accuracy}%</div>
                        <div class="stat-label">Точность</div>
                    </div>
                </div>
            </div>
        `);
    },

    // ===== TOPICS LIST =====
    async showTopics() {
        this._showLoading();
        try {
            const r = await fetch('/api/topics');
            const topics = await r.json();
            let cards = '';

            for (const t of topics) {
                const prog = t.progress || {};
                const isLocked = !t.unlocked;
                const isCompleted = prog.completed;
                const totalStars = (prog.stars_ru_en||0) + (prog.stars_en_ru||0) + (prog.stars_fill_blank||0);
                const maxStars = 9;
                const progressPct = this._calcProgress(prog);

                let statusClass = isLocked ? 'locked' : (isCompleted ? 'completed' : '');
                let starsHtml = '';
                if (!isLocked && totalStars > 0) {
                    starsHtml = `<div class="topic-stars">${'⭐'.repeat(Math.min(totalStars, 9))}</div>`;
                }

                cards += `
                <div class="topic-card ${statusClass}" 
                     ${isLocked ? '' : `onclick="window.location.hash='#/topics/${t.id}'"`}>
                    <div class="topic-icon">${isLocked ? '🔒' : t.icon}</div>
                    <div class="topic-info">
                        <h3>${t.title}</h3>
                        <div class="topic-subtitle">${t.title_ru}</div>
                        ${!isLocked ? `<div class="progress-bar"><div class="progress-fill ${isCompleted ? 'complete' : ''}" style="width:${progressPct}%"></div></div>` : ''}
                    </div>
                    <div class="topic-meta">
                        ${starsHtml}
                        <div class="topic-level">Ур. ${t.level}</div>
                    </div>
                </div>`;
            }

            let mistakesHtml = '';
            try {
                const m = await fetch('/api/mistakes');
                const mData = await m.json();
                if (mData.mistakes && mData.mistakes.length > 0) {
                    mistakesHtml = `
                    <div class="mistakes-section" style="margin-bottom: 2rem; padding: 1.5rem; background: var(--bg-card); border-radius: 1rem; border: 1px solid var(--border);">
                        <h2>📉 Ваши частые ошибки</h2>
                        <ul style="list-style:none; padding:0;">
                            ${mData.mistakes.map(err => `<li style="margin-bottom:0.5rem; color:var(--error)">• ${this._escapeHtml(err.prompt)} <span style="color:var(--text-secondary);font-size:0.8rem">(${err.count} раз)</span></li>`).join('')}
                        </ul>
                    </div>`;
                }
            } catch (e) {}

            this._setContent(`
                <div class="topics-header">
                    <h1>📚 Темы</h1>
                    <p>Изучайте темы последовательно — от простого к сложному</p>
                </div>
                
                <div class="mix-banner" style="background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 1rem; padding: 1.5rem; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                    <div>
                        <h2 style="margin: 0 0 0.5rem 0">🧠 Повторить сегодня</h2>
                        <p style="margin: 0; opacity: 0.9">Микс-тренировка по пройденным темам для закрепления</p>
                    </div>
                    <button class="btn-primary" style="background: white; color: var(--primary); border: none" onclick="window.location.hash='#/mix'">Начать микс</button>
                </div>
                
                ${mistakesHtml}
                
                <div class="topics-grid">${cards}</div>
            `);
        } catch (e) {
            this._setContent('<p style="text-align:center;color:var(--error)">Ошибка загрузки тем</p>');
        }
    },

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    },

    _calcProgress(prog) {
        if (!prog || (!prog.theory_completed && prog.practice_stage === 0)) return 0;
        let p = 0;
        if (prog.theory_completed) p += 25;
        p += (prog.practice_stage || 0) * 25;
        return Math.min(p, 100);
    },

    // ===== TOPIC DETAIL (THEORY) =====
    async showTopic(id) {
        this._showLoading();
        try {
            const r = await fetch(`/api/topics/${id}`);
            if (!r.ok) throw new Error();
            const data = await r.json();
            this._setContent(Theory.render(data, data.progress));
        } catch (e) {
            this._setContent('<p style="text-align:center;color:var(--error)">Тема не найдена</p>');
        }
    },

    async completeTheory(topicId) {
        try {
            await fetch(`/api/topics/${topicId}/theory/complete`, {method: 'POST'});
            this.toast('Теория изучена! Переходим к практике 🎯', 'success');
            setTimeout(() => {
                window.location.hash = `#/topics/${topicId}/practice/1`;
            }, 800);
        } catch (e) {
            this.toast('Ошибка сохранения', 'error');
        }
    },

    // ===== PRACTICE =====
    async showPractice(topicId, stage) {
        this._showLoading();
        try {
            const url = stage === 'mix' ? '/api/practice/mix' : `/api/topics/${topicId}/practice/${stage}`;
            const r = await fetch(url);
            if (!r.ok) {
                const err = await r.json();
                this.toast(err.error || 'Ошибка', 'error');
                window.location.hash = '#/topics';
                return;
            }
            const data = await r.json();
            Practice.init(data, topicId, stage);
            this._setContent(Practice.render());
        } catch (e) {
            this._setContent('<p style="text-align:center;color:var(--error)">Ошибка загрузки упражнений</p>');
        }
    },

    // ===== AUTHENTICATION & PROFILE =====
    showLogin() {
        this._setContent(`
            <div class="auth-container" style="max-width: 400px; margin: 2rem auto; padding: 2rem; background: var(--bg-card); border-radius: 1rem; border: 1px solid var(--border);">
                <h2>Вход</h2>
                <input type="text" id="auth-user" placeholder="Логин" class="auth-input" style="width:100%; padding: 0.8rem; margin: 1rem 0; border-radius: 0.5rem; border: 1px solid var(--border); background: var(--bg); color: var(--text);">
                <input type="password" id="auth-pass" placeholder="Пароль" class="auth-input" style="width:100%; padding: 0.8rem; margin-bottom: 1rem; border-radius: 0.5rem; border: 1px solid var(--border); background: var(--bg); color: var(--text);">
                <button class="btn-primary" style="width:100%" onclick="App.doLogin()">Войти</button>
                <div style="text-align:center; margin-top:1rem;">
                    <a href="#/register" style="color:var(--text-secondary)">Нет аккаунта? Зарегистрироваться</a>
                </div>
            </div>
        `);
    },

    showRegister() {
        this._setContent(`
            <div class="auth-container" style="max-width: 400px; margin: 2rem auto; padding: 2rem; background: var(--bg-card); border-radius: 1rem; border: 1px solid var(--border);">
                <h2>Регистрация</h2>
                <input type="text" id="auth-user" placeholder="Логин" class="auth-input" style="width:100%; padding: 0.8rem; margin: 1rem 0; border-radius: 0.5rem; border: 1px solid var(--border); background: var(--bg); color: var(--text);">
                <input type="password" id="auth-pass" placeholder="Пароль" class="auth-input" style="width:100%; padding: 0.8rem; margin-bottom: 1rem; border-radius: 0.5rem; border: 1px solid var(--border); background: var(--bg); color: var(--text);">
                <button class="btn-primary" style="width:100%" onclick="App.doRegister()">Создать профиль</button>
                <div style="text-align:center; margin-top:1rem;">
                    <a href="#/login" style="color:var(--text-secondary)">Уже есть аккаунт? Войти</a>
                </div>
            </div>
        `);
    },

    async doLogin() {
        const u = document.getElementById('auth-user').value;
        const p = document.getElementById('auth-pass').value;
        if (!u || !p) return this.toast('Введите логин и пароль', 'error');

        try {
            const r = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await r.json();
            if (r.ok) {
                this.currentUser = data.user;
                this._updateNavVisibility();
                window.location.hash = '#/topics';
            } else {
                this.toast(data.error || 'Ошибка входа', 'error');
            }
        } catch (e) {
            this.toast('Ошибка сети', 'error');
        }
    },

    async doRegister() {
        const u = document.getElementById('auth-user').value;
        const p = document.getElementById('auth-pass').value;
        if (!u || !p) return this.toast('Введите логин и пароль', 'error');

        try {
            const r = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await r.json();
            if (r.ok) {
                this.currentUser = data.user;
                this._updateNavVisibility();
                window.location.hash = '#/topics';
                this.toast('Аккаунт создан!', 'success');
            } else {
                this.toast(data.error || 'Ошибка регистрации', 'error');
            }
        } catch (e) {
            this.toast('Ошибка сети', 'error');
        }
    },

    async doLogout() {
        await fetch('/api/logout', {method: 'POST'});
        this.currentUser = null;
        this._updateNavVisibility();
        window.location.hash = '#/login';
    },

    async resetProgress() {
        if (!confirm('Вы уверены, что хотите удалить весь свой прогресс? Это действие нельзя отменить!')) return;
        
        try {
            await fetch('/api/reset_all_progress', {method: 'POST'});
            this.toast('Прогресс успешно очищен', 'success');
            setTimeout(() => this.showProfile(), 500);
        } catch (e) {
            this.toast('Ошибка сброса прогресса', 'error');
        }
    },

    // ===== PROFILE (REPLACES STATS) =====
    async showProfile() {
        this._showLoading();
        try {
            const r = await fetch('/api/stats');
            if (!r.ok) {
                if (r.status === 401) {
                    this.currentUser = null;
                    this._updateNavVisibility();
                    window.location.hash = '#/login';
                    return;
                }
                throw new Error();
            }
            const stats = await r.json();

            this._setContent(`
                <div class="stats-page">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                        <h1>👤 Профиль: ${this.currentUser.username}</h1>
                        <button class="btn-secondary" onclick="App.doLogout()">Выйти</button>
                    </div>
                    
                    <h2>📊 Статистика</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-icon">📚</div>
                            <div class="stat-value">${stats.topics_completed}</div>
                            <div class="stat-label">Тем завершено</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">⭐</div>
                            <div class="stat-value">${stats.total_stars}</div>
                            <div class="stat-label">Звёзд из ${stats.max_possible_stars}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">✅</div>
                            <div class="stat-value">${stats.total_exercises_attempted}</div>
                            <div class="stat-label">Упражнений решено</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">🎯</div>
                            <div class="stat-value">${stats.overall_accuracy}%</div>
                            <div class="stat-label">Общая точность</div>
                        </div>
                    </div>
                    
                    <div class="stars-guide" style="margin-top: 2rem; background: var(--bg-card); padding: 1.5rem; border-radius: 1rem; border: 1px solid var(--border);">
                        <h3>🌟 Как получить звезды?</h3>
                        <p style="color: var(--text-secondary); margin-bottom: 1rem;">За каждую тему можно заработать максимум 9 звезд (по 3 звезды за каждый этап практики).</p>
                        <ul style="list-style: none; padding: 0; color: var(--text-secondary);">
                            <li style="margin-bottom: 0.5rem;">⭐ <strong>1 звезда:</strong> от 50% правильных ответов</li>
                            <li style="margin-bottom: 0.5rem;">⭐⭐ <strong>2 звезды:</strong> от 70% правильных ответов</li>
                            <li style="margin-bottom: 0.5rem;">⭐⭐⭐ <strong>3 звезды:</strong> от 90% правильных ответов</li>
                        </ul>
                    </div>
                    
                    <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; gap: 1rem;">
                        <h3 style="color: var(--error)">Опасная зона</h3>
                        <p style="color: var(--text-secondary); max-width: 500px; text-align: center;">Удаление прогресса приведет к безвозвратной потере всей истории прохождения уроков и статистики.</p>
                        <button class="btn-primary" style="background: var(--error); border-color: var(--error)" onclick="App.resetProgress()">
                            🗑️ Сбросить весь прогресс
                        </button>
                    </div>
                </div>
            `);
        } catch (e) {
            this._setContent('<p style="text-align:center;color:var(--error)">Ошибка загрузки профиля</p>');
        }
    }
};

// Start the app
document.addEventListener('DOMContentLoaded', () => App.init());
