from typing import Dict, List

import streamlit as st

from interpreting_app.audio_ai import transcribe_audio_bytes
from interpreting_app.config import (
    DEEPSEEK_BASE_URL,
    DEEPSEEK_TEXT_MODEL,
    SILICON_STT_ENDPOINT,
    SILICON_STT_MODEL,
)
from interpreting_app.llm import normalize_api_key, sanitize_error, test_text_model


def render_sidebar() -> Dict:
    st.sidebar.header("模型配置")
    st.sidebar.caption("翻译任务：DeepSeek；语音转写：SiliconFlow")

    st.sidebar.subheader("翻译模型（DeepSeek）")
    deepseek_api_key = st.sidebar.text_input(
        "DeepSeek API Key",
        type="password",
        help="用于文本翻译与源语重述",
    )
    deepseek_base_url = st.sidebar.text_input("DeepSeek Base URL", value=DEEPSEEK_BASE_URL)
    deepseek_model = st.sidebar.text_input("DeepSeek Model", value=DEEPSEEK_TEXT_MODEL)

    st.sidebar.subheader("语音模型（SiliconFlow）")
    api_key = st.sidebar.text_input(
        "SiliconFlow API Key",
        type="password",
        help="必须填写 key，系统不会硬编码密钥",
    )
    stt_endpoint = st.sidebar.text_input("语音转写 Endpoint", value=SILICON_STT_ENDPOINT)
    stt_model = st.sidebar.text_input("语音转写模型", value=SILICON_STT_MODEL)

    if st.sidebar.button("测试翻译模型连通性", use_container_width=True):
        try:
            reply = test_text_model(
                api_key=normalize_api_key(deepseek_api_key),
                base_url=deepseek_base_url.strip(),
                model=deepseek_model.strip(),
            )
            st.session_state["text_test_reply"] = reply
            st.sidebar.success("模型连通性正常。")
        except Exception as exc:
            st.sidebar.error(f"连通性测试失败：{sanitize_error(exc, deepseek_api_key)}")

    if st.sidebar.button("测试语音模型连通性", use_container_width=True):
        uploaded = st.session_state.get("uploaded_audio_for_test")
        if not uploaded:
            st.sidebar.warning("请先在主界面上传一个音频文件，再测试语音模型。")
        else:
            try:
                transcript = transcribe_audio_bytes(
                    api_key=normalize_api_key(api_key),
                    endpoint=stt_endpoint.strip(),
                    model=stt_model.strip(),
                    file_bytes=uploaded["bytes"],
                    filename=uploaded["name"],
                    mime_type=uploaded.get("type"),
                )
                st.session_state["stt_test_reply"] = transcript
                st.sidebar.success("语音模型连通性正常。")
            except Exception as exc:
                st.sidebar.error(f"语音连通性测试失败：{sanitize_error(exc, api_key)}")

    st.sidebar.divider()
    st.sidebar.caption("历史记录")
    if st.sidebar.button("查看历史记录", use_container_width=True):
        st.session_state["show_history"] = True

    return {
        "deepseek_api_key": deepseek_api_key,
        "deepseek_base_url": deepseek_base_url,
        "deepseek_model": deepseek_model,
        "silicon_api_key": api_key,
        "stt_endpoint": stt_endpoint,
        "stt_model": stt_model,
    }


def render_history_panel(records: List[Dict]) -> None:
    st.subheader("训练历史")
    if not records:
        st.info("暂无历史记录。")
        return

    for record in reversed(records[-50:]):
        with st.expander(
            f"{record['time']} | {record['mode']} | {record['difficulty']} | {record['material_id']}"
        ):
            st.write(f"主题：{record.get('topic', '-')}")
            st.write(f"源语：{record.get('source_text', '')}")
            st.write(f"参考答案：{record.get('reference_answer', '')}")
            if record.get("llm_answer"):
                st.write(f"{record.get('model_name', 'unknown model')}答案：{record['llm_answer']}")
            else:
                st.write("未生成模型答案。")
        if record.get("user_source", False):
            with st.expander(
                f"{record['time']} | {record['mode']} | {record['name']}"):
                st.write(f"源语：{record.get('source_text', '')}")
                if record.get("llm_answer"):
                    st.write(f"{record.get('model_name', 'unknown model')}答案：{record['llm_answer']}")
                else:
                    st.write("未生成模型答案。")
