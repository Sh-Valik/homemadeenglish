/**
 * Theory page rendering module.
 */
const Theory = {
    render(topicData, progress) {
        const topic = topicData.topic;
        const sections = topic.theory.sections;
        const theoryDone = progress && progress.theory_completed;

        let html = `
        <div class="topic-detail">
            <div class="topic-detail-header">
                <button class="back-btn" onclick="window.location.hash='#/topics'">← Назад</button>
                <span class="topic-icon" style="font-size:1.5rem">${topic.icon}</span>
                <div>
                    <div class="topic-detail-title">${topic.title}</div>
                    <div style="color:var(--text-secondary);font-size:0.9rem">${topic.title_ru}</div>
                </div>
            </div>
            <div class="theory-container">`;

        for (const section of sections) {
            html += `<div class="theory-section"><h2>${section.title}</h2>`;
            
            if (section.content) {
                html += `<div class="theory-content">${this._escapeHtml(section.content)}</div>`;
            }
            if (section.formula) {
                html += `<div class="theory-formula">${this._escapeHtml(section.formula)}</div>`;
            }
            if (section.examples && section.examples.length > 0) {
                html += `<div class="examples-list">`;
                for (const ex of section.examples) {
                    html += `<div class="example-item">
                        <span class="example-en">
                            ${this._escapeHtml(ex.en)}
                            <button class="btn-tts" onclick="Theory.playAudio('${this._escapeHtml(ex.en).replace(/'/g, "\\'")}')">🔊</button>
                        </span>
                        <span class="example-divider">—</span>
                        <span class="example-ru">${this._escapeHtml(ex.ru)}</span>
                    </div>`;
                }
                html += `</div>`;
            }
            if (section.tip) {
                html += `<div class="theory-tip">${this._escapeHtml(section.tip)}</div>`;
            }
            html += `</div>`;
        }

        html += `</div><div class="theory-actions">`;
        
        if (!theoryDone) {
            html += `<button class="btn-primary" onclick="App.completeTheory('${topic.id}')">
                ✅ Теорию изучил — к практике!</button>`;
        } else {
            html += `<button class="btn-primary" onclick="window.location.hash='#/topics/${topic.id}/practice/1'">
                🎯 Перейти к практике</button>`;
        }
        
        html += `<button class="btn-secondary" onclick="window.location.hash='#/topics'">← К списку тем</button>`;
        html += `</div></div>`;

        return html;
    },

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    },

    playAudio(text) {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'en-US';
        msg.rate = 0.9;
        window.speechSynthesis.speak(msg);
    }
};
