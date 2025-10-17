🚀 Smart Task Planner

The Smart Task Planner is a web application designed to transform high-level objectives into structured, actionable task plans using AI reasoning. It serves as a powerful tool for project managers, students, and anyone needing to break down complex goals into manageable steps.

✨ Features

Intelligent Task Breakdown: Leverages the Gemini API to break down vague goals (e.g., "Launch a product in 2 weeks") into detailed, actionable tasks.

Structured Output (JSON Schema): Enforces a strict JSON format for the AI response, guaranteeing reliable data that includes Task ID, Name, Description, Deadline, and Dependencies.

Real-time Planning: Displays the generated plan with smooth, animated card transitions for an excellent user experience.

Unified Architecture: The Flask backend serves both the API endpoint (/api/generate-plan) and the static frontend files (index.html, CSS, JS) from the root (/).

💻 Technical Stack

Component

Technology

Purpose

Backend

Python 3, Flask

API definition, environment handling, and static file serving.

AI/LLM

Google Gemini API (gemini-2.5-flash)

Core reasoning and structured task generation.

Frontend

HTML5, CSS3, Vanilla JavaScript

Interactive UI for goal submission and plan visualization.

Networking

flask-cors

Resolves cross-origin issues between client and server during local development.

Dependencies (As per requirements.txt):
flask, python-dotenv, google-genai, flask-cors

⚙️ Installation and Setup

1. Project Structure

The project uses the following directory and file structure:

smart-task-planner/
├── backend/
│   ├── app.py            <-- Flask server and AI logic
│   └── __init__.py
├── frontend/
│   ├── index.html        <-- Main user interface
│   ├── style.css         <-- Styling and animations
│   └── script.js         <-- Frontend logic and API calls
├── .env                  <-- 🔑 API Key location
└── requirements.txt      <-- Python dependencies


2. Install Dependencies

Navigate to the root directory of your project and install all required Python packages:

pip install -r requirements.txt


3. Configure API Key

You must provide your Gemini API key for the application to function. Create a file named .env in the root directory and add the key in the following format:

# .env file
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"


▶️ Running the Application

Local Development (Using Flask)

To run the application locally using the built-in Flask development server:

Navigate to the backend directory:

cd backend


Run the application:

python app.py


Open your browser and navigate to the local server address: http://127.0.0.1:5000/
