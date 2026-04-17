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


def call_text_chat(
    api_key: str,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> str:
    if not api_key.strip():
        raise ValueError("DeepSeek API Key 不能为空。")

    client = OpenAI(
        api_key=api_key.strip(),
        base_url=base_url.strip().rstrip("/"),
    )
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    if completion.choices and completion.choices[0].message:
        content = completion.choices[0].message.content or ""
        if content.strip():
            return content.strip()

    raise ValueError("DeepSeek 返回为空，无法解析文本结果。")


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
    return call_text_chat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        system_prompt="你是专业口译训练师，擅长中英互译。",
        user_prompt=user_prompt,
    )


def paraphrase_text(api_key: str, base_url: str, model: str, text: str, language: str) -> str:
    user_prompt = (
        "请对下面内容做同语言同义重述。"
        "源语重述要求用同一种语言，对说话的主要内容进行简洁重述，可以使用不同的表达方式，但必须保持原意不变，只需要概括主要内容，在几句话之内完成。"
        "仅输出重述结果，不要解释。\n"
        "例子：原文：'Despite the fact that the team had conducted multiple rounds of rigorous testing and had not encountered any significant issues during the entire development phase, the product still failed catastrophically within the first few hours of its official launch due to an unforeseen interaction between two seemingly unrelated software modules.\n'输出：'An unexpected software conflict caused the product to fail immediately after launch, even though earlier tests had shown no major problems.'\n"
        f"语言：{language}\n"
        f"原文：{text}"
    )
    return call_text_chat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        system_prompt="你是专业口译训练师，擅长源语重述。",
        user_prompt=user_prompt,
    )


def test_text_model(api_key: str, base_url: str, model: str) -> str:
    return call_text_chat(
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
    if not base_url.strip():
        raise ValueError("DeepSeek Base URL 不能为空。")
    if not model.strip():
        raise ValueError("DeepSeek Model 不能为空。")

    text = material["source_text"]
    if mode == "双语转换":
        return translate_text(
            api_key=api_key,
            base_url=base_url.strip(),
            model=model.strip(),
            text=text,
            direction=material["direction"],
        )

    language = material.get("language", "中文")
    return paraphrase_text(
        api_key=api_key,
        base_url=base_url.strip(),
        model=model.strip(),
        text=text,
        language=language,
    )
