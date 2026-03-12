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
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load the ANTHROPIC_API_KEY from the .env file
load_dotenv()

app = Flask(__name__)

# CORS = Cross-Origin Resource Sharing
# Browsers block JavaScript from calling a different server by default.
# This tells Flask: "it's ok, let the browser on localhost call you."
CORS(app)

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
    # If Claude added any extra text, json.loads will raise an error —
    # that's why we told it in the prompt to return ONLY valid JSON.
    parsed = json.loads(raw_text)

    return jsonify({"success": True, "data": parsed})


if __name__ == "__main__":
    # debug=True means Flask auto-reloads when you save the file
    # port 5000 is the standard Flask port
    print("Starting The Bull Contracts backend on http://localhost:5000")
    app.run(debug=True, port=5000)
