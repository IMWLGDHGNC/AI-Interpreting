# Prompt2

在实现Prompt的过程中，我们没有很好的模型去处理，也无法正确接入模型。

现在，先调用下面的语音转文字模型实现对中/英文音频文件的语音转文字，再调用下面的千问实现翻译和源语重述。

修改代码：
1. 重写界面左侧的UI，修改接大模型的模块，接上述两个模型，提供测试大模型连通性的按钮；
2. 增加自主上传音频文件的功能，可以将英文翻成中文、中文翻成英文；

这是接入硅基流动的语音转文字的模型的模版。
```python
import requests
url = "https://api.siliconflow.cn/v1/audio/transcriptions"
file_path = "path/to/your/audio.mp3"
headers = {
    "Authorization": "Bearer <YOUR_API_KEY>"
}
with open(file_path, "rb") as audio_file:
    files = {
        "file": ("audio.mp3", audio_file),  # 根据文件类型调整 MIME 类型
        "model": (None, "FunAudioLLM/SenseVoiceSmall")
    }
    response = requests.post(url, headers=headers, files=files)
```

这是接入文本翻译模型的千问模型的模版
```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.siliconflow.cn/v1"
)

response = client.chat.completions.create(
    model="Qwen/Qwen3.5-4B",
    messages=[
        {"role": "system", "content": "你是一个有用的助手"},
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
)
print(response.choices[0].message.content)
```

