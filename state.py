"""State sederhana berbasis JSON file — dipakai untuk dedupe threshold alert
supaya bot tidak spam alert berulang untuk breach yang sama."""
import json
import os
from datetime import datetime, timezone

import config


def _load() -> dict:
    if not os.path.exists(config.STATE_FILE):
        return {}
    try:
        with open(config.STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(state: dict) -> None:
    with open(config.STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def should_alert(coin_id: str, direction: str) -> bool:
    """direction: 'up' atau 'down'. Return True kalau belum pernah alert untuk
    coin+direction ini dalam ALERT_COOLDOWN_HOURS terakhir."""
    state = _load()
    key = f"{coin_id}:{direction}"
    last = state.get(key)
    if not last:
        return True
    last_dt = datetime.fromisoformat(last)
    elapsed_hours = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
    return elapsed_hours >= config.ALERT_COOLDOWN_HOURS


def mark_alerted(coin_id: str, direction: str) -> None:
    state = _load()
    key = f"{coin_id}:{direction}"
    state[key] = datetime.now(timezone.utc).isoformat()
    _save(state)
