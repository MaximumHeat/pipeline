class CritiqueAccumulator:
    def __init__(self):
        self._history: list[str] = []

    def append(self, critique_text: str):
        cleaned = critique_text.strip().strip('"').strip("'")
        if cleaned:
            self._history.append(cleaned)

    def build_telemetry_block(self) -> str:
        if not self._history:
            return ""
        lines = ["### HISTORICAL CRITIQUE TELEMETRY LOG",
                 "The following structural corrections were flagged in previous execution attempts. "
                 "You MUST adapt your response to solve these errors and prevent failure repetition:"]
        for i, entry in enumerate(self._history, 1):
            lines.append(f"- Iteration {i} Failure Vector: {entry}")
        return "\n".join(lines)

    @property
    def history(self) -> list[str]:
        return list(self._history)

    def clear(self):
        self._history.clear()
