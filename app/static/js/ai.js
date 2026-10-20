document.addEventListener('DOMContentLoaded', function() {
    const goalInput = document.getElementById('goalInput');
    const generateBtn = document.getElementById('generateBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const aiResponse = document.getElementById('aiResponse');
    const aiUnderstanding = document.getElementById('aiUnderstanding');
    const aiDorksList = document.getElementById('aiDorksList');
    const aiResponsible = document.getElementById('aiResponsible');
    const executeAllContainer = document.getElementById('executeAllContainer');

    // Maximum allowed characters for the goal (must match backend MAX_GOAL_LENGTH)
    const MAX_GOAL_LENGTH = 500;

    // --- Suggested prompt buttons ---
    document.querySelectorAll('.suggested-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            goalInput.value = this.dataset.prompt;
            generateQuery();
        });
    });

    // --- Generate trigger ---
    generateBtn.addEventListener('click', generateQuery);
    goalInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') generateQuery();
    });

    // --- Live character counter (optional UX nicety) ---
    goalInput.addEventListener('input', function() {
        const len = this.value.trim().length;
        if (len > MAX_GOAL_LENGTH) {
            this.style.borderColor = 'var(--accent-red)';
        } else {
            this.style.borderColor = '';
        }
    });

    // ============================================================
    // Main generate function
    // ============================================================
    function generateQuery() {
        const goal = goalInput.value.trim();

        // --- Client-side validation ---
        if (!goal) {
            alert('Please describe what you want to learn.');
            return;
        }

        if (goal.length > MAX_GOAL_LENGTH) {
            alert(`Please keep your goal under ${MAX_GOAL_LENGTH} characters. (Current: ${goal.length})`);
            return;
        }

        // --- Show loading, hide previous response ---
        loadingIndicator.style.display = 'block';
        aiResponse.style.display = 'none';
        executeAllContainer.style.display = 'none';

        // --- Send to backend ---
        fetch('/ai/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal: goal })
        })
        .then(response => {
            // Handle non-JSON error responses (e.g. 500 HTML page)
            const contentType = response.headers.get('content-type') || '';
            if (!contentType.includes('application/json')) {
                return response.text().then(text => {
                    throw new Error(`Server returned ${response.status}: ${text.substring(0, 200)}`);
                });
            }
            return response.json();
        })
        .then(data => {
            loadingIndicator.style.display = 'none';

            if (data.error) {
                aiResponse.style.display = 'block';
                aiDorksList.innerHTML = `<div class="ai-error">❌ ${data.error}</div>`;
                aiUnderstanding.textContent = 'Error occurred. Please check your configuration.';
                aiResponsible.textContent = '';
                return;
            }

            displayResponse(data);
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            aiResponse.style.display = 'block';
            aiDorksList.innerHTML = `<div class="ai-error">❌ Network error: ${error.message}</div>`;
            aiUnderstanding.textContent = 'Error occurred. Please try again.';
            aiResponsible.textContent = '';
        });
    }

    // ============================================================
    // Render the AI response
    // ============================================================
    function displayResponse(data) {
        // Understanding
        aiUnderstanding.textContent = data.understanding || 'No explanation provided.';

        // Dorks list
        aiDorksList.innerHTML = '';

        if (data.dorks && data.dorks.length > 0) {
            data.dorks.forEach((dork, index) => {
                const card = document.createElement('div');
                card.className = 'ai-dork-card';

                // Escape user-visible strings to prevent HTML injection
                const name = escapeHtml(dork.name || 'Unnamed Dork');
                const query = escapeHtml(dork.query || '');
                const explanation = escapeHtml(dork.explanation || 'No explanation provided.');
                const security = escapeHtml(dork.security_context || 'Security context not provided.');

                card.innerHTML = `
                    <div class="ai-dork-header">
                        <span class="ai-dork-number">#${index + 1}</span>
                        <span class="ai-dork-name">${name}</span>
                    </div>
                    <div class="ai-dork-query">${query}</div>
                    <div class="ai-dork-explanation">${explanation}</div>
                    <div class="ai-dork-security">🛡️ ${security}</div>
                    <div class="ai-dork-actions">
                        <button class="btn btn-sm btn-secondary ai-copy-dork" data-query="${query}">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                        <button class="btn btn-sm btn-primary ai-open-dork" data-query="${query}">
                            <i class="fas fa-external-link-alt"></i> Open
                        </button>
                        <button class="btn btn-sm btn-success ai-save-dork" data-query="${query}">
                            <i class="fas fa-save"></i> Save
                        </button>
                    </div>
                `;
                aiDorksList.appendChild(card);
            });

            // Attach per-dork action handlers
            attachDorkActions();

            // Show "Execute All" button
            executeAllContainer.style.display = 'block';
        } else {
            aiDorksList.innerHTML = '<p class="ai-empty">No dorks generated. Please try a different goal.</p>';
        }

        // Responsible use
        aiResponsible.textContent = data.responsible_use || 'Only search authorized targets.';

        // Show response
        aiResponse.style.display = 'block';
    }

    // ============================================================
    // Attach click handlers to copy / open / save buttons
    // ============================================================
    function attachDorkActions() {
        document.querySelectorAll('.ai-copy-dork').forEach(btn => {
            btn.addEventListener('click', function() {
                const q = this.dataset.query;
                if (!q) return;

                navigator.clipboard.writeText(q)
                    .then(() => showFeedback(this, '<i class="fas fa-check"></i> Copied!'))
                    .catch(() => {
                        // Fallback for older browsers / non-HTTPS contexts
                        const ta = document.createElement('textarea');
                        ta.value = q;
                        document.body.appendChild(ta);
                        ta.select();
                        document.execCommand('copy');
                        document.body.removeChild(ta);
                        showFeedback(this, '<i class="fas fa-check"></i> Copied!');
                    });
            });
        });

        document.querySelectorAll('.ai-open-dork').forEach(btn => {
            btn.addEventListener('click', function() {
                const q = this.dataset.query;
                if (!q) return;
                window.open(`https://www.google.com/search?q=${encodeURIComponent(q)}`, '_blank');
                saveToHistory(q);
            });
        });

        document.querySelectorAll('.ai-save-dork').forEach(btn => {
            btn.addEventListener('click', function() {
                const q = this.dataset.query;
                if (!q) return;

                const saved = JSON.parse(localStorage.getItem('dorkforge_saved') || '[]');
                saved.push({ query: q, timestamp: new Date().toISOString() });
                localStorage.setItem('dorkforge_saved', JSON.stringify(saved));

                showFeedback(this, '<i class="fas fa-check"></i> Saved!');
            });
        });
    }

    // ============================================================
    // Helpers
    // ============================================================
    function showFeedback(btn, html) {
        const original = btn.innerHTML;
        btn.innerHTML = html;
        btn.disabled = true;
        setTimeout(() => {
            btn.innerHTML = original;
            btn.disabled = false;
        }, 1500);
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function saveToHistory(query) {
        const history = JSON.parse(localStorage.getItem('dorkforge_history') || '[]');
        history.unshift({ query: query, timestamp: new Date().toISOString() });
        if (history.length > 50) history.pop();
        localStorage.setItem('dorkforge_history', JSON.stringify(history));
    }

    // ============================================================
    // Global function for the "Execute All" button
    // ============================================================
    window.executeAllDorks = function() {
        const queries = [];
        document.querySelectorAll('.ai-dork-query').forEach(el => {
            const q = el.textContent.trim();
            if (q) queries.push(q);
        });

        if (queries.length === 0) {
            alert('No queries to execute.');
            return;
        }

        // Confirm before opening many tabs
        if (queries.length > 5) {
            if (!confirm(`This will open ${queries.length} new tabs. Continue?`)) {
                return;
            }
        }

        queries.forEach((q, i) => {
            setTimeout(() => {
                window.open(`https://www.google.com/search?q=${encodeURIComponent(q)}`, '_blank');
                saveToHistory(q);
            }, i * 500);
        });
    };
});