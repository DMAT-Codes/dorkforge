document.addEventListener('DOMContentLoaded', function() {
    const domain = document.getElementById('domain');
    const filetype = document.getElementById('filetype');
    const intitle = document.getElementById('intitle');
    const inurl = document.getElementById('inurl');
    const intext = document.getElementById('intext');
    const exact = document.getElementById('exact');
    const exclude = document.getElementById('exclude');
    const exclude_site = document.getElementById('exclude_site');
    const before_date = document.getElementById('before_date');
    const after_date = document.getElementById('after_date');
    const or_terms = document.getElementById('or_terms');
    const custom = document.getElementById('custom');
    const templateSelect = document.getElementById('templateSelect');
    
    const queryDisplay = document.getElementById('queryDisplay');
    const queryInterpretation = document.getElementById('queryInterpretation');
    const copyBtn = document.getElementById('copyQueryBtn');
    const openGoogleBtn = document.getElementById('openGoogleBtn');
    const saveBtn = document.getElementById('saveQueryBtn');
    const resetBtn = document.getElementById('resetBtn');
    const historyList = document.getElementById('historyList');
    const savedList = document.getElementById('savedList');

    const templates = {
        research: { domain: '', filetype: 'pdf', intitle: 'research paper', inurl: '', intext: '', exact: '', exclude: '', exclude_site: '', before: '', after: '', or: '', custom: '' },
        documents: { domain: '', filetype: 'pdf', intitle: 'report', inurl: '', intext: '', exact: '', exclude: '', exclude_site: '', before: '', after: '', or: '', custom: '' },
        technical: { domain: '', filetype: 'pdf', intitle: 'technical', inurl: '', intext: 'documentation', exact: '', exclude: '', exclude_site: '', before: '', after: '', or: '', custom: '' },
        news: { domain: '', filetype: '', intitle: 'news', inurl: '', intext: '', exact: '', exclude: '', exclude_site: '', before: '', after: '', or: '', custom: '' },
        code: { domain: 'github.com', filetype: '', intitle: '', inurl: '', intext: '', exact: '', exclude: '', exclude_site: '', before: '', after: '', or: '', custom: '' },
        academic: { domain: 'edu', filetype: 'pdf', intitle: '', inurl: '', intext: 'university', exact: '', exclude: '', exclude_site: '', before: '', after: '', or: '', custom: '' },
        organization: { domain: '', filetype: '', intitle: 'about', inurl: '', intext: '', exact: '', exclude: '', exclude_site: '', before: '', after: '', or: '', custom: '' }
    };

    function buildQuery() {
        const parts = [];
        const breakdown = [];

        if (domain.value.trim()) { parts.push(`site:${domain.value.trim()}`); breakdown.push(`Domain: ${domain.value.trim()}`); }
        if (filetype.value) { parts.push(`filetype:${filetype.value}`); breakdown.push(`File type: ${filetype.value}`); }
        if (intitle.value.trim()) { const v = intitle.value.trim(); parts.push(v.includes(' ') ? `intitle:"${v}"` : `intitle:${v}`); breakdown.push(`Title: ${v}`); }
        if (inurl.value.trim()) { const v = inurl.value.trim(); parts.push(v.includes(' ') ? `inurl:"${v}"` : `inurl:${v}`); breakdown.push(`URL: ${v}`); }
        if (intext.value.trim()) { const v = intext.value.trim(); parts.push(v.includes(' ') ? `intext:"${v}"` : `intext:${v}`); breakdown.push(`Text: ${v}`); }
        if (exact.value.trim()) { let v = exact.value.trim(); if (!v.startsWith('"')) v = `"${v}`; if (!v.endsWith('"')) v = `${v}"`; parts.push(v); breakdown.push(`Exact: ${v}`); }
        if (exclude.value.trim()) { exclude.value.trim().split(/\s+/).forEach(w => { if (w) { parts.push(`-${w}`); breakdown.push(`Exclude: ${w}`); } }); }
        if (exclude_site.value.trim()) { parts.push(`-site:${exclude_site.value.trim()}`); breakdown.push(`Exclude domain: ${exclude_site.value.trim()}`); }
        if (before_date.value) { parts.push(`before:${before_date.value}`); breakdown.push(`Before: ${before_date.value}`); }
        if (after_date.value) { parts.push(`after:${after_date.value}`); breakdown.push(`After: ${after_date.value}`); }
        if (or_terms.value.trim()) { const terms = or_terms.value.split(',').map(t => t.trim()).filter(t => t); if (terms.length) { parts.push(`(${terms.join(' OR ')})`); breakdown.push(`OR: ${terms.join(' OR ')}`); } }
        if (custom.value.trim()) { parts.push(custom.value.trim()); breakdown.push(`Custom: ${custom.value.trim()}`); }

        const query = parts.join(' ');
        if (query && query.trim()) {
            queryDisplay.textContent = query;
            queryDisplay.className = 'query-display query-active';
            if (breakdown.length) {
                queryInterpretation.innerHTML = `🔍 <strong>Searching:</strong> ${breakdown.join(' • ')}`;
                queryInterpretation.className = 'query-interpretation visible';
            }
        } else {
            queryDisplay.innerHTML = '<span class="query-placeholder">Fill in the fields above to build your query...</span>';
            queryDisplay.className = 'query-display';
            queryInterpretation.className = 'query-interpretation';
        }
        return query;
    }

    function loadTemplate(key) {
        if (!key || !templates[key]) return;
        const t = templates[key];
        domain.value = t.domain || '';
        filetype.value = t.filetype || '';
        intitle.value = t.intitle || '';
        inurl.value = t.inurl || '';
        intext.value = t.intext || '';
        exact.value = t.exact || '';
        exclude.value = t.exclude || '';
        exclude_site.value = t.exclude_site || '';
        before_date.value = t.before || '';
        after_date.value = t.after || '';
        or_terms.value = t.or || '';
        custom.value = t.custom || '';
        buildQuery();
    }

    function copyQuery() {
        const q = queryDisplay.textContent;
        if (q && q !== 'Fill in the fields above to build your query...') {
            navigator.clipboard.writeText(q);
            const orig = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => { copyBtn.innerHTML = orig; }, 1500);
        }
    }

    function openInGoogle() {
        const q = queryDisplay.textContent;
        if (q && q !== 'Fill in the fields above to build your query...') {
            window.open(`https://www.google.com/search?q=${encodeURIComponent(q)}`, '_blank');
            addToHistory(q);
        }
    }

    function saveQuery() {
        const q = queryDisplay.textContent;
        if (!q || q === 'Fill in the fields above to build your query...') { alert('No query to save!'); return; }
        const saved = JSON.parse(localStorage.getItem('dorkforge_saved') || '[]');
        saved.push({ query: q, timestamp: new Date().toISOString() });
        localStorage.setItem('dorkforge_saved', JSON.stringify(saved));
        renderSaved();
        const orig = saveBtn.innerHTML;
        saveBtn.innerHTML = '<i class="fas fa-check"></i> Saved!';
        setTimeout(() => { saveBtn.innerHTML = orig; }, 1500);
    }

    function resetForm() {
        domain.value = ''; filetype.value = ''; intitle.value = ''; inurl.value = ''; intext.value = '';
        exact.value = ''; exclude.value = ''; exclude_site.value = ''; before_date.value = ''; after_date.value = '';
        or_terms.value = ''; custom.value = '';
        buildQuery();
    }

    function addToHistory(query) {
        if (!query || query === 'Fill in the fields above to build your query...') return;
        const history = JSON.parse(localStorage.getItem('dorkforge_history') || '[]');
        history.unshift({ query: query, timestamp: new Date().toISOString() });
        if (history.length > 20) history.pop();
        localStorage.setItem('dorkforge_history', JSON.stringify(history));
        renderHistory();
    }

    function renderHistory() {
        const history = JSON.parse(localStorage.getItem('dorkforge_history') || '[]');
        if (history.length === 0) { historyList.innerHTML = '<span class="simple-empty">No history yet</span>'; return; }
        historyList.innerHTML = history.map((item, i) => `
            <div class="simple-item">
                <span class="simple-item-query" onclick="window.loadBuilderHistory(${i})" title="${item.query}">${item.query.substring(0, 50)}${item.query.length > 50 ? '...' : ''}</span>
                <span class="simple-item-time">${new Date(item.timestamp).toLocaleDateString()}</span>
                <div class="simple-item-actions">
                    <button class="btn btn-sm btn-danger" onclick="window.deleteBuilderHistory(${i})"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `).join('');
    }

    function renderSaved() {
        const saved = JSON.parse(localStorage.getItem('dorkforge_saved') || '[]');
        if (saved.length === 0) { savedList.innerHTML = '<span class="simple-empty">No saved queries yet</span>'; return; }
        savedList.innerHTML = saved.map((item, i) => `
            <div class="simple-item">
                <span class="simple-item-query" onclick="window.loadBuilderSaved(${i})" title="${item.query}">${item.query.substring(0, 50)}${item.query.length > 50 ? '...' : ''}</span>
                <div class="simple-item-actions">
                    <button class="btn btn-sm btn-danger" onclick="window.deleteBuilderSaved(${i})"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `).join('');
    }

    window.loadBuilderHistory = function(i) {
        const history = JSON.parse(localStorage.getItem('dorkforge_history') || '[]');
        if (history[i]) { queryDisplay.textContent = history[i].query; queryDisplay.className = 'query-display query-active'; }
    };
    window.deleteBuilderHistory = function(i) {
        const history = JSON.parse(localStorage.getItem('dorkforge_history') || '[]');
        history.splice(i, 1);
        localStorage.setItem('dorkforge_history', JSON.stringify(history));
        renderHistory();
    };
    window.loadBuilderSaved = function(i) {
        const saved = JSON.parse(localStorage.getItem('dorkforge_saved') || '[]');
        if (saved[i]) { queryDisplay.textContent = saved[i].query; queryDisplay.className = 'query-display query-active'; addToHistory(saved[i].query); }
    };
    window.deleteBuilderSaved = function(i) {
        const saved = JSON.parse(localStorage.getItem('dorkforge_saved') || '[]');
        saved.splice(i, 1);
        localStorage.setItem('dorkforge_saved', JSON.stringify(saved));
        renderSaved();
    };

    const inputs = [domain, filetype, intitle, inurl, intext, exact, exclude, exclude_site, before_date, after_date, or_terms, custom];
    inputs.forEach(input => { input.addEventListener('input', buildQuery); input.addEventListener('change', buildQuery); });

    templateSelect.addEventListener('change', function() { if (this.value) { loadTemplate(this.value); this.value = ''; } });

    copyBtn.addEventListener('click', copyQuery);
    openGoogleBtn.addEventListener('click', openInGoogle);
    saveBtn.addEventListener('click', saveQuery);
    resetBtn.addEventListener('click', resetForm);

    // Auto-load template query from sessionStorage
    const templateQuery = sessionStorage.getItem('template_query');
    if (templateQuery) {
        queryDisplay.textContent = templateQuery;
        queryDisplay.className = 'query-display query-active';
        sessionStorage.removeItem('template_query');
    }

    buildQuery();
    renderHistory();
    renderSaved();
});