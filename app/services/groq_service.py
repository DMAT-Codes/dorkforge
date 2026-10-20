import json
import re
import time
import requests
from flask import current_app


class GroqError(Exception):
    """Raised when the Groq API call or parsing fails."""
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


SYSTEM_PROMPT_TEMPLATE = """You are an expert OSINT and Google Dorking assistant. Generate 25 to 30 highly diverse, specific, and unique Google dork queries based on the user's goal.

ABSOLUTE RULES:
1. Maximum number of dorks: 30. Aim for 25-30; never fewer than 20.
2. Each dork must be distinct - different operator combinations, angles, targets.
3. Avoid simple variations - use entirely different logical approaches.
4. Operator diversity: site:, filetype:, intitle:, inurl:, intext:, exact phrase " ", exclusion -, OR, before:, after:, custom terms, parentheses for grouping.
5. Be specific: queries should be detailed.
6. If the user mentions a domain (e.g., "nasa"), use it in site:; otherwise use example.com.

STRUCTURE YOUR RESPONSE exactly in this JSON format (no extra text, no markdown, NO code blocks):
{{
    "understanding": "One-sentence summary of the user's goal.",
    "dorks": [
        {{
            "name": "Descriptive title (max 6 words)",
            "query": "The actual Google query string",
            "explanation": "What this query finds (10-15 words)",
            "security_context": "Why it matters (10-15 words)"
        }}
    ],
    "responsible_use": "Only search systems you own or have explicit permission to assess."
}}

Goal: {goal}"""


def generate_dorks(goal, max_dorks=30):
    """
    Call Groq API and return parsed JSON with up to `max_dorks` dorks.
    Raises GroqError on failure.
    """
    api_key = current_app.config.get('GROQ_API_KEY')
    if not api_key:
        raise GroqError(
            'Groq API key is missing. Please set GROQ_API_KEY in the environment.',
            status_code=500
        )

    model = current_app.config.get('GROQ_MODEL', 'llama-3.1-70b-versatile')
    api_url = current_app.config.get(
        'GROQ_API_URL',
        'https://api.groq.com/openai/v1/chat/completions'
    )

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT_TEMPLATE.format(goal=goal)},
            {'role': 'user', 'content': f'User goal: {goal}'},
        ],
        'temperature': 0.7,
        'max_tokens': 3000,  # Increased to fit 30 dorks without cutting off the JSON
    }

    # --- HTTP call with Retry Logic (Exponential Backoff) ---
    MAX_RETRIES = 3
    INITIAL_DELAY = 2
    response = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=90)
        except requests.exceptions.Timeout:
            raise GroqError('The AI request timed out (90 seconds). Please try a simpler goal.', 504)
        except requests.exceptions.RequestException as exc:
            raise GroqError(f'Network error calling Groq API: {exc}', 500)

        # Check for rate limit (429)
        if response.status_code == 429:
            if attempt == MAX_RETRIES - 1:
                raise GroqError('Rate limit exceeded after multiple retries. Please wait a minute and try again.', 429)
            
            delay = INITIAL_DELAY * (2 ** attempt)
            print(f"[Groq API] Rate limit hit (429). Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            break

    # --- HTTP status handling ---
    if response.status_code == 401:
        raise GroqError('Invalid Groq API key. Please check GROQ_API_KEY.', 401)
    elif response.status_code == 429:
        raise GroqError('Rate limit exceeded. Please wait and try again.', 429)
    elif response.status_code != 200:
        raise GroqError(
            f'Groq API error (HTTP {response.status_code}): {response.text}',
            response.status_code
        )

    # --- Parse content ---
    try:
        content = response.json()['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError):
        raise GroqError('Unexpected response structure from Groq API.', 500)

    # --- Clean the content to ensure valid JSON ---
    # 1. Remove markdown code blocks if the AI added them (e.g., ```json ... ```)
    json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
        
    # 2. Extract from the first '{' to the last '}' to ignore any extra conversational text
    start = content.find('{')
    end = content.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        content = content[start:end+1]

    try:
        ai_response = json.loads(content)
    except json.JSONDecodeError:
        raise GroqError('AI response contained invalid JSON. Please try again. (Tip: The response may have been cut off by token limits).', 500)

    # --- Validate structure ---
    if 'dorks' not in ai_response or not isinstance(ai_response['dorks'], list):
        raise GroqError('AI response missing required "dorks" array.', 500)

    if len(ai_response['dorks']) < 10:
        raise GroqError('AI generated too few dorks. Please try a broader goal.', 500)

    if len(ai_response['dorks']) > max_dorks:
        ai_response['dorks'] = ai_response['dorks'][:max_dorks]

    for dork in ai_response['dorks']:
        if 'name' not in dork or 'query' not in dork:
            raise GroqError('AI response missing required fields in a dork object.', 500)

    return ai_response