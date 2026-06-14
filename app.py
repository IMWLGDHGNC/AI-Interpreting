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
from interpreting_app.style import (
    inject_custom_css,
    render_result_card,
    render_section_header,
    render_status_badge,
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

def pull_url(url: str) -> str | None:
    """从 B 站拉取视频并提取音频，返回音频文件名。失败返回 None。"""
    try:
        tuple_1 = get_headers()
        response = get_response(url=url, cookies=tuple_1[0], headers=tuple_1[1])
        st.write("原链接:", url)
        info_tuple = get_video_audio_info(response)
        audio_name = info_tuple[2] + ".mp3"
        audio_path = MP3_PATH / audio_name
        if audio_path.exists():
            st.write("音频已存在，直接播放")
        else:
            MP3_PATH.mkdir(parents=True, exist_ok=True)
            download_video(info_tuple, save_dir=str(MP3_PATH))
            st.write("视频下载完成")
        return audio_name
    except Exception as exc:
        st.error(f"加载素材失败：{exc}")
        return None



def sanitize_with_keys(exc: Exception, keys: list[str]) -> str:
    msg = str(exc)
    for key in keys:
        msg = sanitize_error(Exception(msg), key)
    return msg


def friendly_error(exc: Exception, stt_key: str, llm_key: str) -> str:
    """把原始异常翻译成用户能看懂的中文提示。"""
    msg = str(exc).lower()
    if "401" in msg:
        return "🔑 API Key 无效或已过期。请在左侧栏检查 SiliconFlow / DeepSeek 的 API Key 是否正确填写。"
    if "403" in msg:
        return "🚫 API 访问被拒绝（403）。请检查 API Key 权限或账户余额是否充足。"
    if "404" in msg:
        return "🔗 API 端点不存在（404）。请检查左侧栏的 Base URL / Endpoint 地址是否正确。"
    if "timeout" in msg or "timed out" in msg:
        return "⏱️ 请求超时。请检查网络连接，或切换网络后重试。"
    if "connection" in msg or "refused" in msg or "name or service not known" in msg:
        return "🌐 网络连接失败。请检查网络是否正常，或 API 地址是否能访问。"
    return sanitize_with_keys(exc, [stt_key, llm_key])


def main() -> None:
    st.set_page_config(page_title="AI+口译训练平台", layout="wide")
    inject_custom_css()
    st.title("AI+口译训练平台")
    st.markdown("这是一个利用大模型辅助大学生进行英语口译训练的工具，它调用两个模型接口：DeepSeek 生成文本答案，Silicon STT 进行语音转写。")
    st.markdown("它支持从素材库中抓取训练素材进行练习；也支持自主上传语音进行练习。")
    st.markdown("大模型可以实现转写、翻译、重述和生成口译笔记的功能。")
    st.caption("开发者正在想办法压低成本。")
    

    ensure_storage()
    model_cfg = render_sidebar()
    used = st.session_state.setdefault("used", {})
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
            if picked is None:
                # 该类别没有配置任何素材 URL
                st.error(
                    f"「{material_type}」类别暂无素材。\n\n"
                    "请在 `interpreting_app/config.py` 的 `DAILY_ENGLISH_URL`（或其他对应列表）"
                    "中添加 B 站视频链接，并将类别名注册到 `MATERIAL_URLS` 字典中。"
                )
            elif picked == "":
                # 全部用完 → 重置并重试
                st.warning("该类别素材已全部用完，已重置使用状态，请再次点击加载。")
                st.session_state["used"] = {}
                picked = select_material(material_type, st.session_state["used"])
            if picked and picked != "":
                st.session_state["current_material"] = picked
                audio_name = pull_url(picked)
                if audio_name is None:
                    st.stop()  # pull_url 内部已经显示了错误信息
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
            try:
                st.caption("伟大的大模型将一站式处理转写+翻译+源语重述+口译笔记，坐享其成吧～")
                stt_key = normalize_api_key(model_cfg["silicon_api_key"])
                transcript = transcribe_audio_bytes(
                    api_key=stt_key,
                    endpoint=model_cfg["stt_endpoint"],
                    model=model_cfg["stt_model"],
                    file_bytes=payload["bytes"],
                    filename=payload["name"],
                    mime_type=payload["type"],
                    language="en",  # 训练素材均为英文
                )
                st.session_state["uploaded_transcript"] = transcript
                render_result_card("转写文本", transcript, "transcription")

                direction = TRANSLATION_DIRECTION_OPTIONS[0]
                translated = translate_text(
                    api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                    base_url=model_cfg["deepseek_base_url"],
                    model=model_cfg["deepseek_model"],
                    text=transcript,
                    direction=direction,
                )
                render_result_card("翻译结果", translated, "translation")

                language = "English"
                paraphrased = paraphrase_text(
                    api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                    base_url=model_cfg["deepseek_base_url"],
                    model=model_cfg["deepseek_model"],
                    text=transcript,
                    language=language,
                )
                st.session_state["paraphrased"] = paraphrased
                render_result_card("重述结果", paraphrased, "paraphrase")

                language = "English"
                notes = taking_notes_text(
                    api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                    base_url=model_cfg["deepseek_base_url"],
                    model=model_cfg["deepseek_model"],
                    text=transcript,
                    language=language,
                )
                render_result_card("口译笔记", notes, "notes")
            except Exception as exc:
                st.error(friendly_error(
                    exc,
                    model_cfg["silicon_api_key"],
                    model_cfg["deepseek_api_key"],
                ))

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
                        language="en" if direction == "英文 -> 中文" else "zh",
                    )
                    st.session_state["uploaded_transcript"] = transcript
                    render_result_card("转写文本", transcript, "transcription")

                    if run_translate:
                        translated = translate_text(
                            api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                            base_url=model_cfg["deepseek_base_url"],
                            model=model_cfg["deepseek_model"],
                            text=transcript,
                            direction=direction,
                        )
                        render_result_card("翻译结果", translated, "translation")

                    if run_paraphrase:
                        language = "English" if direction == "英文 -> 中文" else "中文"
                        paraphrased = paraphrase_text(
                            api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                            base_url=model_cfg["deepseek_base_url"],
                            model=model_cfg["deepseek_model"],
                            text=transcript,
                            language=language,
                        )
                        render_result_card("重述结果", paraphrased, "paraphrase")

                    if run_notes:
                        language = "English" if direction == "英文 -> 中文" else "中文"
                        notes = taking_notes_text(
                            api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                            base_url=model_cfg["deepseek_base_url"],
                            model=model_cfg["deepseek_model"],
                            text=transcript,
                            language=language,
                        )
                        render_result_card("口译笔记", notes, "notes")
                except Exception as exc:
                    st.error(friendly_error(
                        exc,
                        model_cfg["silicon_api_key"],
                        model_cfg["deepseek_api_key"],
                    ))
        else:
            st.info("先上传音频后再执行转写/翻译。")

        # if st.button("保存历史记录",use_container_width=True):
        #     if not st.session_state.get("uploaded_transcript"):
        #         st.warning("没有转写文本可保存，请先执行转写。")

        if st.session_state.get("text_test_reply"):
            st.caption(f"最近一次文本连通性测试返回：{st.session_state['text_test_reply']}")
        if st.session_state.get("stt_test_reply"):
            st.caption(f"最近一次语音连通性测试转写：{st.session_state['stt_test_reply'][:120]}")

    with tab_notes:
        st.subheader("📝 口译笔记专项训练")
        st.caption(
            "训练流程：听音频 → 自己动手写笔记 → 查看 AI 笔记对照。"
            "口译笔记的核心是 **少记、快记**——只抓关键词、逻辑关系、数字和专有名词，中英混用，善用符号和缩写。"
        )

        # ── 素材加载 ──────────────────────────────────────────
        st.markdown("### ① 加载训练素材")
        notes_mat_type = st.selectbox("素材类别", CLASS, key="notes_material_type")

        col_load, col_upload_notes = st.columns([1, 1])
        with col_load:
            if st.button("随机加载素材", type="primary", key="notes_load_btn"):
                picked = select_material(notes_mat_type, used)
                if picked is None:
                    st.error(
                        f"「{notes_mat_type}」类别暂无素材。"
                        "请在 `config.py` 中添加链接并注册到 `MATERIAL_URLS`。"
                    )
                elif picked == "":
                    st.warning("该类别素材已全部用完，已重置，请再次点击加载。")
                    st.session_state["used"] = {}
                    picked = select_material(notes_mat_type, st.session_state["used"])
                if picked and picked != "":
                    st.session_state["notes_current_material"] = picked
                    audio_name = pull_url(picked)
                    if audio_name is None:
                        st.stop()
                    audio_path = MP3_PATH / audio_name
                    if audio_path.exists():
                        payload_bytes = audio_path.read_bytes()
                        audio_mime = (
                            "audio/mp4"
                            if len(payload_bytes) > 8 and payload_bytes[4:8] == b"ftyp"
                            else "audio/mpeg"
                        )
                        st.session_state["notes_audio_payload"] = {
                            "bytes": payload_bytes,
                            "name": audio_name,
                            "type": audio_mime,
                        }
                        # 自动转写
                        try:
                            stt_key = normalize_api_key(model_cfg["silicon_api_key"])
                            st.session_state["notes_transcript"] = transcribe_audio_bytes(
                                api_key=stt_key,
                                endpoint=model_cfg["stt_endpoint"],
                                model=model_cfg["stt_model"],
                                file_bytes=payload_bytes,
                                filename=audio_name,
                                mime_type=audio_mime,
                                language="en",
                            )
                        except Exception as exc:
                            st.error(friendly_error(exc, model_cfg["silicon_api_key"], model_cfg["deepseek_api_key"]))
                            st.stop()
                    # 清除上一次的笔记，新素材新开始
                    st.session_state["notes_user_text"] = ""
                    st.session_state["notes_ai_text"] = ""

        notes_payload = st.session_state.get("notes_audio_payload")
        notes_transcript = st.session_state.get("notes_transcript", "")
        notes_current = st.session_state.get("notes_current_material", "")

        if notes_current:
            st.info(f"当前素材：{notes_current}")

        # ── 音频播放 ──────────────────────────────────────────
        if notes_payload:
            st.markdown("### ② 听音频，写笔记")
            st.audio(notes_payload["bytes"], format=notes_payload.get("type", "audio/mpeg"))
            st.caption(f"文件：{notes_payload.get('name', 'unknown')}")

            # 转写原文折叠起来（先不看，听完再对照）
            if notes_transcript:
                with st.expander("📄 查看转写原文（建议先听完再点开）"):
                    st.write(notes_transcript)

            # ── 用户笔记输入区 ────────────────────────────────
            user_notes = st.text_area(
                "✏️ 你的口译笔记",
                value=st.session_state.get("notes_user_text", ""),
                height=200,
                placeholder=(
                    "听完音频后，在这里写下你的口译笔记……\n\n"
                    "提示：\n"
                    "· 尽量少记，只记关键词和逻辑关系\n"
                    "· 数字、专有名词一定要记\n"
                    "· 中英混用，哪个快用哪个\n"
                    "· 多用符号（↑↓→← $ & @ #）和缩写"
                ),
                key="notes_user_text",
            )

            # ── 操作按钮 ──────────────────────────────────────
            col_gen, col_clear = st.columns([1, 1])
            with col_gen:
                if st.button("🤖 生成 AI 笔记对照", type="primary", use_container_width=True):
                    if not notes_transcript:
                        st.warning("请先加载素材并完成转写。")
                    else:
                        try:
                            with st.spinner("AI 正在生成口译笔记……"):
                                ai_notes = taking_notes_text(
                                    api_key=normalize_api_key(model_cfg["deepseek_api_key"]),
                                    base_url=model_cfg["deepseek_base_url"],
                                    model=model_cfg["deepseek_model"],
                                    text=notes_transcript,
                                    language="English",
                                )
                            st.session_state["notes_ai_text"] = ai_notes
                        except Exception as exc:
                            st.error(friendly_error(exc, model_cfg["silicon_api_key"], model_cfg["deepseek_api_key"]))
            with col_clear:
                if st.button("🗑️ 清空重写", use_container_width=True):
                    st.session_state["notes_user_text"] = ""
                    st.session_state["notes_ai_text"] = ""
                    st.rerun()

            # ── 对照展示 ──────────────────────────────────────
            ai_notes = st.session_state.get("notes_ai_text", "")
            current_user = st.session_state.get("notes_user_text", "")
            if ai_notes:
                st.markdown("### ③ 对照学习")
                col_me, col_ai = st.columns(2)
                with col_me:
                    render_result_card("我的笔记", current_user or "（空）", "notes")
                with col_ai:
                    render_result_card("AI 笔记", ai_notes, "notes")

            # ── 笔记法小贴士 ──────────────────────────────────
            with st.expander("💡 口译笔记法小贴士"):
                st.markdown("""
| 原则 | 说明 |
|------|------|
| **少记** | 记 20% 的关键信息，脑补剩下的 80% |
| **关键词** | 主谓宾核心词、逻辑连接词（因/果/但/所以） |
| **数字 & 专名** | 最容易忘，必须写下来 |
| **符号化** | ↑增长 ↓下降 →导致 ←来自 $钱 &和 @在 #编号 |
| **缩写** | info=信息, gov=政府, eco=经济, rel=关系, resp=责任 |
| **中英混** | 哪个短写哪个，中文词短写中文，英文词短写英文 |
| **竖排** | 主句左对齐，从句缩进，一目了然 |
                """)

    st.markdown("---")
    st.caption("© 2026 Daniel")
    st.caption("Design, implementation, testing, and deployment")


if __name__ == "__main__":
    main()
