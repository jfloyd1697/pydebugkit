from PyQt5 import QtWidgets

from debugkit.ui.persistence.settings import RecorderConfig
from debugkit.core.recorder import Recorder


class RecorderControl(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._recorder: Recorder = None

    def set_recorder(self, recorder):
        self._recorder = recorder

    def to_config(self):
        return RecorderConfig(
            enabled=self._recorder.is_running(),
            sample_interval=self.sample_interval,
            watched_keys=list(self._recorder.keys())
        )

    def from_config(self, config: RecorderConfig):
        self.sample_interval = config.sample_interval

        for key in config.watched_keys:
            self._recorder.watch(key)

        if config.enabled:
            self._recorder.start()