import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- NEW IMPORT
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # <-- CRITICAL FIX: Allows frontend JS to call this API

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

    except Exception as e:
        print(f"Error during plan generation: {e}")
        return jsonify({"error": f"Failed to generate plan. Detail: {str(e)}"}), 500

if __name__ == '__main__':
    # Running on a specific port for development
    app.run(debug=True, port=5000)