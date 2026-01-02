from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

@dataclass
class SessionParams:
    day_type: str = "RANGE"      # TREND or RANGE
    bias: str = "NEUTRAL"        # LONG / SHORT / NEUTRAL
    y_high: float = 0.0
    y_low: float = 0.0
    y_close: float = 0.0
    pred_high_range: List[float] = None
    pred_low_range: List[float] = None

    open15_setup: str = "NO_TRADE"       # TREND_SETUP / RANGE_SETUP / NO_TRADE
    open15_direction: str = "WAIT"       # LONG / SHORT / WAIT
    break_level: float = 0.0
    fail_level: float = 0.0
    target_zone: List[float] = None

    notes: str = ""
    updated_at: str = ""

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SessionParams":
        return SessionParams(
            day_type=str(d.get("day_type", "RANGE")).upper(),
            bias=str(d.get("bias", "NEUTRAL")).upper(),
            y_high=float(d.get("y_high", 0.0) or 0.0),
            y_low=float(d.get("y_low", 0.0) or 0.0),
            y_close=float(d.get("y_close", 0.0) or 0.0),
            pred_high_range=list(d.get("pred_high_range", [0, 0])),
            pred_low_range=list(d.get("pred_low_range", [0, 0])),
            open15_setup=str(d.get("open15_setup", "NO_TRADE")).upper(),
            open15_direction=str(d.get("open15_direction", "WAIT")).upper(),
            break_level=float(d.get("break_level", 0.0) or 0.0),
            fail_level=float(d.get("fail_level", 0.0) or 0.0),
            target_zone=list(d.get("target_zone", [0, 0])),
            notes=str(d.get("notes", "")),
            updated_at=str(d.get("updated_at", "")),
        )

def load_params(path: str = "session_params.json") -> SessionParams:
    p = Path(path)
    if not p.exists():
        return SessionParams(pred_high_range=[0,0], pred_low_range=[0,0], target_zone=[0,0])
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        sp = SessionParams.from_dict(d)
        if sp.pred_high_range is None: sp.pred_high_range = [0,0]
        if sp.pred_low_range is None: sp.pred_low_range = [0,0]
        if sp.target_zone is None: sp.target_zone = [0,0]
        return sp
    except Exception:
        return SessionParams(pred_high_range=[0,0], pred_low_range=[0,0], target_zone=[0,0])
