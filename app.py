from datetime import datetime

import streamlit as st

from interpreting_app.audio_ai import transcribe_audio_bytes
from interpreting_app.config import (
    DIFFICULTY_OPTIONS,
    MODE_OPTIONS,
    TRANSLATION_DIRECTION_OPTIONS,
    SILICON_STT_MODEL,
    DEEPSEEK_TEXT_MODEL,
    NEWS_URL,
    MP3_PATH,
    CLASS
)
from interpreting_app.llm import (
    normalize_api_key,
    paraphrase_text,
    sanitize_error,
    translate_text,
    taking_notes_text,
)
from interpreting_app.media import render_local_audio
from interpreting_app.repository import (
    ensure_storage,
    load_history,
    select_material,
)
from interpreting_app.ui import render_history_panel, render_sidebar
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SPIDER_DIR = PROJECT_ROOT / "third_party" / "Spider-for-Bilibili"
if SPIDER_DIR.exists() and str(SPIDER_DIR) not in sys.path:
    sys.path.insert(0, str(SPIDER_DIR))

from get_download import (  # type: ignore[import-not-found]
    download_subtitle,
    download_video,
    get_response,
    get_subtitle_info,
    get_video_audio_info,
)
from headers_test import get_headers  # type: ignore[import-not-found]

def pull_url(url: str) -> str:
    tuple_1 = get_headers()
    response = get_response(url=url, cookies=tuple_1[0], headers=tuple_1[1])
    st.write("原链接:", url)
    info_tuple = get_video_audio_info(response)
    audio_name = info_tuple[2] + ".mp3"
    audio_path = MP3_PATH / audio_name
    if audio_path.exists():
        st.write("音频已存在，直接播放")
    else:
        download_video(info_tuple)
        st.write("视频下载完成")
    return audio_name



def sanitize_with_keys(exc: Exception, keys: list[str]) -> str:
    msg = str(exc)
    for key in keys:
        msg = sanitize_error(Exception(msg), key)
    return msg


def main() -> None:
    st.set_page_config(page_title="AI+口译训练平台", layout="wide")
    st.title("AI+口译训练平台")
    st.markdown("这是一个利用大模型辅助大学生进行英语口译训练的工具，它调用两个模型接口：DeepSeek 生成文本答案，Silicon STT 进行语音转写。")
    st.markdown("它支持从素材库中抓取训练素材进行练习；也支持自主上传语音进行练习。")
    st.markdown("大模型可以实现转写、翻译、重述和生成口译笔记的功能。")
    st.caption("开发者正在想办法压低成本。")
    

    ensure_storage()
    model_cfg = render_sidebar()
    used = st.session_state.setdefault("used", {"news": [0] * len(NEWS_URL)})
    top_left, top_right = st.columns([3, 1])

    if st.session_state.get("show_history",False):
        render_history_panel(load_history())
        if st.button("关闭历史记录"):
            st.session_state["show_history"] = False
        st.divider()

    tab_train, tab_upload, tab_notes = top_left.tabs(["随机素材训练", "上传音频训练", "口译笔记训练"])

    with tab_train:
        material_type = st.selectbox("素材类别", CLASS)
        st.caption("系统将从素材库中抓取一个英语素材进行训练。")
        if st.button("加载新素材", type="primary"):
            picked = select_material(material_type, used)
            if not picked:
                st.warning("没有更多未使用的素材了，已重置使用状态，将生成用过的素材。")
                st.session_state["used"] = {"news": [0] * len(NEWS_URL)}
                picked = select_material(material_type, st.session_state["used"])
            if picked:
                st.session_state["current_material"] = picked
                audio_name = pull_url(picked)
                audio_path = MP3_PATH / audio_name
                if audio_path.exists():
                    payload_bytes = audio_path.read_bytes()
                    audio_mime = "audio/mp4" if len(payload_bytes) > 8 and payload_bytes[4:8] == b"ftyp" else "audio/mpeg"
                    st.session_state["train_audio_payload"] = {
                        "bytes": payload_bytes,
                        "name": audio_name,
                        "type": audio_mime,
                    }
        current_material = st.session_state.get("current_material")
        if current_material:
            st.info(f"当前素材：{current_material}")

        payload = st.session_state.get("train_audio_payload")
        if payload:
            st.markdown("### 训练音频")
            st.audio(payload["bytes"], format=payload.get("type", "audio/mpeg"))
            st.caption(f"文件：{payload.get('name', 'unknown')}")

        if payload and st.button("Magic Button", type="primary"):
            st.caption("伟大的大模型将一站式处理转写+翻译+源语重述+口译笔记，坐享其成吧～")
            st.markdown("### 转写文本")
            stt_key = normalize_api_key(model_cfg["silicon_api_key"])
            transcript = transcribe_audio_bytes(
                api_key=stt_key,
                endpoint=model_cfg["stt_endpoint"],
                model=model_cfg["stt_model"],
                file_bytes=payload["bytes"],
                filename=payload["name"],
                mime_type=payload["type"],
            )
            st.session_state["uploaded_transcript"] = transcript
            st.write(transcript)
            st.markdown("### 翻译")
            direction = TRANSLATION_DIRECTION_OPTIONS[0]
            translated = translate_text(
                api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                base_url=model_cfg["deepseek_base_url"],
                model=model_cfg["deepseek_model"],
                text=transcript,
                direction=direction,
            )
            st.write(translated)
            st.markdown("### 重述")
            language = "English"
            paraphrased = paraphrase_text(
                api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                base_url=model_cfg["deepseek_base_url"],
                model=model_cfg["deepseek_model"],
                text=transcript,
                language=language,
            )
            st.session_state["paraphrased"] = paraphrased
            st.write(paraphrased)
            st.markdown("### 生成口译笔记")
            language = "English"
            notes = taking_notes_text(
                api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                base_url=model_cfg["deepseek_base_url"],
                model=model_cfg["deepseek_model"],
                text=transcript,
                language=language,
            )
            st.write(notes)

    with tab_upload:
        st.subheader("上传音频 -> 语音转文字 -> 翻译/重述/口译笔记")
        uploaded = st.file_uploader(
            "上传音频文件（支持 mp3/wav/m4a/mp4）",
            type=["mp3", "wav", "m4a", "mp4"],
            key="audio_uploader_main",
        )

        if uploaded:
            file_bytes = uploaded.getvalue() # 获得原始字节数据
            st.session_state["uploaded_audio_for_test"] = {
                "bytes": file_bytes,
                "name": uploaded.name,
                "type": uploaded.type,
            }
            st.audio(file_bytes)

            direction = st.selectbox("翻译方向", TRANSLATION_DIRECTION_OPTIONS)
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                run_stt = st.button("1) 仅转写")
            with col2:
                run_translate = st.button("2) 转写并翻译")
            with col3:
                run_paraphrase = st.button("3) 转写并重述")
            with col4:
                run_notes = st.button("4) 转写并生成口译笔记")

            if run_stt or run_translate or run_paraphrase or run_notes:
                try:
                    key = normalize_api_key(model_cfg["silicon_api_key"])
                    transcript = transcribe_audio_bytes(
                        api_key=key,
                        endpoint=model_cfg["stt_endpoint"],
                        model=model_cfg["stt_model"],
                        file_bytes=file_bytes,
                        filename=uploaded.name,
                        mime_type=uploaded.type,
                    )
                    st.session_state["uploaded_transcript"] = transcript
                    st.markdown("### 转写文本")
                    st.write(transcript)

                    if run_translate:
                        translated = translate_text(
                            api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                            base_url=model_cfg["deepseek_base_url"],
                            model=model_cfg["deepseek_model"],
                            text=transcript,
                            direction=direction,
                        )
                        st.markdown("### 翻译结果")
                        st.write(translated)

                    if run_paraphrase:
                        language = "English" if direction == "英文 -> 中文" else "中文"
                        paraphrased = paraphrase_text(
                            api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                            base_url=model_cfg["deepseek_base_url"],
                            model=model_cfg["deepseek_model"],
                            text=transcript,
                            language=language,
                        )
                        st.markdown("### 重述结果")
                        st.write(paraphrased)
                    
                    if run_notes:
                        language = "English" if direction == "英文 -> 中文" else "中文"
                        notes = taking_notes_text(
                            api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                            base_url=model_cfg["deepseek_base_url"],
                            model=model_cfg["deepseek_model"],
                            text=transcript,
                            language=language,
                        )
                        st.markdown("### 口译笔记")
                        st.write(notes)
                except Exception as exc:
                    masked = sanitize_with_keys(
                        exc,
                        [model_cfg["silicon_api_key"], model_cfg["deepseek_api_key"]],
                    )
                    st.error(f"处理失败：{masked}")
        else:
            st.info("先上传音频后再执行转写/翻译。")

        # if st.button("保存历史记录",use_container_width=True):
        #     if not st.session_state.get("uploaded_transcript"):
        #         st.warning("没有转写文本可保存，请先执行转写。")

        if st.session_state.get("text_test_reply"):
            st.caption(f"最近一次文本连通性测试返回：{st.session_state['text_test_reply']}")
        if st.session_state.get("stt_test_reply"):
            st.caption(f"最近一次语音连通性测试转写：{st.session_state['stt_test_reply'][:120]}")

    st.markdown("---")
    st.caption("© 2026 Daniel")
    st.caption("Design, implementation, testing, and deployment")


if __name__ == "__main__":
    main()
