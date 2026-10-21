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

    // --- Live character counter ---
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
            const contentType = response.headers.get('content-type') || '';
            if (!contentType.includes('application/json')) {
                return response.text().then(text => {
                    throw new Error(`Server returned ${response.status}: ${text.substring(0, 100)}`);
                });
            }
            return response.json();
        })
        .then(data => {
            loadingIndicator.style.display = 'none';

            if (data.error) {
                aiResponse.style.display = 'block';
                aiUnderstanding.textContent = 'Could not generate dorks at this time.';
                aiResponsible.textContent = '';
                
                // Clean, friendly warning UI
                aiDorksList.innerHTML = `
                    <div class="ai-error" style="background: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; color: #f59e0b; padding: 1.5rem; border-radius: 8px; text-align: center; font-weight: 500; margin-top: 1rem;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
                        ${data.error}
                    </div>
                `;
                return;
            }

            displayResponse(data);
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            aiResponse.style.display = 'block';
            aiUnderstanding.textContent = 'Network Error';
            
            aiDorksList.innerHTML = `
                <div class="ai-error" style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; padding: 1.5rem; border-radius: 8px; text-align: center; font-weight: 500; margin-top: 1rem;">
                    <i class="fas fa-wifi" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
                    Failed to connect to the server. Please check your internet connection and try again.
                </div>
            `;
        });
    }

    // ============================================================
    // Render the AI response
    // ============================================================
    function displayResponse(data) {
        aiUnderstanding.textContent = data.understanding || 'No explanation provided.';
        aiDorksList.innerHTML = '';

        if (data.dorks && data.dorks.length > 0) {
            data.dorks.forEach((dork, index) => {
                const card = document.createElement('div');
                card.className = 'ai-dork-card';

                // Escape user-visible strings to prevent HTML injection (XSS)
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

            attachDorkActions();
            executeAllContainer.style.display = 'block';
        } else {
            aiDorksList.innerHTML = '<p class="ai-empty">No dorks generated. Please try a different goal.</p>';
        }

        aiResponsible.textContent = data.responsible_use || 'Only search authorized targets.';
        aiResponse.style.display = 'block';
    }

    // ============================================================
    // Attach click handlers to copy / open / save buttons
    // ============================================================
    function attachDorkActions() {
        // COPY
        document.querySelectorAll('.ai-copy-dork').forEach(btn => {
            btn.addEventListener('click', function() {
                const q = this.dataset.query;
                if (!q) return;

                navigator.clipboard.writeText(q)
                    .then(() => showFeedback(this, '<i class="fas fa-check"></i> Copied!'))
                    .catch(() => {
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

        // OPEN
        document.querySelectorAll('.ai-open-dork').forEach(btn => {
            btn.addEventListener('click', function() {
                const q = this.dataset.query;
                if (!q) return;
                window.open(`https://www.google.com/search?q=${encodeURIComponent(q)}`, '_blank');
                saveToHistory(q);
            });
        });

        // SAVE (UPDATED TO USE DATABASE API)
        document.querySelectorAll('.ai-save-dork').forEach(btn => {
            btn.addEventListener('click', function() {
                const q = this.dataset.query;
                if (!q) return;

                fetch('/history/api/saved', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: q, title: 'Saved from AI Assistant' })
                }).then(response => {
                    if (response.ok) {
                        showFeedback(this, '<i class="fas fa-check"></i> Saved to DB!');
                    } else {
                        alert('Please log in to save queries to your account.');
                    }
                }).catch(() => {
                    alert('Error connecting to the database.');
                });
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