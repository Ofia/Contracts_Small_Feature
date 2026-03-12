# The Bull Contracts — Small Feature

A hands-on learning app for a "live contract" platform where lawyers upload contracts, AI extracts key terms and payments, and all parties track/confirm obligations in real-time via a decentralized network.

## What it does

1. **Lawyer** uploads a contract → Flask backend sends it to Claude AI → structured JSON with payments and terms comes back → lawyer publishes to Gun.js (decentralized DB)
2. **Parties** open a shared link → see their obligations live → submit signed confirmations using their crypto keypair
3. All data lives in **every connected browser's localStorage** — no central server owns it

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python Flask + Anthropic SDK |
| AI | Claude claude-sonnet-4-6 |
| Decentralized DB | Gun.js + SEA (crypto signing) |
| Frontend | Plain HTML/JS |

## How to run

```bash
# 1. Install Python dependencies
cd "small feature/backend"
pip install -r requirements.txt

# 2. Add your API key
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=...

# 3. Start the backend
python app.py
# → runs on http://localhost:5000

# 4. Open the frontend
# Double-click small feature/frontend/lawyer.html in your browser
```

## File structure

```
small feature/
├── backend/
│   ├── app.py            ← Flask server, calls Claude API
│   └── requirements.txt
└── frontend/
    ├── lawyer.html       ← Upload contract, analyze, publish
    └── party.html        ← View contract, submit confirmations
```

## Current status

- Lawyer dashboard: drag & drop upload, Claude analysis, Gun.js publish, share link
- Party dashboard: loads contract by URL param, real-time sync, signed confirmations
- Next: lawyer countersign flow, immutable sealed records, IPFS file storage
