/**
 * Simple hash-based router for the SPA.
 */
class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
        window.addEventListener('hashchange', () => this.resolve());
    }

    on(pattern, handler) {
        this.routes[pattern] = handler;
        return this;
    }

    resolve() {
        const hash = window.location.hash.slice(1) || '/';
        
        // Try exact match first
        if (this.routes[hash]) {
            this.currentRoute = hash;
            this.routes[hash]();
            this._updateNav(hash);
            return;
        }

        // Try pattern matching
        for (const pattern of Object.keys(this.routes)) {
            const regex = this._patternToRegex(pattern);
            const match = hash.match(regex);
            if (match) {
                this.currentRoute = hash;
                const params = match.slice(1);
                this.routes[pattern](...params);
                this._updateNav(hash);
                return;
            }
        }

        // 404 — redirect to home
        window.location.hash = '#/';
    }

    _patternToRegex(pattern) {
        const escaped = pattern.replace(/:[^/]+/g, '([^/]+)');
        return new RegExp('^' + escaped + '$');
    }

    _updateNav(hash) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        if (hash === '/' || hash === '') {
            document.getElementById('nav-home')?.classList.add('active');
        } else if (hash.startsWith('/topics') || hash.startsWith('/mix')) {
            document.getElementById('nav-topics')?.classList.add('active');
        } else if (hash.startsWith('/profile') || hash.startsWith('/stats')) {
            document.getElementById('nav-profile')?.classList.add('active');
        } else if (hash.startsWith('/login') || hash.startsWith('/register')) {
            document.getElementById('nav-login')?.classList.add('active');
        }
    }

    navigate(path) {
        window.location.hash = '#' + path;
    }
}
