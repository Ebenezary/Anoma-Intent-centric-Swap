from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Intent

class Solver:
    """A tiny depth-limited DFS solver for direct and multi-hop cycles."""

    def __init__(self, db: Session, max_depth: int = 6):
        self.db = db
        self.max_depth = max_depth

    def _get_open_intents(self) -> List[Intent]:
        return self.db.query(Intent).filter(Intent.is_open == True).all()

    def find_chain(self, start_id: int) -> Optional[List[int]]:
        intents = self._get_open_intents()
        id_map = {i.id: i for i in intents}
        start = id_map.get(start_id)
        if not start:
            return None

        visited = set()

        def dfs(current: Intent, chain: List[Intent]):
            if len(chain) > self.max_depth:
                return None

            # If next offer satisfies the original want, we can close the loop
            if len(chain) >= 2 and chain[-1].offer == chain[0].want:
                return [i.id for i in chain]

            for nxt in intents:
                if nxt.id in {c.id for c in chain}:
                    continue
                # We can go to 'nxt' if it offers what current wants
                if nxt.offer == current.want and nxt.is_open:
                    res = dfs(nxt, chain + [nxt])
                    if res:
                        return res
            return None

        # Start chain with the starting intent
        return dfs(start, [start])
