from pydantic import BaseModel, Field
from typing import Optional, List

class IntentCreate(BaseModel):
    actor: str = Field(..., min_length=1, max_length=64)
    offer: str = Field(..., min_length=1, max_length=128)
    want: str = Field(..., min_length=1, max_length=128)
    deadline: Optional[str] = None

class IntentOut(BaseModel):
    id: int
    actor: str
    offer: str
    want: str
    deadline: Optional[str]
    is_open: bool

    class Config:
        from_attributes = True

class SolveResponse(BaseModel):
    chain: list[int]

class SettleRequest(BaseModel):
    chain: list[int]

class SettlementOut(BaseModel):
    id: int
    chain: str

    class Config:
        from_attributes = True
