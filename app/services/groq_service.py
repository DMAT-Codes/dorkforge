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

You must respond strictly in valid JSON format with the exact structure below. Ensure all internal quotes within the query strings are properly escaped (e.g., use \\" instead of "). Do not use markdown code blocks.

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
    api_key = current_app.config.get('GROQ_API_KEY')
    if not api_key:
        raise GroqError('Groq API key is missing.', 500)

    model = current_app.config.get('GROQ_MODEL', 'llama-3.1-70b-versatile')
    api_url = current_app.config.get('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')

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
        'max_tokens': 4000, # Plenty of room
        'response_format': {'type': 'json_object'} # FORCES the AI to return valid JSON
    }

    MAX_RETRIES = 3
    INITIAL_DELAY = 2
    response = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=90)
        except requests.exceptions.Timeout:
            raise GroqError('The AI request timed out. Please try again.', 504)
        except requests.exceptions.RequestException as exc:
            raise GroqError(f'Network error: {exc}', 500)

        if response.status_code == 429:
            if attempt == MAX_RETRIES - 1:
                raise GroqError('Rate limit exceeded. Please wait a minute.', 429)
            delay = INITIAL_DELAY * (2 ** attempt)
            time.sleep(delay)
        else:
            break

    if response.status_code == 401:
        raise GroqError('Invalid Groq API key.', 401)
    elif response.status_code != 200:
        raise GroqError(f'API Error: {response.text}', response.status_code)

    try:
        content = response.json()['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError):
        raise GroqError('Unexpected API response structure.', 500)

    # Clean any accidental markdown
    content = re.sub(r'^```json\s*', '', content)
    content = re.sub(r'\s*```$', '', content)

    try:
        ai_response = json.loads(content)
    except json.JSONDecodeError as e:
        # Fallback: If the AI broke the quotes, try to extract the outer structure
        print(f"JSON Decode Error: {e}")
        raise GroqError('AI returned malformed JSON. Please try again.', 500)

    if 'dorks' not in ai_response or not isinstance(ai_response['dorks'], list):
        raise GroqError('AI response missing "dorks" array.', 500)

    if len(ai_response['dorks']) < 10:
        raise GroqError('AI generated too few dorks. Please try a broader goal.', 500)

    if len(ai_response['dorks']) > max_dorks:
        ai_response['dorks'] = ai_response['dorks'][:max_dorks]

    return ai_response