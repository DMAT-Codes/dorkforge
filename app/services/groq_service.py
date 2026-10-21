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
4. Operator diversity: site:, filetype:, intitle:, inurl:, intext:, exclusion -, OR, before:, after:.
5. Be specific: queries should be detailed.
6. IMPORTANT FOR JSON FORMATTING: Because you are returning JSON, you MUST use single quotes (') instead of double quotes (") inside the "query" string. Google accepts single quotes. 
   - BAD: "query": "intitle:\\"admin\\""
   - GOOD: "query": "intitle:'admin'"
7. If the user mentions a domain (e.g., "nasa"), use it in site:; otherwise use example.com.

STRUCTURE YOUR RESPONSE exactly in this JSON format (no extra text, no markdown):
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
        raise GroqError('Groq API key is missing.', status_code=500)

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
        'max_tokens': 4000, 
        'response_format': {'type': 'json_object'} 
    }

    # --- HTTP call with Retry Logic ---
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
        # If Groq gives a specific JSON error, try to extract the AI's broken text and fix it
        error_data = response.json()
        if error_data.get('error', {}).get('code') == 'json_validate_failed':
            broken_json = error_data['error'].get('failed_generation', '')
            if broken_json:
                # Attempt to clean up bad backslashes from the AI's response
                try:
                    cleaned_json = broken_json.replace('\\\\\\"', "'").replace('\\"', "'")
                    ai_response = json.loads(cleaned_json)
                    return ai_response # Successfully salvaged!
                except:
                    pass # If salvage fails, move to the standard error below
        
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
    except json.JSONDecodeError:
        # Final fallback: Extract just the { ... } part
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                ai_response = json.loads(match.group())
            except:
                raise GroqError('AI returned malformed JSON. Please try again.', 500)
        else:
            raise GroqError('AI did not return valid JSON.', 500)

    if 'dorks' not in ai_response or not isinstance(ai_response['dorks'], list):
        raise GroqError('AI response missing "dorks" array.', 500)

    if len(ai_response['dorks']) > max_dorks:
        ai_response['dorks'] = ai_response['dorks'][:max_dorks]

    return ai_response