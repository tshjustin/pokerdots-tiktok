# app/pools/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class CompensationRuleIn(BaseModel):
    period: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="YYYY-MM")
    human_multiplier: float = 1.2
    ai_multiplier: float = 0.7
    dpv_base: float = 1.0  # base $ per effective token (optional if you have an external pool amount)

class CompensationRuleOut(CompensationRuleIn):
    id: int

class PoolShareOut(BaseModel):
    creator_id: int
    token_count: int
    effective_tokens: float
    share_pct: float
    payout_amount: float

class PoolSummaryOut(BaseModel):
    pool_id: int
    period: str
    base_amount: float
    total_effective_tokens: float
    shares: List[PoolShareOut]

class CloseAndSettleIn(BaseModel):
    period: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="YYYY-MM")
    base_amount: float = Field(..., ge=0, description="Total $ pool amount for the month")
    force_recompute: bool = False  # if True, recompute & overwrite existing settlement (admin-only)
