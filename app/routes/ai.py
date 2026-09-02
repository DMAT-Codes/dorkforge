from flask import Blueprint, render_template, request, jsonify, current_app
import json
import requests
import re

bp = Blueprint('ai', __name__, url_prefix='/ai')

@bp.route('/')
def index():
    return render_template('ai.html')

@bp.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    goal = data.get('goal', '').strip()
    
    if not goal:
        return jsonify({'error': 'Please enter a goal.'}), 400

    api_key = current_app.config.get('GROQ_API_KEY')
    if not api_key:
        return jsonify({
            'error': 'Groq API key is missing. Please set GROQ_API_KEY in your .env file and restart the server.'
        }), 500

    # Use a reliable model
    model = current_app.config.get('GROQ_MODEL', 'mixtral-8x7b-32768')
    api_url = current_app.config.get('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')

    system_prompt = f"""You are an expert OSINT and Google Dorking assistant. Generate **10 to 15** highly relevant, accurate, and diverse Google dork queries based on the user's goal.

**RULES:**
- If the user mentions a specific domain (e.g., "nasa", "google", "microsoft"), use that exact domain with `site:` (e.g., `site:nasa.gov`). If no domain is mentioned, use `example.com`.
- Generate a wide variety of queries covering different operators:
  - site:, filetype:, intitle:, inurl:, intext:, 
  - Exact phrase ("")
  - Exclusion (-)
  - OR
  - before:, after:
- Ensure each query is **realistic and useful** for security awareness or OSINT.
- Provide a clear **explanation** and **security context** for each dork.
- Respond **ONLY** with a valid JSON object. No extra text, no markdown, no code blocks.

**JSON STRUCTURE (exactly):**
{{
    "understanding": "A brief, one-sentence summary of the user's goal.",
    "dorks": [
        {{
            "name": "Short descriptive title",
            "query": "The actual Google query string",
            "explanation": "What this specific query finds.",
            "security_context": "Why this matters for security awareness."
        }}
    ],
    "responsible_use": "Only search systems you own or have explicit permission to assess."
}}

**Important:** The query must be properly escaped for URL encoding (but keep it as a plain string). Use double quotes inside the query when needed, e.g., `intitle:"admin"`.

**Goal:** {goal}

Generate 10-15 diverse dorks that cover the user's request as comprehensively as possible."""

    user_prompt = f"User goal: {goal}"

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'temperature': 0.5,  # Slightly higher for creativity
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 401:
            return jsonify({'error': 'Invalid Groq API key. Please check your GROQ_API_KEY in .env'}), 401
        elif response.status_code == 429:
            return jsonify({'error': 'Rate limit exceeded. Please wait and try again.'}), 429
        elif response.status_code != 200:
            return jsonify({'error': f'Groq API error (HTTP {response.status_code}): {response.text}'}), response.status_code

        result = response.json()
        content = result['choices'][0]['message']['content'].strip()

        # Try to parse JSON from the content
        try:
            ai_response = json.loads(content)
        except json.JSONDecodeError:
            # Attempt to extract JSON with regex
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    ai_response = json.loads(match.group())
                except:
                    return jsonify({'error': 'AI response contained invalid JSON. Please try again.'}), 500
            else:
                return jsonify({'error': 'AI did not return a valid JSON. Please try again with a clearer goal.'}), 500

        # Validate structure
        if 'dorks' not in ai_response or not isinstance(ai_response['dorks'], list):
            return jsonify({'error': 'AI response missing required "dorks" array.'}), 500

        if len(ai_response['dorks']) < 3:
            return jsonify({'error': 'AI generated too few dorks. Please try a broader goal.'}), 500

        for dork in ai_response['dorks']:
            if 'name' not in dork or 'query' not in dork:
                return jsonify({'error': 'AI response missing required fields in a dork object.'}), 500

        # Limit to 20 dorks max to avoid overwhelming UI
        if len(ai_response['dorks']) > 20:
            ai_response['dorks'] = ai_response['dorks'][:20]

        return jsonify(ai_response)

    except requests.exceptions.Timeout:
        return jsonify({'error': 'The AI request timed out (60 seconds). Please try a simpler goal.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error calling Groq API: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500