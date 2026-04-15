import re
from typing import Dict

from openai import OpenAI


def normalize_api_key(raw_key: str) -> str:
    key = (raw_key or "").strip()
    tokens = re.findall(r"sk-[A-Za-z0-9_\-]+", key)
    if tokens:
        return tokens[0]
    return key


def sanitize_error(exc: Exception, api_key: str) -> str:
    '''
    异常处理函数，避免在显示报错时暴露api key
    '''
    msg = str(exc)
    key = normalize_api_key(api_key)
    if key:
        msg = msg.replace(key, "[REDACTED_KEY]")
    return msg


def call_qwen_chat(api_key: str, base_url: str, model: str, system_prompt: str, user_prompt: str) -> str:
    client = OpenAI(api_key=api_key, base_url=base_url.strip())
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        extra_body={"enable_thinking": False},
        temperature=0.4,
        
    )
    return completion.choices[0].message.content.strip()


def translate_text(
    api_key: str,
    base_url: str,
    model: str,
    text: str,
    direction: str,
) -> str:
    if direction == "英文 -> 中文":
        user_prompt = (
            "你是一个专业的口译人员，擅长将英文翻译成自然、准确的中文。"
            "请把下面英文翻译成自然、准确的中文。"
            "只输出译文，不要解释。\n"
            f"原文：{text}"
        )
    else:
        user_prompt = (
            "你是一个专业的口译人员，擅长将中文翻译成自然、准确的英文。"
            "请把下面中文翻译成自然、准确的英文。"
            "只输出译文，不要解释。\n"
            f"原文：{text}"
        )
    return call_qwen_chat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        system_prompt="你是专业口译训练师，擅长中英互译。",
        user_prompt=user_prompt,
    )


def paraphrase_text(api_key: str, base_url: str, model: str, text: str, language: str) -> str:
    user_prompt = (
        "请对下面内容做同语言同义重述。"
        "仅输出重述结果，不要解释。\n"
        f"语言：{language}\n"
        f"原文：{text}"
    )
    return call_qwen_chat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        system_prompt="你是专业口译训练师，擅长源语重述。",
        user_prompt=user_prompt,
    )


def test_text_model(api_key: str, base_url: str, model: str) -> str:
    return call_qwen_chat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        system_prompt="你是一个有用的助手。",
        user_prompt="请只回复ok",
    )


def generate_llm_answer(
    api_key: str,
    model: str,
    base_url: str,
    mode: str,
    material: Dict,
) -> str:
    normalized_key = normalize_api_key(api_key)
    if not normalized_key:
        raise ValueError("请先填写 API Key（必须使用 key 才能调用模型）。")
    if not base_url.strip():
        raise ValueError("Base URL 不能为空。")
    if not model.strip():
        raise ValueError("Model 不能为空。")

    text = material["source_text"]
    if mode == "双语转换":
        return translate_text(
            api_key=normalized_key,
            base_url=base_url.strip(),
            model=model.strip(),
            text=text,
            direction=material["direction"],
        )

    language = material.get("language", "中文")
    return paraphrase_text(
        api_key=normalized_key,
        base_url=base_url.strip(),
        model=model.strip(),
        text=text,
        language=language,
    )
