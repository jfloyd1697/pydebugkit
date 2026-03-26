from dataclasses import dataclass
from typing import Any, Callable, Optional

@dataclass
class DebugSetting:
    key: str
    name: str
    type: Optional[type]
    getter: Callable[[], Any]
    setter: Optional[Callable[[Any], None]]
    options: Optional[list] = None
    readonly: bool = False
    min: Optional[float] = None
    max: Optional[float] = None
    group: Optional[str] = None
    level: str = "basic"
    scope: str = "instance"
    trace: bool = False
