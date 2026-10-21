import json
import re
import time
import requests
from flask import current_app

class GroqError(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

# Optimized prompt to fit 30 dorks within the token limit
SYSTEM_PROMPT_TEMPLATE = """You are an expert OSINT and Google Dorking assistant. Generate 20 to 30 highly diverse Google dork queries based on the user's goal.

RULES:
1. Aim for 20-30 dorks. Keep explanations SHORT (5-8 words) to save space.
2. Each dork must be distinct - use different operators (site:, filetype:, intitle:, inurl:, intext:, OR, before:, after:).
3. JSON FORMATTING: You MUST use single quotes (') instead of double quotes (") inside the "query" string. 
   - BAD: "query": "intitle:\\"admin\\""
   - GOOD: "query": "intitle:'admin'"
4. If no domain is mentioned, use example.com.

Respond ONLY with a valid JSON object. No extra text.

{{
    "understanding": "One-sentence summary.",
    "dorks": [
        {{
            "name": "Short title",
            "query": "The Google query string",
            "explanation": "Short explanation",
            "security_context": "Short security context"
        }}
    ],
    "responsible_use": "Only search systems you own or have permission to assess."
}}

Goal: {goal}"""

def generate_dorks(goal, max_dorks=30):
    api_key = current_app.config.get('GROQ_API_KEY')
    if not api_key:
        raise GroqError('Groq API key is missing.', 500)

    model = current_app.config.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
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
        'temperature': 0.6,
        'max_tokens': 4000, # Maximum safe limit for Groq to prevent cut-offs
    }

    MAX_RETRIES = 3
    INITIAL_DELAY = 2
    response = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        except requests.exceptions.Timeout:
            raise GroqError('The AI request timed out. Please try again.', 504)
        except requests.exceptions.RequestException:
            raise GroqError('Network error. Please check your connection.', 500)

        if response.status_code == 429:
            if attempt == MAX_RETRIES - 1:
                raise GroqError('Rate limit exceeded. Please wait a minute.', 429)
            time.sleep(INITIAL_DELAY * (2 ** attempt))
        else:
            break

    if response.status_code != 200:
        # HIDE THE UGLY JSON ERROR: Convert it to a friendly message
        error_msg = response.json().get('error', {}).get('message', '')
        if 'json_validate_failed' in str(response.json()) or 'Failed to validate JSON' in error_msg:
            raise GroqError('The AI generated too many dorks at once and timed out. Please click Generate again.', 500)
        raise GroqError('The AI service is currently busy. Please try again.', response.status_code)

    try:
        content = response.json()['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError):
        raise GroqError('Unexpected API response structure.', 500)

    # Clean Markdown code blocks if present
    content = re.sub(r'^```(?:json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)

    # Regex to extract just the JSON object {}
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        content = match.group()

    # Fix any accidental double quotes inside the query string that break JSON
    content = content.replace('\\\\\\"', "'").replace('\\"', "'")

    try:
        ai_response = json.loads(content)
    except json.JSONDecodeError:
        # If it still fails, give a friendly UI message
        raise GroqError('The AI generated an incomplete response. Please click Generate again.', 500)

    if 'dorks' not in ai_response:
        raise GroqError('AI response missing dorks. Please try again.', 500)

    # Enforce the 20-30 limit
    ai_response['dorks'] = ai_response['dorks'][:max_dorks]

    return ai_response