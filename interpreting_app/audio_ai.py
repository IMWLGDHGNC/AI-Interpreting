from typing import Optional
from interpreting_app.config import DATA_DIR
import requests
import json


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
) -> str:
    headers = {"Authorization": f"Bearer {api_key}"}# Bearer认证方式，构造HTTP请求头
    files = {
        "file": (filename, file_bytes, guess_mime_type(filename, mime_type)),
        "model": (None, model),
    }
    
    resp = requests.post(endpoint, headers=headers, files=files, timeout=20)# 向语音转写API发送POST请求，包含认证头和文件数据，设置超时时间为60秒
    resp.raise_for_status() # 异常处理，如果响应状态码不是200-299，会抛出HTTPError异常
    body = resp.json() # 解析响应体为JSON格式，得到一个字典对象
    # with open(DATA_DIR / f"{filename}.json", "w") as f:
    #     json.dump(body, f)

    text = body.get("text", "") 
    if isinstance(text, str) and text.strip():
        return text.strip()

    # 兼容部分接口返回格式
    if isinstance(body.get("results"), list) and body["results"]:
        merged = " ".join(str(item.get("text", "")) for item in body["results"])
        if merged.strip():
            return merged.strip()

    raise ValueError(f"语音转写返回无法解析：{body}")
