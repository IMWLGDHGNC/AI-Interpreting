import json
import random
from typing import Dict, List, Optional

from interpreting_app.config import HISTORY_PATH, MATERIALS_PATH, MATERIAL_URLS, SPIDER_PATH


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
    material_type: str,
    used: Optional[Dict[str, List[int]]] = None
) -> Optional[str]:
    """从指定类别随机选一个未用过的素材 URL。

    返回值含义：
    - 正常 URL 字符串：选中成功
    - ``None``：该类别没有配置任何素材
    - ``""``（空字符串）：该类别素材已全部用完
    """
    url_list = MATERIAL_URLS.get(material_type, [])
    if not url_list:
        return None  # 该类别没有任何素材

    candidates = url_list.copy()
    if used is not None:
        used_flags = used.get(material_type, [])
        # 安全移除已用项（倒序遍历避免索引偏移）
        for index in sorted(
            [i for i in range(min(len(candidates), len(used_flags)))
             if used_flags[i] == 1],
            reverse=True,
        ):
            if index < len(candidates):
                candidates.pop(index)

    if not candidates:
        return ""  # 全部用完

    picked = random.choice(candidates)
    if picked and used is not None:
        index = url_list.index(picked)
        used.setdefault(material_type, [0] * len(url_list))
        used[material_type][index] = 1
    return picked

