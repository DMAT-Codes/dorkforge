def build_query(data):
    """
    Build a Google dork query string from form data.
    
    Args:
        data (dict): Form data with keys like domain, filetype, intitle, etc.
    
    Returns:
        str: The constructed query string.
    """
    parts = []
    breakdown = []
    
    # Domain (site:)
    domain = data.get('domain', '').strip()
    if domain:
        parts.append(f'site:{domain}')
        breakdown.append(f'🔍 Restrict to: {domain}')
    
    # File type (filetype:)
    filetype = data.get('filetype', '').strip()
    if filetype:
        parts.append(f'filetype:{filetype}')
        breakdown.append(f'📄 File type: {filetype}')
    
    # Title (intitle:)
    intitle = data.get('intitle', '').strip()
    if intitle:
        parts.append(f'intitle:"{intitle}"')
        breakdown.append(f'📑 Title contains: "{intitle}"')
    
    # URL (inurl:)
    inurl = data.get('inurl', '').strip()
    if inurl:
        parts.append(f'inurl:"{inurl}"')
        breakdown.append(f'🔗 URL contains: "{inurl}"')
    
    # Text (intext:)
    intext = data.get('intext', '').strip()
    if intext:
        parts.append(f'intext:"{intext}"')
        breakdown.append(f'📝 Text contains: "{intext}"')
    
    # Exact phrase
    exact = data.get('exact', '').strip()
    if exact:
        # Remove surrounding quotes if user added them
        if exact.startswith('"') and exact.endswith('"'):
            parts.append(exact)
        else:
            parts.append(f'"{exact}"')
        breakdown.append(f'💬 Exact phrase: "{exact}"')
    
    # Exclude words
    exclude = data.get('exclude', '').strip()
    if exclude:
        words = exclude.split()
        for word in words:
            parts.append(f'-{word}')
        breakdown.append(f'🚫 Excluded: {exclude}')
    
    # Exclude site
    exclude_site = data.get('exclude_site', '').strip()
    if exclude_site:
        parts.append(f'-site:{exclude_site}')
        breakdown.append(f'🚫 Excluded domain: {exclude_site}')
    
    # Before date
    before_date = data.get('before_date', '').strip()
    if before_date:
        parts.append(f'before:{before_date}')
        breakdown.append(f'📅 Before: {before_date}')
    
    # After date
    after_date = data.get('after_date', '').strip()
    if after_date:
        parts.append(f'after:{after_date}')
        breakdown.append(f'📅 After: {after_date}')
    
    # OR conditions
    or_terms = data.get('or_terms', '').strip()
    if or_terms:
        terms = [term.strip() for term in or_terms.split(',') if term.strip()]
        if terms:
            or_part = ' OR '.join(terms)
            parts.append(f'({or_part})')
            breakdown.append(f'🔀 OR: {or_part}')
    
    # Custom terms
    custom = data.get('custom', '').strip()
    if custom:
        parts.append(custom)
        breakdown.append(f'⚙️ Custom: {custom}')
    
    # Build final query
    query = ' '.join(parts)
    
    # Store breakdown for later use (optional)
    data['_breakdown'] = breakdown
    
    return query


def get_breakdown(data):
    """Return the breakdown list from the data."""
    return data.get('_breakdown', [])