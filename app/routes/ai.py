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

    # Use a reliable model with large context
    model = current_app.config.get('GROQ_MODEL', 'llama-3.1-70b-versatile')
    api_url = current_app.config.get('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')

    system_prompt = f"""You are an expert OSINT and Google Dorking assistant. Your task is to generate **25 to 30 highly diverse, specific, and unique Google dork queries** based on the user's goal.

**ABSOLUTE RULES:**
1. **Maximum number of dorks: 30**. Aim for 25–30; never fewer than 20.
2. **Each dork must be distinct** – use different operator combinations, search angles, and targets.
3. **Avoid simple variations** – changing one keyword or operator is not enough; use entirely different logical approaches.
4. **Operator diversity**: Use a wide array of operators: `site:`, `filetype:`, `intitle:`, `inurl:`, `intext:`, exact phrase `" "`, exclusion `-`, `OR`, `before:`, `after:`, custom terms, parentheses `( )` for grouping, and nested conditions.
5. **Be specific**: Queries should be detailed (e.g., `site:example.com intitle:"annual report" filetype:pdf intext:"2024"`).
6. **Contextual relevance**: If the user mentions a domain (e.g., "nasa"), use it in `site:`; otherwise use `example.com`.

**Goal:** {goal}

**STRUCTURE YOUR RESPONSE** exactly in this JSON format (no extra text, no markdown):

{{
    "understanding": "A brief one‑sentence summary of the user's goal.",
    "dorks": [
        {{
            "name": "A descriptive title (max 6 words)",
            "query": "The actual Google query string",
            "explanation": "What this query finds (10‑15 words)",
            "security_context": "Why it matters (10‑15 words)"
        }},
        ...  // 25‑30 items
    ],
    "responsible_use": "Only search systems you own or have explicit permission to assess."
}}

Make every dork count – no filler. Provide the broadest possible coverage of the user's request."""

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
        'temperature': 0.7,          # Creative but controlled
        'max_tokens': 3500,          # Allow longer responses
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=90)
        
        if response.status_code == 401:
            return jsonify({'error': 'Invalid Groq API key. Please check your GROQ_API_KEY in .env'}), 401
        elif response.status_code == 429:
            return jsonify({'error': 'Rate limit exceeded. Please wait and try again.'}), 429
        elif response.status_code != 200:
            return jsonify({'error': f'Groq API error (HTTP {response.status_code}): {response.text}'}), response.status_code

        result = response.json()
        content = result['choices'][0]['message']['content'].strip()

        # Parse JSON from the AI response
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

        # Ensure we have enough dorks (at least 15, but aim for 25)
        if len(ai_response['dorks']) < 10:
            return jsonify({'error': 'AI generated too few dorks. Please try a broader goal.'}), 500

        # Limit to 30 to avoid UI overload
        if len(ai_response['dorks']) > 30:
            ai_response['dorks'] = ai_response['dorks'][:30]

        # Validate each dork has required fields
        for dork in ai_response['dorks']:
            if 'name' not in dork or 'query' not in dork:
                return jsonify({'error': 'AI response missing required fields in a dork object.'}), 500

        return jsonify(ai_response)

    except requests.exceptions.Timeout:
        return jsonify({'error': 'The AI request timed out (90 seconds). Please try a simpler goal.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error calling Groq API: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500