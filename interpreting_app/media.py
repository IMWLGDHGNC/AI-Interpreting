import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components


@st.cache_data(show_spinner=False)
def fetch_media_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=18) as resp:
        return resp.read()


def parse_bilibili_embed(url: str) -> Optional[str]:
    if "bilibili.com/video/" not in url:
        return None

    match = re.search(r"BV[0-9A-Za-z]+", url)
    if not match:
        return None

    bvid = match.group(0)
    return f"https://player.bilibili.com/player.html?bvid={bvid}&page=1"


def render_media(url: str) -> None:
    if not url:
        st.warning("当前素材没有音频链接。")
        return

    embed_url = parse_bilibili_embed(url)
    if embed_url:
        components.iframe(embed_url, height=460, scrolling=False)
        st.markdown(f"[打开原始媒体链接]({url})")
        return

    lower = url.lower()
    is_video = lower.endswith(".mp4") or "ted.com/talks/" in lower

    try:
        media_bytes = fetch_media_bytes(url)
        if is_video:
            st.video(media_bytes)
        else:
            st.audio(media_bytes)
        st.caption("若播放卡顿，可点击下方原始链接在新标签页打开。")
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        st.warning(f"媒体加载失败：{exc}")
        if is_video:
            st.video(url)
        else:
            st.audio(url)

    st.markdown(f"[打开原始媒体链接]({url})")


def render_local_audio(audio_path: str | Path) -> None:
    path = Path(audio_path)
    if not path.exists():
        st.warning(f"音频文件不存在：{path}")
        return

    st.audio(str(path))
    st.caption(f"音频文件：{path.name}")
