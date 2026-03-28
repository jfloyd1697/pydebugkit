from .settings import AppState


class PersistenceManager:
    """
    Handles saving and loading the entire DebugKit state.
    """

    def __init__(self):
        self.current_file = None

    # -------------------------------
    # Save / Load
    # -------------------------------
    def save(self, state: AppState, filepath: str):
        with open(filepath, "w") as f:
            f.write(state.to_json(indent=2))
        self.current_file = filepath

    def load(self, filepath: str) -> AppState:
        with open(filepath, "r") as f:
            data = f.read()
        state = AppState.from_json(data)
        self.current_file = filepath
        return state

    # -------------------------------
    # Autosave
    # -------------------------------
    def autosave(self, state: AppState):
        if self.current_file:
            self.save(state, self.current_file)