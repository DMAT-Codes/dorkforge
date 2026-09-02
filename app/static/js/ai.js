document.addEventListener('DOMContentLoaded', function() {
    const goalInput = document.getElementById('goalInput');
    const generateBtn = document.getElementById('generateBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const aiResponse = document.getElementById('aiResponse');
    const aiUnderstanding = document.getElementById('aiUnderstanding');
    const aiDorksList = document.getElementById('aiDorksList');
    const aiResponsible = document.getElementById('aiResponsible');
    const executeAllContainer = document.getElementById('executeAllContainer');

    document.querySelectorAll('.suggested-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            goalInput.value = this.dataset.prompt;
            generateQuery();
        });
    });

    generateBtn.addEventListener('click', generateQuery);
    goalInput.addEventListener('keypress', function(e) { if (e.key === 'Enter') generateQuery(); });

    function generateQuery() {
        const goal = goalInput.value.trim();
        if (!goal) { alert('Please describe what you want to learn.'); return; }

        loadingIndicator.style.display = 'block';
        aiResponse.style.display = 'none';
        executeAllContainer.style.display = 'none';

        fetch('/ai/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal: goal })
        })
        .then(response => response.json())
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
        });
    }

    function displayResponse(data) {
        aiUnderstanding.textContent = data.understanding || 'No explanation provided.';

        aiDorksList.innerHTML = '';
        if (data.dorks && data.dorks.length > 0) {
            data.dorks.forEach((dork, index) => {
                const card = document.createElement('div');
                card.className = 'ai-dork-card';
                card.innerHTML = `
                    <div class="ai-dork-header">
                        <span class="ai-dork-number">#${index + 1}</span>
                        <span class="ai-dork-name">${dork.name || 'Unnamed Dork'}</span>
                    </div>
                    <div class="ai-dork-query">${dork.query || ''}</div>
                    <div class="ai-dork-explanation">${dork.explanation || 'No explanation provided.'}</div>
                    <div class="ai-dork-security">🛡️ ${dork.security_context || 'Security context not provided.'}</div>
                    <div class="ai-dork-actions">
                        <button class="btn btn-sm btn-secondary ai-copy-dork" data-query="${dork.query || ''}"><i class="fas fa-copy"></i> Copy</button>
                        <button class="btn btn-sm btn-primary ai-open-dork" data-query="${dork.query || ''}"><i class="fas fa-external-link-alt"></i> Open</button>
                        <button class="btn btn-sm btn-success ai-save-dork" data-query="${dork.query || ''}"><i class="fas fa-save"></i> Save</button>
                    </div>
                `;
                aiDorksList.appendChild(card);
            });

            document.querySelectorAll('.ai-copy-dork').forEach(btn => {
                btn.addEventListener('click', function() {
                    const q = this.dataset.query;
                    if (q) { navigator.clipboard.writeText(q); const orig = this.innerHTML; this.innerHTML = '<i class="fas fa-check"></i> Copied!'; setTimeout(() => { this.innerHTML = orig; }, 1500); }
                });
            });

            document.querySelectorAll('.ai-open-dork').forEach(btn => {
                btn.addEventListener('click', function() {
                    const q = this.dataset.query;
                    if (q) { window.open(`https://www.google.com/search?q=${encodeURIComponent(q)}`, '_blank'); saveToHistory(q); }
                });
            });

            document.querySelectorAll('.ai-save-dork').forEach(btn => {
                btn.addEventListener('click', function() {
                    const q = this.dataset.query;
                    if (q) {
                        const saved = JSON.parse(localStorage.getItem('dorkforge_saved') || '[]');
                        saved.push({ query: q, timestamp: new Date().toISOString() });
                        localStorage.setItem('dorkforge_saved', JSON.stringify(saved));
                        const orig = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-check"></i> Saved!';
                        setTimeout(() => { this.innerHTML = orig; }, 1500);
                    }
                });
            });

            executeAllContainer.style.display = 'block';
        } else {
            aiDorksList.innerHTML = '<p class="ai-empty">No dorks generated. Please try a different goal.</p>';
        }

        aiResponsible.textContent = data.responsible_use || 'Only search authorized targets.';
        aiResponse.style.display = 'block';
    }

    function saveToHistory(query) {
        const history = JSON.parse(localStorage.getItem('dorkforge_history') || '[]');
        history.unshift({ query: query, timestamp: new Date().toISOString() });
        if (history.length > 50) history.pop();
        localStorage.setItem('dorkforge_history', JSON.stringify(history));
    }

    window.executeAllDorks = function() {
        const queries = [];
        document.querySelectorAll('.ai-dork-query').forEach(el => {
            const q = el.textContent.trim();
            if (q) queries.push(q);
        });
        if (queries.length === 0) { alert('No queries to execute.'); return; }
        queries.forEach((q, i) => {
            setTimeout(() => {
                window.open(`https://www.google.com/search?q=${encodeURIComponent(q)}`, '_blank');
                saveToHistory(q);
            }, i * 500);
        });
    };
});