from typing import List
from sqlalchemy.orm import Session
from .models import Intent

def chain_to_str(chain_ids: List[int]) -> str:
    return ",".join(map(str, chain_ids))

def validate_chain(db: Session, chain_ids: List[int]) -> bool:
    """Very basic check:
    - All intents exist and are open
    - The chain forms a valid cycle where each offer satisfies the next want
    - The last's offer satisfies the first's want
    """
    if not chain_ids or len(chain_ids) < 2:
        return False

    intents = db.query(Intent).filter(Intent.id.in_(chain_ids)).all()
    if len(intents) != len(chain_ids):
        return False

    # Keep order as submitted
    id_to_intent = {i.id: i for i in intents}
    try:
        ordered = [id_to_intent[i] for i in chain_ids]
    except KeyError:
        return False

    # All open?
    if any(not it.is_open for it in ordered):
        return False

    # Check offers/wants alignment around the cycle
    n = len(ordered)
    for idx in range(n):
        cur = ordered[idx]
        nxt = ordered[(idx + 1) % n]
        if cur.offer != nxt.want:
            return False

    return True
