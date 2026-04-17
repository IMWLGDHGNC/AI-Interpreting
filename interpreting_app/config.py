from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MATERIALS_PATH = BASE_DIR / "data" / "materials.json"
HISTORY_PATH = BASE_DIR / "storage" / "history.json"
DATA_DIR = BASE_DIR / "data"

MODE_OPTIONS = ["双语转换", "源语重述"]
DIFFICULTY_OPTIONS = ["初级", "中级", "高级"]

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_TEXT_MODEL = "deepseek-chat"

SILICON_STT_ENDPOINT = "https://api.siliconflow.cn/v1/audio/transcriptions"
SILICON_STT_MODEL = "FunAudioLLM/SenseVoiceSmall"

TRANSLATION_DIRECTION_OPTIONS = ["英文 -> 中文", "中文 -> 英文"]
