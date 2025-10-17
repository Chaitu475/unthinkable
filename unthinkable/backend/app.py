import os
import json
from flask import Flask, request, jsonify, send_file # <-- Added send_file
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allows frontend JS to call this API

# --- Gemini API Configuration ---
# Ensure GOOGLE_API_KEY is set in your .env file
try:
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env")
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    # This error will show up in the Flask console
    print(f"Error initializing Gemini client: {e}")
    client = None

# --- Prompt Guidance (as per technical expectations) ---
SYSTEM_INSTRUCTION = (
    "You are a 'Smart Task Planner' AI. Your goal is to break down a high-level user goal "
    "into a detailed, actionable list of tasks with clear deadlines and dependencies. "
    "Respond ONLY with a JSON object. Do not include any introductory or concluding text."
)

PROMPT_TEMPLATE = (
    "Break down this goal into actionable tasks with suggested deadlines and dependencies. "
    "The input goal is: '{goal}'"
)

# --- JSON Schema for Structured Output ---
TASK_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "task_id": {"type": "integer", "description": "Unique ID for the task."},
            "task_name": {"type": "string", "description": "Short, descriptive task title."},
            "description": {"type": "string", "description": "Detailed explanation of the task."},
            "deadline": {"type": "string", "description": "Suggested deadline (e.g., '3 days from now' or 'YYYY-MM-DD')."},
            "dependencies": {"type": "array", "items": {"type": "integer"}, "description": "Array of task_ids that must be completed before this task."}
        },
        "required": ["task_id", "task_name", "deadline", "dependencies"]
    }
}

# NEW ROUTE: Serve the frontend index.html file
@app.route('/')
def serve_frontend():
    # Construct the path to the index.html file
    # Assumes the script is run from the backend/ directory or the project root.
    # Adjust the path as necessary based on where you run app.py
    frontend_path = os.path.join(os.getcwd(), '..', 'frontend', 'index.html')
    if not os.path.exists(frontend_path):
        # Fallback if running from a different directory
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')

    try:
        return send_file(frontend_path)
    except Exception as e:
        return f"Error serving frontend: {str(e)}. Check that frontend/index.html exists and that you are running 'python app.py' from the 'backend' folder.", 500

# NEW ROUTE: Serve static files (CSS, JS)
@app.route('/<filename>')
def serve_static(filename):
    if filename.endswith(('.css', '.js')):
        static_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', filename)
        try:
            return send_file(static_path)
        except Exception:
            return "File Not Found", 404
    return "File Not Found", 404


@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    if not client:
        return jsonify({"error": "API Key is not configured correctly on the server."}), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON payload."}), 400

    user_goal = data.get('goal')

    if not user_goal:
        return jsonify({"error": "Goal text is required."}), 400

    full_prompt = PROMPT_TEMPLATE.format(goal=user_goal)

    try:
        # Retry logic for transient API errors (using exponential backoff concept)
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        response_schema=TASK_SCHEMA
                    )
                )

                # Parse the JSON response text
                task_plan = json.loads(response.text)
                return jsonify(task_plan)

            except Exception as inner_e:
                if attempt < MAX_RETRIES - 1:
                    print(f"Transient error on attempt {attempt + 1}: {inner_e}. Retrying in {2**(attempt+1)} seconds...")
                    import time
                    time.sleep(2**(attempt+1))
                else:
                    raise inner_e # Re-raise final exception

    except Exception as e:
        print(f"Error during plan generation: {e}")
        return jsonify({"error": f"Failed to generate plan. Detail: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
