## Anoma Intent-centric Swap Demo"

A beginner-friendly, end-to-end demo that shows how **intent-centric coordination** can work in practice.

You’ll run a **FastAPI backend** (SQLite for storage) and a **vanilla HTML/CSS/JS frontend**.  
No complex frameworks required. Everything is heavily commented for learning.

---

## What You’ll Build

- Post **intents** (what you offer, what you want, deadline, name)
- View open intents
- **Solve** (find matching chains) automatically up to a small depth
- **Settle** chains to complete multi-hop swaps
- Cancel your intent

This mirrors a tiny slice of Anoma’s intent-centric idea: you describe **what** you want, the system figures out **how**.

---

## Prereqs

- Python 3.10+
- `pip` installed
- A modern browser (for the frontend)

---

## Setup

1) Open a terminal and go to the project directory:

```bash
cd anoma-intent-app
```

2) Create a virtualenv (recommended):

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

3) Install backend dependencies:

```bash
pip install -r requirements.txt
```

4) Run the backend (in one terminal):

```bash
uvicorn backend.app.main:app --reload
```
This starts the API at `http://127.0.0.1:8000`

5) Open the frontend `index.html` in your browser:  
- Option A (simplest): double-click `frontend/index.html` to open it.  
  If your browser blocks fetches due to CORS/file origin, use Option B.
- Option B (recommended): run a tiny local static server from `frontend`:

```bash
# from the project root
cd frontend
python -m http.server 5500
```
Now visit: `http://127.0.0.1:5500`

6) Start posting intents and try solving/settling chains!

---

## Project Structure

```
anoma-intent-app/
├─ README.md
├─ requirements.txt
├─ backend/
│  └─ app/
│     ├─ main.py         # FastAPI app with routes and CORS
│     ├─ database.py     # SQLite engine + Session management
│     ├─ models.py       # SQLAlchemy ORM models
│     ├─ schemas.py      # Pydantic models (request/response)
│     ├─ solver.py       # Intent matching logic (direct + multi-hop chains)
│     └─ utils.py        # Helpers (validation, chain checks)
└─ frontend/
   ├─ index.html
   ├─ styles.css
   └─ script.js
```

---

## How Matching Works (Simple Version)

- **Direct match**: A offers X and wants Y; B offers Y and wants X
- **Chain match**: A offers X → B wants X (offers Y) → C wants Y (offers Z) → ... until we loop back to satisfy A’s want with someone’s offer

The solver uses a **depth-limited DFS** to find small cycles.  
In real systems, you’d add pricing, quantities, privacy, proofs, etc.—this demo is intentionally simple.

---

## API Quick Reference

- `POST /intents` — create an intent
- `GET /intents` — list open intents
- `GET /intents/{id}` — fetch one
- `DELETE /intents/{id}` — cancel
- `POST /solve/{intent_id}` — find a chain for an intent
- `POST /settle` — finalize a returned chain

You can also explore at: `http://127.0.0.1:8000/docs` (Swagger UI)

---

## Example Chain

Alice offers Coffee Beans, wants Bike Fix  
Bob offers Bike Fix, wants Spanish Tutoring  
Carla offers Spanish Tutoring, wants Bread  
David offers Bread, wants Coffee Beans  

The solver finds the cycle and proposes a **settlement** that satisfies all four.

---

## Learning Notes

- We separate **schemas** (Pydantic) from **models** (SQLAlchemy)
- We use **dependency-injected DB sessions**
- The solver is **pure Python**, easy to read and extend
- All code is explained with comments

Have fun building! This is a teaching project, not production software.
# Anoma-Intent-centric-Swap
