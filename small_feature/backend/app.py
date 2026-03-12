"""
THE BULL CONTRACTS - Small Feature
Backend server: receives a contract text, asks Claude to analyze it,
returns structured JSON that the frontend will display and save to Gun.js.

Why Flask and not FastAPI?
  You know Python. Flask is the simplest way to expose a URL that the
  browser can call. Think of it as a small "translator" between the
  browser and Claude.

Why not LangChain here?
  LangChain is powerful but adds layers of abstraction that hide what's
  really happening. For learning, we call Claude directly so you can see
  every step. Once you understand this, LangChain will make more sense.
"""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Load the ANTHROPIC_API_KEY from the .env file
load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    print("\n⚠  ERROR: ANTHROPIC_API_KEY not found.")
    print("   Create a .env file in the backend/ folder with:")
    print("   ANTHROPIC_API_KEY=sk-ant-...\n")

app = Flask(__name__)

# CORS is no longer needed — Flask now serves the HTML files directly.
# When the browser, the HTML page, and the API are all on the same
# origin (localhost:5000), the browser doesn't apply CORS restrictions.
# Same origin = same protocol + same host + same port.
CORS(app)

# ── SERVE FRONTEND FILES ──────────────────────────────────────────────────
# This tells Flask: "if someone requests a .html file, look for it in
# the ../frontend/ folder relative to this app.py file."
#
# os.path.dirname(__file__)  = the folder where app.py lives  (backend/)
# os.path.join(..., '..', 'frontend') = one level up, then into frontend/
#
# So visiting http://localhost:5000/lawyer.html serves lawyer.html,
# and http://localhost:5000/party.html serves party.html.
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'lawyer.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

client = Anthropic()


# ---------------------------------------------------------------------------
# THE PROMPT — this is the heart of the AI analysis
# We ask Claude to return ONLY valid JSON (no extra text) so we can parse it.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are a legal contract analyst.
When given a contract, you extract two things and return ONLY valid JSON — no explanation, no markdown, no code fences.

Return this exact structure:
{
  "contract_summary": "one sentence summary",
  "parties": {
    "owner": "name and role",
    "renter": "name and role"
  },
  "payment_schedule": [
    {
      "id": "pay_1",
      "description": "what this payment is for",
      "amount": 0,
      "currency": "USD",
      "due_when": "human readable timing",
      "paid_by": "name",
      "confirmed_by": "name",
      "status": "pending"
    }
  ],
  "terms": [
    {
      "id": "term_1",
      "description": "what must happen",
      "deadline": "when it must happen",
      "responsible_party": "who must do it",
      "verified_by": "who confirms it was done",
      "status": "pending"
    }
  ]
}

Rules:
- payment_schedule: only include items where money moves (deposits, rent, refunds)
- terms: only include obligations/conditions that need to be verified (not the payments)
- status is always "pending" — the app will track real status separately
- if a date is not specified, use a descriptive string like "Monthly" or "Within 30 days of start"
"""


@app.route("/health", methods=["GET"])
def health():
    """Simple check to confirm the server is running."""
    return jsonify({"status": "ok"})


@app.route("/analyze", methods=["POST"])
def analyze_contract():
    """
    Receives contract text from the browser.
    Sends it to Claude.
    Returns structured JSON.

    The browser sends:  { "contract_text": "..." }
    We return:          { "success": true, "data": { ...parsed contract... } }
    """
    # Wrap everything in try/except so errors come back as readable JSON
    # instead of a silent 500. Check the Flask terminal for the full traceback.
    try:
        return _do_analyze()
    except Exception as e:
        import traceback
        traceback.print_exc()   # prints full error to Flask terminal
        return jsonify({"success": False, "error": str(e)}), 500

def _do_analyze():
    body = request.get_json()

    if not body or "contract_text" not in body:
        return jsonify({"success": False, "error": "Missing contract_text"}), 400

    contract_text = body["contract_text"]

    # Call Claude
    # We use claude-sonnet-4-6 — powerful enough for legal text, fast enough for UI
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Analyze this contract and return the JSON:\n\n{contract_text}",
            }
        ],
    )

    # message.content is a list; the first item is the text block
    raw_text = message.content[0].text

    # Parse the JSON Claude returned
    # If Claude added markdown fences (```json ... ```) strip them first
    clean = raw_text.strip().strip('`')
    if clean.startswith('json'):
        clean = clean[4:]

    parsed = json.loads(clean)

    return jsonify({"success": True, "data": parsed})


if __name__ == "__main__":
    # debug=True means Flask auto-reloads when you save the file
    # port 5000 is the standard Flask port
    print("Starting The Bull Contracts backend on http://localhost:5000")
    app.run(debug=True, port=5000)
