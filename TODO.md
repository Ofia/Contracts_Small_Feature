# The Bull Contracts — TODO

## Session — 2026-03-12

### Done today ✓
- **UI redesign** — both dashboards (lawyer + party) rebuilt with clean light theme
  - Inter font, dot-grid background, white cards, hairline borders
  - Monochrome palette, no framework, same JS logic underneath
- **Block 2: Lawyer countersigns** — lawyer.html now:
  - Listens live (`Gun .map().on()`) for party confirmations after publishing
  - Shows a "Party Confirmations" inbox that appears automatically when first item arrives
  - "Countersign & Seal" button per item → SEA.sign() with lawyer's key → writes lawyerSignature to Gun
  - Sealed items: status flips to `confirmed` → party.html picks it up in real-time ✓
  - Immutability by convention: checks lawyerSignature before allowing re-seal
- **Infrastructure fixes**
  - Flask now serves the HTML files directly (no separate frontend server needed)
  - Removed dead Gun relay (gun-manhattan Heroku RIP), Gun runs localStorage-only for local dev
  - Added startup check for missing ANTHROPIC_API_KEY
  - Added try/except in `/analyze` — errors now surfaced as JSON, not silent 500s
  - Added markdown fence stripping on Claude output (defensive JSON parsing)

---

## Open for Tomorrow

### Block 3 — Immutable chain (blockchain-style sealing)
- Each sealed record should store a `previousHash` field
- `previousHash` = hash of the previous sealed record, computed with `SEA.work()`
- This creates a tamper-evident chain: if any record is edited, the chain breaks
- Add a "Verify Chain" button on lawyer.html that walks the chain and checks all hashes

### Block 4 — IPFS file storage
- Instead of passing raw contract text to Flask, upload the file to IPFS
- IPFS returns a CID (Content Identifier) — a fingerprint of the file
- Store the CID in Gun, not the raw text
- Anyone with the CID can retrieve the original file from IPFS forever
- Libraries to explore: `ipfs-http-client` (JS) or Pinata API (easier, no local node)

### Block 5 — Gun relay (multi-device sync)
- Right now Gun only syncs within the same browser (localStorage)
- To sync between two real devices, we need a relay
- Easiest path: add a tiny Node.js relay server (`gun-relay.js`) to the project
  - Just 5 lines: `require('gun')({web: require('http').createServer().listen(8765)})`
- Or explore self-hosting on a free tier (Railway, Fly.io, Render)

### Small improvements backlog
- Filter action buttons by `currentUser` — only show "Submit" to the responsible party
- Add a party name display on lawyer.html's confirmation inbox (show who the party is)
- Auto-scroll confirmation inbox to newest entry
- Add a timestamp to sealed records visible on party.html

---

## How to Run (current state)
```bash
# 1. Start backend (also serves frontend)
cd "small_feature/backend"
python app.py

# 2. Open in browser (two tabs, same browser)
http://localhost:5000/lawyer.html
http://localhost:5000/party.html
```
