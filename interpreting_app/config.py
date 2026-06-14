from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MATERIALS_PATH = BASE_DIR / "data" / "materials.json"
HISTORY_PATH = BASE_DIR / "storage" / "history.json"
DATA_DIR = BASE_DIR / "data"
SPIDER_PATH = BASE_DIR / "third_party" / "Spider-for-Bilibili"

MODE_OPTIONS = ["双语转换", "源语重述"]
DIFFICULTY_OPTIONS = ["初级", "中级", "高级"]
CLASS = ["news", "daily English"]

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

DAILY_ENGLISH_URL = [
    # 朗文场景英语系列 —— 日常生活场景，每集3-8分钟，四步跟读训练法
    "https://www.bilibili.com/video/BV1FNDaYtEmA",   # Returning Home 回家
    "https://www.bilibili.com/video/BV1jYDJYSEJ6",   # Walking Somewhere 步行
    "https://www.bilibili.com/video/BV1yKDiYGEwU",   # Making a Salad 做沙拉
    "https://www.bilibili.com/video/BV1r3UYYsEAX",   # Going to Bed 上床睡觉
    "https://www.bilibili.com/video/BV1mA1NYLEGP",   # Brushing Teeth 刷牙剔牙
    "https://www.bilibili.com/video/BV1WWSSY5Emw",   # Driving Along 开车
    # 场景训练合集 & 口语专项
    "https://www.bilibili.com/video/BV1jR4y1F7jK",   # 朗文场景英语·训练版合集（61集）
    "https://www.bilibili.com/video/BV19zWmzeE5n",   # 50句超高频英语口语 场景对话
    "https://www.bilibili.com/video/BV1KR4y187Sf",   # 30天听力飞跃之旅（初/中/高级）
    "https://www.bilibili.com/video/BV1Ni4y1k7sm",   # 场景跟读训练版（跟读·训练版）
]

# 类别名 -> URL 列表的统一注册表，select_material 会从这里取素材
MATERIAL_URLS = {
    "news": NEWS_URL,
    "daily English": DAILY_ENGLISH_URL,
}