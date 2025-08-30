# app/pools/pools_router.py
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, and_, select
from sqlalchemy.orm import Session
from app.auth.deps import require_admin as get_admin_user  

from database.session import get_db
from database import models
from .schemas import (
    CloseAndSettleIn,
    PoolSummaryOut,
    PoolShareOut,
    CompensationRuleIn,
    CompensationRuleOut,
)

router = APIRouter(prefix="/pools", tags=["Pools"])



# --- Helpers ---
def month_bounds(period: str) -> Tuple[datetime, datetime]:
    """period: 'YYYY-MM' -> (month_start_utc, month_end_utc)"""
    dt = datetime.strptime(period, "%Y-%m")
    # naive -> UTC
    start = datetime(dt.year, dt.month, 1, tzinfo=timezone.utc)
    if dt.month == 12:
        end = datetime(dt.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(dt.year, dt.month + 1, 1, tzinfo=timezone.utc)
    return start, end

# --- Rules CRUD (minimal) ---
@router.post("/rules", response_model=CompensationRuleOut)
def upsert_rule(body: CompensationRuleIn, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    rule = (
        db.query(models.CompensationRule)
        .filter(models.CompensationRule.period == body.period)
        .one_or_none()
    )
    if rule is None:
        rule = models.CompensationRule(
            period=body.period,
            human_multiplier=body.human_multiplier,
            ai_multiplier=body.ai_multiplier,
            dpv_base=body.dpv_base,
        )
        db.add(rule)
    else:
        rule.human_multiplier = body.human_multiplier
        rule.ai_multiplier = body.ai_multiplier
        rule.dpv_base = body.dpv_base
    db.commit()
    db.refresh(rule)
    return CompensationRuleOut(
        id=rule.id,
        period=rule.period,
        human_multiplier=rule.human_multiplier,
        ai_multiplier=rule.ai_multiplier,
        dpv_base=rule.dpv_base,
    )

@router.get("/rules/{period}", response_model=CompensationRuleOut)
def get_rule(period: str, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    rule = (
        db.query(models.CompensationRule)
        .filter(models.CompensationRule.period == period)
        .one_or_none()
    )
    if not rule:
        raise HTTPException(404, "compensation rule not found")
    return CompensationRuleOut(
        id=rule.id,
        period=rule.period,
        human_multiplier=rule.human_multiplier,
        ai_multiplier=rule.ai_multiplier,
        dpv_base=rule.dpv_base,
    )

# --- Close & Settle (idempotent) ---
@router.post("/close-and-settle", response_model=PoolSummaryOut, summary="Close month and settle pool (idempotent)")
def close_and_settle(body: CloseAndSettleIn, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    start, end = month_bounds(body.period)

    # If already settled and not forcing, return existing summary
    existing = (
        db.query(models.Pool)
        .filter(models.Pool.period_month == body.period, models.Pool.settled == True)
        .one_or_none()
    )
    if existing and not body.force_recompute:
        return _pool_summary(existing.id, db)

    # If force, delete existing shares & pool for the period
    if existing and body.force_recompute:
        db.query(models.PoolShare).filter(models.PoolShare.pool_id == existing.id).delete()
        db.delete(existing)
        db.commit()

    # Fetch appreciation token counts per creator inside the month
    # effective_tokens = sum over tokens: multiplier (human or ai) per token's video
    # If no AI score row for a video, multiplier defaults to 1.0
    # 1) Raw token counts per (creator_id, video_id)
    Sub = (
        db.query(
            models.Video.creator_id.label("creator_id"),
            models.AppreciationToken.video_id.label("video_id"),
            func.count(models.AppreciationToken.token_id).label("tok_cnt"),
        )
        .join(models.Video, models.Video.id == models.AppreciationToken.video_id)
        .filter(
            models.AppreciationToken.used_at >= start,
            models.AppreciationToken.used_at < end,
        )
        .group_by(models.Video.creator_id, models.AppreciationToken.video_id)
        .subquery()
    )

    # 2) Join AI scores (optional)
    rows = (
        db.query(
            Sub.c.creator_id,
            Sub.c.video_id,
            Sub.c.tok_cnt,
            models.VideoAIScore.human_prob,
            models.VideoAIScore.ai_prob,
        )
        .outerjoin(models.VideoAIScore, models.VideoAIScore.video_id == Sub.c.video_id)
        .all()
    )

    # Resolve rule (or fallback)
    rule = (
        db.query(models.CompensationRule)
        .filter(models.CompensationRule.period == body.period)
        .one_or_none()
    )
    human_mul = rule.human_multiplier if rule else 1.2
    ai_mul = rule.ai_multiplier if rule else 0.7

    # Aggregate effective tokens per creator
    creator_buckets: Dict[int, Dict[str, float]] = {}
    for r in rows:
        mult = 1.0
        if r.human_prob is not None and r.ai_prob is not None:
            # choose multiplier by higher probability class
            mult = human_mul if (r.human_prob >= r.ai_prob) else ai_mul
        # if no score, mult stays 1.0
        d = creator_buckets.setdefault(r.creator_id, {"tok": 0.0, "eff": 0.0})
        d["tok"] += float(r.tok_cnt)
        d["eff"] += float(r.tok_cnt) * mult

    total_effective = sum(v["eff"] for v in creator_buckets.values())

    # Create pool
    pool = models.Pool(
        period_month=body.period,
        base_amount=body.base_amount,
        settled=True,
        settled_at=datetime.now(tz=timezone.utc),
        total_effective_tokens=total_effective,
    )
    db.add(pool)
    db.flush()  # get pool.id

    shares: List[models.PoolShare] = []
    for creator_id, agg in creator_buckets.items():
        share_pct = (agg["eff"] / total_effective) if total_effective > 0 else 0.0
        payout = round(body.base_amount * share_pct, 2)
        shares.append(
            models.PoolShare(
                pool_id=pool.id,
                creator_id=creator_id,
                token_count=int(agg["tok"]),
                effective_tokens=agg["eff"],
                share_pct=share_pct,
                payout_amount=payout,
            )
        )
    db.bulk_save_objects(shares)
    db.commit()

    return _pool_summary(pool.id, db)

def _pool_summary(pool_id: int, db: Session) -> PoolSummaryOut:
    pool = db.query(models.Pool).get(pool_id)
    if not pool:
        raise HTTPException(404, "pool not found")
    rows = (
        db.query(models.PoolShare)
        .filter(models.PoolShare.pool_id == pool_id)
        .order_by(models.PoolShare.payout_amount.desc())
        .all()
    )
    return PoolSummaryOut(
        pool_id=pool.id,
        period=pool.period_month,
        base_amount=pool.base_amount,
        total_effective_tokens=pool.total_effective_tokens,
        shares=[
            PoolShareOut(
                creator_id=r.creator_id,
                token_count=r.token_count,
                effective_tokens=r.effective_tokens,
                share_pct=r.share_pct,
                payout_amount=r.payout_amount,
            )
            for r in rows
        ],
    )

# --- GET summary (+ optional CSV) ---
@router.get("/{period}/summary", response_model=PoolSummaryOut)
def get_summary(
    period: str,
    format: Optional[str] = Query(None, pattern="^(csv)$"),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user),
):
    pool = (
        db.query(models.Pool)
        .filter(models.Pool.period_month == period, models.Pool.settled == True)
        .one_or_none()
    )
    if not pool:
        raise HTTPException(404, "pool not found for period")
    summary = _pool_summary(pool.id, db)

    if format == "csv":
        def _iter():
            yield "creator_id,token_count,effective_tokens,share_pct,payout_amount\n"
            for s in summary.shares:
                yield f"{s.creator_id},{s.token_count},{s.effective_tokens:.6f},{s.share_pct:.6f},{s.payout_amount:.2f}\n"
        return StreamingResponse(_iter(), media_type="text/csv")
    return summary
