from datetime import datetime

import streamlit as st

from interpreting_app.audio_ai import transcribe_audio_bytes
from interpreting_app.config import (
    DIFFICULTY_OPTIONS,
    MODE_OPTIONS,
    TRANSLATION_DIRECTION_OPTIONS,
)
from interpreting_app.llm import (
    generate_llm_answer,
    normalize_api_key,
    paraphrase_text,
    sanitize_error,
    translate_text,
)
from interpreting_app.media import render_media
from interpreting_app.repository import (
    append_history,
    ensure_storage,
    load_history,
    load_materials,
    select_material,
)
from interpreting_app.ui import render_history_panel, render_sidebar


def main() -> None:
    st.set_page_config(page_title="AI+口译训练平台", layout="wide")
    st.title("AI+口译训练平台（课程作业版）")
    st.caption("支持：素材训练、上传音频转写、中英互译、源语重述与历史记录")

    ensure_storage()
    materials = load_materials()
    model_cfg = render_sidebar()

    top_left, top_right = st.columns([3, 1])
    with top_right:
        if st.button("打开历史记录", use_container_width=True):
            st.session_state["show_history"] = True

    if st.session_state.get("show_history"):
        render_history_panel(load_history())
        if st.button("关闭历史记录"):
            st.session_state["show_history"] = False
        st.divider()

    tab_train, tab_upload = top_left.tabs(["素材训练", "上传音频训练"])

    with tab_train:
        mode = st.selectbox("选择功能", MODE_OPTIONS)
        difficulty = st.selectbox("选择难度", DIFFICULTY_OPTIONS)

        if st.button("加载新素材", type="primary"):
            picked = select_material(materials, mode, difficulty)
            st.session_state["current_material"] = picked
            st.session_state["llm_answer"] = ""

        current = st.session_state.get("current_material")
        if not current:
            st.info("请先选择功能和难度，再点击“加载新素材”。")
        else:
            st.subheader("当前训练素材")
            st.write(f"题目编号：{current['id']}")
            st.write(f"来源：{current.get('source', '-')}")
            st.write(f"主题：{current.get('topic', '-')}")
            st.write(f"语速提示：{current.get('speed_hint', '-')}")

            if current.get("audio_url"):
                render_media(current["audio_url"])

            user_note = st.text_area("你的口译/重述输出（仅自我记录）", height=140)
            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("查看原文与参考答案", use_container_width=True):
                    st.markdown("### 原文")
                    st.write(current["source_text"])
                    st.markdown("### 参考答案")
                    st.write(current["reference_answer"])

            with c2:
                if st.button("调用大模型生成参考", use_container_width=True):
                    try:
                        llm_answer = generate_llm_answer(
                            api_key=model_cfg["api_key"],
                            model=model_cfg["text_model"],
                            base_url=model_cfg["text_base_url"],
                            mode=mode,
                            material=current,
                        )
                        st.session_state["llm_answer"] = llm_answer
                        st.success("模型调用成功。")
                    except Exception as exc:
                        st.error(f"模型调用失败：{sanitize_error(exc, model_cfg['api_key'])}")

            with c3:
                if st.button("保存到历史记录", use_container_width=True):
                    append_history(
                        {
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "mode": mode,
                            "difficulty": difficulty,
                            "material_id": current["id"],
                            "topic": current.get("topic", ""),
                            "source_text": current["source_text"],
                            "reference_answer": current["reference_answer"],
                            "user_output": user_note,
                            "llm_answer": st.session_state.get("llm_answer", ""),
                        }
                    )
                    st.success("已保存。")

            if st.session_state.get("llm_answer"):
                st.markdown("### 大模型参考答案")
                st.write(st.session_state["llm_answer"])

    with tab_upload:
        st.subheader("上传音频 -> 语音转文字 -> 翻译/重述")
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
            col1, col2, col3 = st.columns(3)

            with col1:
                run_stt = st.button("1) 仅转写")
            with col2:
                run_translate = st.button("2) 转写并翻译")
            with col3:
                run_paraphrase = st.button("3) 转写并重述")

            if run_stt or run_translate or run_paraphrase:
                try:
                    key = normalize_api_key(model_cfg["api_key"])
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
                            api_key=key,
                            base_url=model_cfg["text_base_url"],
                            model=model_cfg["text_model"],
                            text=transcript,
                            direction=direction,
                        )
                        st.markdown("### 翻译结果")
                        st.write(translated)

                    if run_paraphrase:
                        language = "English" if direction == "英文 -> 中文" else "中文"
                        paraphrased = paraphrase_text(
                            api_key=key,
                            base_url=model_cfg["text_base_url"],
                            model=model_cfg["text_model"],
                            text=transcript,
                            language=language,
                        )
                        st.markdown("### 重述结果")
                        st.write(paraphrased)
                except Exception as exc:
                    st.error(f"处理失败：{sanitize_error(exc, model_cfg['api_key'])}")
        else:
            st.info("先上传音频后再执行转写/翻译。")

        if st.session_state.get("text_test_reply"):
            st.caption(f"最近一次文本连通性测试返回：{st.session_state['text_test_reply']}")
        if st.session_state.get("stt_test_reply"):
            st.caption(f"最近一次语音连通性测试转写：{st.session_state['stt_test_reply'][:120]}")


if __name__ == "__main__":
    main()
