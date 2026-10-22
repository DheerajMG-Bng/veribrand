import time
from collections import defaultdict, deque
from threading import Lock
from datetime import datetime, timezone
from sqlalchemy import select, func
from ..models import AIUsage

_minute = defaultdict(deque)
_inflight = set()
_lock = Lock()

def used_today(db, model):
    midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return db.scalar(select(func.coalesce(func.sum(AIUsage.tokens), 0)).where(AIUsage.model == model, AIUsage.created_at >= midnight)) or 0

def minute_used(model):
    with _lock:
        queue = _minute[model]
        while queue and queue[0][0] < time.monotonic() - 60:
            queue.popleft()
        return sum(count for _, count in queue)

def state(db, model):
    if used_today(db, model) >= 180000:
        return 'exhausted'
    if minute_used(model) >= 6400 or model in _inflight:
        return 'busy'
    return 'ok'

def reserve(db, model):
    if state(db, model) != 'ok':
        return False
    with _lock:
        if model in _inflight:
            return False
        _inflight.add(model)
        return True

def release(model):
    with _lock:
        _inflight.discard(model)

def record(db, model, tokens):
    tokens = max(0, int(tokens))
    with _lock:
        _minute[model].append((time.monotonic(), tokens))
    db.add(AIUsage(model=model, tokens=tokens))
    db.flush()
