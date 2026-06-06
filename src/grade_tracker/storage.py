import json
from pathlib import Path

DATA_FILE = Path.home() / ".grade-tracker.json"


def load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"courses": {}}


def save(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2))
