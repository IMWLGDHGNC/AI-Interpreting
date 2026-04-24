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

def taking_notes_text(api_key: str, base_url: str, model: str, text: str, language: str) -> str:
    user_prompt = (
        "请就所听到的内容生成适合职业口译员使用的中英口译笔记，\n"
        "笔记应遵循四个原则：\n"
        "1）尽量少记\n"
        "2）只记关键词，逻辑关系，容易遗忘的数字和专有名词\n"
        "3）中英并用，以快为准\n"
        "4）多用符号和缩略式\n"  
        "举个例子，如果听到:\n"
        "Researchers found that most young netizens still aspire to be in a romantic relationship, and only a few expressed no intention.But young netizen's willingness to get married is much lower than their willingness to fall in love Staistics show that compared to young netizens with a middle school or high school degree, those with a bachelor's or master's degree are more willing to get involved in a romantic relationship and get married, on the one hand, young people hold high expectations for relationships, because being in a relationship not only fits the worldly definition of success, but is also the first option for young people when they feel,Lonely and crave company On the other hand, marriageage means more responsibility, a heavier financial burden and stricter social discipline, the fact that many parents forbid their children from engaging in relationships in primary and secondary school, also Rob's young people of opportunities to communicate with the opposite sex, making it difficult for them to effectively establish intimate relationships when they grow up.\n"
        "返回如下内容：\n"
        "Res\n"
        "青网：most 恋，few 无\n"
        "恋≫婚\n"
        "edu："
        "初高中↓｜本硕↑"
        "恋：高预期｜世俗success｜解lone"
        "婚：resp↑｜$重｜社束严"
        "小中学：家长禁早恋"
        "→异性交少→难intimate rel"      
        f"语言：{language}\n"
        f"原文：{text}"
    )
    return call_text_chat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        system_prompt="你是专业口译训练师，擅长生成口译笔记。",
        user_prompt=user_prompt,
    )

def test_text_model(api_key: str, base_url: str, model: str) -> str:
    """测试文本模型是否可用，返回模型回复的内容"""
    return call_text_chat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        system_prompt="你是一个有用的助手。",
        user_prompt="请只回复ok",
    )
