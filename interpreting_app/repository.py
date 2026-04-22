import json
import random
from typing import Dict, List, Optional

from interpreting_app.config import HISTORY_PATH, MATERIALS_PATH, SPIDER_PATH, NEWS_URL


def ensure_storage() -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text("[]", encoding="utf-8")


def load_materials() -> Dict[str, List[Dict]]:
    return json.loads(MATERIALS_PATH.read_text(encoding="utf-8"))


def load_history() -> List[Dict]:
    ensure_storage()
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [] # 返回空列表


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
    material_type:str,
    used: Optional[Dict[str, List[int]]] = None
) -> Optional[Dict]:
    candidates = NEWS_URL.copy() if material_type == "news" else []
    if not candidates:
        return None
    if used is not None:
        used_flags = used.get(material_type, [])
        for index, url in enumerate(candidates):
            if index < len(used_flags) and used_flags[index] == 1:
                candidates.remove(url)
    if not candidates:
        return None
    picked = random.choice(candidates) if candidates else None
    if picked and used is not None:
        index = NEWS_URL.index(picked)
        used.setdefault(material_type, [0] * len(NEWS_URL))
        used[material_type][index] = 1
    return picked

