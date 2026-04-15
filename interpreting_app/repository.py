import json
import random
from typing import Dict, List, Optional

from interpreting_app.config import HISTORY_PATH, MATERIALS_PATH


def ensure_storage() -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text("[]", encoding="utf-8")


def load_materials() -> Dict[str, List[Dict]]:
    return json.loads(MATERIALS_PATH.read_text(encoding="utf-8"))


def load_history() -> List[Dict]:
    ensure_storage()
    return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))


def save_history(records: List[Dict]) -> None:
    HISTORY_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_history(entry: Dict) -> None:
    records = load_history()
    records.append(entry)
    save_history(records)


def select_material(
    materials: Dict[str, List[Dict]],
    mode: str,
    difficulty: str,
) -> Optional[Dict]:
    candidates = [m for m in materials.get(mode, []) if m.get("difficulty") == difficulty]
    if not candidates:
        return None
    return random.choice(candidates)
