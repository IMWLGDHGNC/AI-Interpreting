from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MATERIALS_PATH = BASE_DIR / "data" / "materials.json"
HISTORY_PATH = BASE_DIR / "storage" / "history.json"
DATA_DIR = BASE_DIR / "data"
SPIDER_PATH = BASE_DIR / "third_party" / "Spider-for-Bilibili"

MODE_OPTIONS = ["双语转换", "源语重述"]
DIFFICULTY_OPTIONS = ["初级", "中级", "高级"]
CLASS = ["news"]

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_TEXT_MODEL = "deepseek-chat"

SILICON_STT_ENDPOINT = "https://api.siliconflow.cn/v1/audio/transcriptions"
SILICON_STT_MODEL = "FunAudioLLM/SenseVoiceSmall"

TRANSLATION_DIRECTION_OPTIONS = ["英文 -> 中文", "中文 -> 英文"]

MP3_PATH= DATA_DIR / "mp3"

NEWS_URL = [
    "https://www.bilibili.com/video/BV1grsaeaEhM",
    "https://www.bilibili.com/video/BV1AssmebEJT",
    "https://www.bilibili.com/video/BV1VJtkeMEgd",
    "https://www.bilibili.com/video/BV1GCtneGELh",
    "https://www.bilibili.com/video/BV1Q7t7eaEmh",
    "https://www.bilibili.com/video/BV1zgtYepE84",
    "https://www.bilibili.com/video/BV1iGWBeQEqe",
    "https://www.bilibili.com/video/BV1FE421A7wv",
    "https://www.bilibili.com/video/BV1zn4y1X76t",
    "https://www.bilibili.com/video/BV1cw4m1e7y6"
]