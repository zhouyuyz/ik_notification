from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

from position import PositionState

def load_state(path: str, default_long: PositionState, default_short: PositionState) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"long": default_long.to_dict(), "short": default_short.to_dict()}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if "long" not in data:
            data["long"] = default_long.to_dict()
        if "short" not in data:
            data["short"] = default_short.to_dict()
        return data
    except Exception:
        return {"long": default_long.to_dict(), "short": default_short.to_dict()}

def save_state(path: str, data: Dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_position(data: Dict[str, Any], side: str) -> PositionState:
    return PositionState.from_dict(data.get(side, {}))

def set_position(data: Dict[str, Any], side: str, pos: PositionState) -> None:
    data[side] = pos.to_dict()
