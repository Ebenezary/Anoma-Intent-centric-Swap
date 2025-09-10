from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import Base, engine, get_db
from .models import Intent, Settlement
from .schemas import IntentCreate, IntentOut, SolveResponse, SettleRequest, SettlementOut
from .solver import Solver
from .utils import validate_chain, chain_to_str

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Anoma-Style Intent-Centric App (Demo)",
    description="A tiny demo for intent posting, solving, and settling.",
    version="0.1.0",
)

# Allow frontend to talk to backend during local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def root():
    return {"message": "API up. See /docs for Swagger."}

@app.post("/intents", response_model=IntentOut, tags=["Intents"])
def create_intent(payload: IntentCreate, db: Session = Depends(get_db)):
    intent = Intent(
        actor=payload.actor.strip(),
        offer=payload.offer.strip(),
        want=payload.want.strip(),
        deadline=payload.deadline.strip() if payload.deadline else None,
        is_open=True,
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)
    return intent

@app.get("/intents", response_model=List[IntentOut], tags=["Intents"])
def list_intents(db: Session = Depends(get_db)):
    intents = db.query(Intent).order_by(Intent.id.desc()).all()
    return intents

@app.get("/intents/{intent_id}", response_model=IntentOut, tags=["Intents"])
def get_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter_by(id=intent_id).first()
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intent

@app.delete("/intents/{intent_id}", tags=["Intents"])
def cancel_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter_by(id=intent_id).first()
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    intent.is_open = False
    db.commit()
    return {"status": "ok", "message": "Intent canceled"}

@app.post("/solve/{intent_id}", response_model=SolveResponse, tags=["Solve"])
def solve_chain(intent_id: int, db: Session = Depends(get_db)):
    solver = Solver(db=db, max_depth=6)
    chain = solver.find_chain(start_id=intent_id)
    if not chain or len(chain) < 2:
        raise HTTPException(status_code=404, detail="No chain found for this intent")
    return SolveResponse(chain=chain)

@app.post("/settle", response_model=SettlementOut, tags=["Settle"])
def settle_chain(payload: SettleRequest, db: Session = Depends(get_db)):
    chain_ids = payload.chain
    if not validate_chain(db, chain_ids):
        raise HTTPException(status_code=400, detail="Invalid or stale chain")

    # Mark intents closed
    intents = db.query(Intent).filter(Intent.id.in_(chain_ids)).all()
    for i in intents:
        i.is_open = False
    db.commit()

    # Record settlement
    st = Settlement(chain=chain_to_str(chain_ids))
    db.add(st)
    db.commit()
    db.refresh(st)
    return st

@app.get("/settlements", response_model=List[SettlementOut], tags=["Settle"])
def list_settlements(db: Session = Depends(get_db)):
    rows = db.query(Settlement).order_by(Settlement.id.desc()).all()
    return rows
