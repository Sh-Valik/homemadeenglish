/**
 * Practice exercises module — handles all 3 practice stages.
 */
const Practice = {
    exercises: [],
    currentIndex: 0,
    correctCount: 0,
    totalCount: 0,
    topicId: '',
    stage: 0,
    stageName: '',
    selectedWords: [],
    answered: false,
    isMix: false,

    init(data, topicId, stage) {
        this.exercises = data.exercises;
        this.currentIndex = 0;
        this.correctCount = 0;
        this.totalCount = data.total;
        this.topicId = topicId;
        this.stage = stage;
        this.stageName = data.stage_name || 'Микс';
        this.selectedWords = [];
        this.answered = false;
        this.isMix = stage === 'mix';
    },

    playAudio(text) {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'en-US';
        msg.rate = 0.9;
        window.speechSynthesis.speak(msg);
    },

    render() {
        if (this.currentIndex >= this.exercises.length) return this._renderResults();
        
        const ex = this.exercises[this.currentIndex];
        const currentStage = this.isMix ? ex.stage : this.stage;
        
        let html = `<div class="practice-container">`;
        html += this._renderHeader();
        html += `<div class="practice-card">`;

        const stageLabels = {1: 'Переведите на английский', 2: 'Переведите на русский', 3: 'Вставьте пропущенное слово'};
        html += `<div class="practice-stage-label">${stageLabels[currentStage] || 'Микс'}</div>`;

        if (currentStage === 1) html += this._renderRuToEn(ex);
        else if (currentStage === 2) html += this._renderEnToRu(ex);
        else if (currentStage === 3) html += this._renderFillBlank(ex);

        html += `<div id="feedback-area"></div>`;
        html += `</div></div>`;
        return html;
    },

    _renderHeader() {
        const pct = this.totalCount > 0 ? (this.currentIndex / this.totalCount) * 100 : 0;
        return `<div class="practice-header">
            <div class="practice-progress" style="width: 100%;">
                <span class="practice-counter">${this.currentIndex + 1} / ${this.totalCount}</span>
                <div class="practice-bar"><div class="practice-bar-fill" style="width:${pct}%"></div></div>
            </div>
        </div>`;
    },

    _renderRuToEn(ex) {
        let html = `<div class="practice-prompt">${this._esc(ex.prompt)}</div>`;
        html += `<div class="answer-area" id="answer-area" onclick="Practice._removeLastWord()">`;
        html += `<span style="color:var(--text-muted);font-size:0.85rem" id="answer-placeholder">Нажмите на слова ниже</span>`;
        html += `</div>`;
        html += `<div class="word-bank" id="word-bank">`;
        for (let i = 0; i < ex.words.length; i++) {
            html += `<div class="word-chip" data-index="${i}" onclick="Practice.selectWord(${i})">${this._esc(ex.words[i])}</div>`;
        }
        html += `</div>`;
        html += `<button class="btn-check" id="btn-check" onclick="Practice.checkAnswer()" disabled>Проверить</button>`;
        return html;
    },

    _renderEnToRu(ex) {
        let html = `<div class="practice-prompt en">
            ${this._esc(ex.prompt)}
            <button class="btn-tts" onclick="Practice.playAudio('${this._esc(ex.prompt).replace(/'/g, "\\'")}')">🔊</button>
        </div>`;
        html += `<div class="options-grid" id="options-grid">`;
        for (let i = 0; i < ex.options.length; i++) {
            html += `<button class="option-btn" data-index="${i}" onclick="Practice.selectOption(${i})">${this._esc(ex.options[i])}</button>`;
        }
        html += `</div>`;
        return html;
    },

    _renderFillBlank(ex) {
        const parts = ex.sentence.split('___');
        let sentence = '';
        for (let i = 0; i < parts.length; i++) {
            sentence += this._esc(parts[i]);
            if (i < parts.length - 1) sentence += `<span class="blank-slot" id="blank-slot">...</span>`;
        }
        let html = `<div class="fill-sentence">${sentence}</div>`;
        html += `<div class="options-grid" id="options-grid">`;
        for (let i = 0; i < ex.options.length; i++) {
            html += `<button class="option-btn" data-index="${i}" onclick="Practice.selectOption(${i})">${this._esc(ex.options[i])}</button>`;
        }
        html += `</div>`;
        return html;
    },

    // Word bank interactions (Stage 1)
    selectWord(index) {
        if (this.answered) return;
        const ex = this.exercises[this.currentIndex];
        const chip = document.querySelector(`.word-chip[data-index="${index}"]`);
        if (!chip || chip.classList.contains('selected')) return;
        
        chip.classList.add('selected');
        this.selectedWords.push({index, word: ex.words[index]});
        this._updateAnswerArea();
    },

    _removeLastWord() {
        if (this.answered || this.selectedWords.length === 0) return;
        const last = this.selectedWords.pop();
        const chip = document.querySelector(`.word-chip[data-index="${last.index}"]`);
        if (chip) chip.classList.remove('selected');
        this._updateAnswerArea();
    },

    removeWord(wordIndex) {
        if (this.answered) return;
        const idx = this.selectedWords.findIndex(w => w.index === wordIndex);
        if (idx === -1) return;
        this.selectedWords.splice(idx, 1);
        const chip = document.querySelector(`.word-chip[data-index="${wordIndex}"]`);
        if (chip) chip.classList.remove('selected');
        this._updateAnswerArea();
    },

    _updateAnswerArea() {
        const area = document.getElementById('answer-area');
        const placeholder = document.getElementById('answer-placeholder');
        const btn = document.getElementById('btn-check');
        
        if (this.selectedWords.length === 0) {
            area.innerHTML = `<span style="color:var(--text-muted);font-size:0.85rem" id="answer-placeholder">Нажмите на слова ниже</span>`;
            area.classList.remove('has-words');
            btn.disabled = true;
        } else {
            area.innerHTML = this.selectedWords.map(w => 
                `<span class="answer-word" onclick="Practice.removeWord(${w.index})">${this._esc(w.word)}</span>`
            ).join('');
            area.classList.add('has-words');
            btn.disabled = false;
        }
    },

    // Option selection (Stage 2 & 3)
    selectOption(index) {
        if (this.answered) return;
        this.answered = true;
        
        const ex = this.exercises[this.currentIndex];
        const selectedText = ex.options[index];
        const currentStage = this.isMix ? ex.stage : this.stage;
        const currentTopic = this.isMix ? ex.topic_id : this.topicId;
        const prompt = currentStage === 3 ? ex.sentence : ex.prompt;

        document.querySelectorAll('.option-btn').forEach(b => b.classList.add('disabled'));

        fetch(`/api/topics/${currentTopic}/practice/${currentStage}/check`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({answer: selectedText, prompt: prompt})
        })
        .then(r => r.json())
        .then(result => {
            const btns = document.querySelectorAll('.option-btn');
            btns[index].classList.add(result.correct ? 'correct' : 'wrong');
            
            // Highlight correct answer if wrong
            if (!result.correct) {
                btns.forEach(b => {
                    if (b.textContent === result.correct_answer) b.classList.add('correct');
                });
            } else {
                this.correctCount++;
                if (currentStage === 3) {
                    this.playAudio(result.correct_answer);
                }
            }

            if (currentStage === 3) {
                const slot = document.getElementById('blank-slot');
                if (slot) {
                    slot.textContent = result.correct_answer;
                    slot.style.color = result.correct ? 'var(--success)' : 'var(--error)';
                }
            }

            this._showFeedback(result);
        });
    },

    // Check answer for Stage 1 (word bank)
    checkAnswer() {
        if (this.answered || this.selectedWords.length === 0) return;
        this.answered = true;

        const ex = this.exercises[this.currentIndex];
        const currentStage = this.isMix ? ex.stage : this.stage;
        const currentTopic = this.isMix ? ex.topic_id : this.topicId;
        
        const userAnswer = this.selectedWords.map(w => w.word).join(' ');
        const btn = document.getElementById('btn-check');
        btn.disabled = true;

        fetch(`/api/topics/${currentTopic}/practice/${currentStage}/check`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({answer: userAnswer, prompt: ex.prompt})
        })
        .then(r => r.json())
        .then(result => {
            if (result.correct) {
                this.correctCount++;
            }
            if (result.correct_answer) {
                this.playAudio(result.correct_answer);
            }

            // Disable word interactions
            document.querySelectorAll('.word-chip').forEach(c => c.style.pointerEvents = 'none');
            
            this._showFeedback(result);
        });
    },

    _showFeedback(result) {
        const area = document.getElementById('feedback-area');
        let html = `<div class="feedback ${result.correct ? 'correct' : 'wrong'}">`;
        html += result.correct ? '✅ Правильно!' : '❌ Неправильно';
        if (!result.correct && result.correct_answer) {
            html += `<div class="correct-answer">Правильный ответ: <strong>${this._esc(result.correct_answer)}</strong></div>`;
        }
        if (result.explanation) {
            html += `<div class="explanation">💡 ${this._esc(result.explanation)}</div>`;
        }
        html += `</div>`;
        html += `<button class="btn-check btn-next" onclick="Practice.next()">Далее →</button>`;
        area.innerHTML = html;
    },

    next() {
        this.currentIndex++;
        this.selectedWords = [];
        this.answered = false;
        const app = document.getElementById('app');
        if (this.currentIndex >= this.exercises.length) {
            if (this.isMix) {
                app.innerHTML = this._renderResults();
                return;
            }
            // Complete stage on server
            fetch(`/api/topics/${this.topicId}/practice/${this.stage}/complete`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({correct: this.correctCount, total: this.totalCount})
            })
            .then(r => r.json())
            .then(data => {
                this._starsEarned = data.stars;
                app.innerHTML = this._renderResults();
            });
        } else {
            app.innerHTML = this.render();
        }
    },

    _renderResults() {
        const pct = this.totalCount > 0 ? Math.round((this.correctCount / this.totalCount) * 100) : 0;
        const stars = this._starsEarned || (pct >= 90 ? 3 : pct >= 70 ? 2 : pct >= 50 ? 1 : 0);
        const starStr = '⭐'.repeat(stars) + '☆'.repeat(3 - stars);
        const emoji = stars === 3 ? '🎉' : stars >= 2 ? '👏' : stars >= 1 ? '👍' : '💪';
        const msg = stars === 3 ? 'Отлично!' : stars >= 2 ? 'Хорошо!' : stars >= 1 ? 'Неплохо!' : 'Попробуйте ещё раз';

        const nextStage = (!this.isMix && this.stage < 3) ? this.stage + 1 : null;

        let html = `<div class="results-screen">
            <div class="results-emoji">${emoji}</div>
            <h2>${msg}</h2>
            <div style="color:var(--text-secondary);margin-bottom:0.5rem">${this.isMix ? 'Тренировка' : stageLabels[this.stage]} завершена</div>
            ${!this.isMix ? `<div class="results-stars">${starStr}</div>` : ''}
            <div class="results-stats">
                <div class="result-stat"><div class="stat-value">${this.correctCount}/${this.totalCount}</div><div class="stat-label">Правильных</div></div>
                <div class="result-stat"><div class="stat-value">${pct}%</div><div class="stat-label">Точность</div></div>
            </div>
            <div class="results-actions">`;

        if (nextStage) {
            html += `<button class="btn-primary" onclick="window.location.hash='#/topics/${this.topicId}/practice/${nextStage}'">
                Следующий этап →</button>`;
        } else {
            html += `<button class="btn-primary" onclick="window.location.hash='#/topics'">
                🎓 Завершить</button>`;
        }
        
        if (this.isMix) {
            html += `<button class="btn-secondary" onclick="window.location.hash='#/mix'">
                🔄 Повторить микс</button>`;
        } else {
            html += `<button class="btn-secondary" onclick="window.location.hash='#/topics/${this.topicId}/practice/${this.stage}'">
                🔄 Повторить</button>`;
            html += `<button class="btn-secondary" onclick="window.location.hash='#/topics/${this.topicId}'">
                📖 К теории</button>`;
        }
        html += `</div></div>`;
        return html;
    },

    _esc(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
