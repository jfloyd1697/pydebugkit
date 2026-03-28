from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Optional


# -------------------------------
# Plot Configuration
# -------------------------------

@dataclass
class PlotSeriesConfig(DataClassJsonMixin):
    key: str
    panel: str
    enabled: bool = True



@dataclass
class PlotPanelConfig(DataClassJsonMixin):
    name: str
    series: list[PlotSeriesConfig] = field(default_factory=list)


# -------------------------------
# Inspector State
# -------------------------------


@dataclass
class InspectorConfig(DataClassJsonMixin):
    checked_keys: list[str] = field(default_factory=list)
    expanded_keys: list[str] = field(default_factory=list)


# -------------------------------
# Recorder Settings
# -------------------------------


@dataclass
class RecorderConfig(DataClassJsonMixin):
    enabled: bool = True
    sample_interval: float = 0.1
    watched_keys: list[str] = field(default_factory=list)


# -------------------------------
# App Settings
# -------------------------------


@dataclass
class AppSettings(DataClassJsonMixin):
    autosave_enabled: bool = True
    autosave_interval_sec: int = 10
    last_file: Optional[str] = None


# -------------------------------
# Root App State
# -------------------------------


@dataclass
class AppState(DataClassJsonMixin):
    settings: AppSettings = field(default_factory=AppSettings)
    inspector: InspectorConfig = field(default_factory=InspectorConfig)
    plots: list[PlotPanelConfig] = field(default_factory=list)
    recorder: RecorderConfig = field(default_factory=RecorderConfig)