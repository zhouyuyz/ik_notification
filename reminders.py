from __future__ import annotations
import datetime as dt
from dataclasses import dataclass
from typing import Dict, Tuple

from notifier import notify, NotifyConfig, EVENT_ICON

@dataclass
class ReminderSpec:
    hour: int
    minute: int
    title: str
    body: str

def _now_local() -> dt.datetime:
    # Use system local time on the machine running the program
    return dt.datetime.now()

def should_fire(last_fired: Dict[str, str], key: str, now: dt.datetime) -> bool:
    # fire once per day per key
    today = now.strftime("%Y-%m-%d")
    return last_fired.get(key) != today

def mark_fired(last_fired: Dict[str, str], key: str, now: dt.datetime) -> None:
    last_fired[key] = now.strftime("%Y-%m-%d")

def run_time_reminders(last_fired: Dict[str, str], cfg: NotifyConfig) -> None:
    now = _now_local()
    specs = [
        ReminderSpec(6, 30, f"{EVENT_ICON.get('INFO','🟡')} 开盘提醒", "前15分钟观察，不开仓。只做结构识别/方向确认。"),
        ReminderSpec(9, 30, f"{EVENT_ICON.get('INFO','🟡')} 半程提醒", "交易时间过半：只做A+机会，减少追单。"),
        ReminderSpec(11, 0, f"{EVENT_ICON.get('INFO','🟡')} 尾盘提醒", "11am后尾盘波动可能开始：注意快速拉扯与假突破。"),
    ]
    for i, sp in enumerate(specs, start=1):
        key = f"reminder_{i}"
        if now.hour == sp.hour and now.minute == sp.minute and should_fire(last_fired, key, now):
            notify(sp.title, sp.body, cfg)
            mark_fired(last_fired, key, now)
