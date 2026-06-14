from typing import Optional
from interpreting_app.config import DATA_DIR
import re
import requests
import json


# SenseVoiceSmall 情感标签格式：<|HAPPY|>、<|SAD|> 等
_EMOTION_TAG_RE = re.compile(r"<\|[A-Za-z_]+\|>")

# emoji Unicode 区间（覆盖常见表情符号、杂项符号、增补符号）
_EMOJI_RE = re.compile(
    "[\U0001F600-\U0001F64F"   # 表情符号
    "\U0001F300-\U0001F5FF"   # 杂项符号及象形文字
    "\U0001F680-\U0001F6FF"   # 交通与地图符号
    "\U0001F1E0-\U0001F1FF"   # 国旗（区域指示符）
    "\U00002600-\U000027BF"   # 杂项符号
    "\U0000FE00-\U0000FE0F"   # 变体选择器
    "\U0000200D"              # 零宽连字
    "]+",
    flags=re.UNICODE,
)


def _strip_emotion_tags(text: str) -> str:
    """移除 SenseVoiceSmall 模型输出的情感标签和表情符号。"""
    text = _EMOTION_TAG_RE.sub("", text)    # 去掉 <|HAPPY|> 等
    text = _EMOJI_RE.sub("", text)          # 去掉表情符号
    # 压缩多余空白
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def guess_mime_type(filename: str, fallback: Optional[str] = None) -> str:
    if fallback:
        return fallback

    lower = (filename or "").lower()
    if lower.endswith(".wav"):
        return "audio/wav"
    if lower.endswith(".mp3"):
        return "audio/mpeg"
    if lower.endswith(".m4a"):
        return "audio/mp4"
    if lower.endswith(".mp4"):
        return "video/mp4"
    return "application/octet-stream"


def transcribe_audio_bytes(
    api_key: str, #api
    endpoint: str, #api端点url
    model: str, #使用的模型名称
    file_bytes: bytes, #原始字节数据
    filename: str, #文件名
    mime_type: Optional[str] = None,#mime类型
    language: Optional[str] = None,  # 强制指定音频语言，"en" / "zh" / None=自动检测
) -> str:
    if not api_key or not api_key.strip():
        raise ValueError(
            "SiliconFlow API Key 不能为空。请在左侧栏填写有效的 API Key。\n"
            "可前往 https://siliconflow.cn 免费注册获取。"
        )
    headers = {"Authorization": f"Bearer {api_key}"}# Bearer认证方式，构造HTTP请求头
    files: dict = {
        "file": (filename, file_bytes, guess_mime_type(filename, mime_type)),
        "model": (None, model),
    }
    if language:
        files["language"] = (None, language)
    
    resp = requests.post(endpoint, headers=headers, files=files, timeout=20)# 向语音转写API发送POST请求，包含认证头和文件数据，设置超时时间为60秒
    resp.raise_for_status() # 异常处理，如果响应状态码不是200-299，会抛出HTTPError异常
    body = resp.json() # 解析响应体为JSON格式，得到一个字典对象
    # with open(DATA_DIR / f"{filename}.json", "w") as f:
    #     json.dump(body, f)

    text = body.get("text", "")
    if isinstance(text, str) and text.strip():
        return _strip_emotion_tags(text)

    # 兼容部分接口返回格式
    if isinstance(body.get("results"), list) and body["results"]:
        merged = " ".join(str(item.get("text", "")) for item in body["results"])
        if merged.strip():
            return _strip_emotion_tags(merged)

    raise ValueError(f"语音转写返回无法解析：{body}")
