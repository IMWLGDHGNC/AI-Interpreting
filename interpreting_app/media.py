from pathlib import Path
from typing import Tuple

import streamlit as st


def detect_audio_mime(payload: bytes, suffix: str) -> str:
    # B站下载的音轨常是 MP4 容器（m4s/m4a），即使文件名被写成 .mp3。
    if len(payload) > 8 and payload[4:8] == b"ftyp":
        return "audio/mp4"
    if suffix in {".wav"}:
        return "audio/wav"
    return "audio/mpeg"


def load_audio_payload(audio_path: str | Path) -> Tuple[bytes, str, str]:
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"音频文件不存在：{path}")

    payload = path.read_bytes()
    mime = detect_audio_mime(payload, path.suffix.lower())
    return payload, mime, path.name


def render_local_audio(audio_path: str | Path) -> None:
    try:
        payload, mime, name = load_audio_payload(audio_path)
    except FileNotFoundError as exc:
        st.warning(str(exc))
        return

    st.audio(payload, format=mime)
    st.caption(f"音频文件：{name} | 格式：{mime}")
