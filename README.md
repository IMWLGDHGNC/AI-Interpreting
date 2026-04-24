# AI+口译训练平台（Streamlit）

## 1. 功能概览
- 双语转换：英译中 / 中译英
- 源语重述：同语言同义转述
- 音频播放：支持 B 站内嵌播放与直链兜底
- 上传音频：先用硅基流动语音转写，再用 DeepSeek 做翻译或源语重述
- 历史记录：训练题面、参考答案、模型答案可持久化到 JSON
- 大模型调用：DeepSeek Chat + 硅基流动 SenseVoice

## 2. 克隆与部署
### 2.1 克隆仓库（含子模块）
本项目使用 Git Submodule 管理第三方库 [Spider-for-Bilibili](https://github.com/xinren46/Spider-for-Bilibili)。

# AI+口译训练平台（Streamlit）

## 1. 项目简介
本项目用于英语口译训练，支持随机素材训练和上传音频训练两类流程。
系统使用两条模型链路：
- DeepSeek：文本翻译、源语重述、口译笔记生成
- SiliconFlow SenseVoice：语音转文字

## 2. 当前功能
- 随机素材训练（B站视频素材）
- 自动下载素材音频到本地
- Magic Button 一键执行：转写 + 翻译 + 重述 + 口译笔记
- 上传本地音频后分步执行：
  - 仅转写
  - 转写并翻译
  - 转写并重述
  - 转写并生成口译笔记
- 左侧栏模型连通性测试（文本模型、语音模型）
- 历史记录查看

## 3. 环境准备
### 3.1 克隆项目（包含子模块）
本项目依赖 Spider-for-Bilibili 子模块下载B站素材：

```bash
git clone --recurse-submodules <your-repo-url>
```

如果你已经 clone 过但没有子模块：

```bash
git submodule update --init --recursive
```

### 3.2 安装依赖
```bash
pip install -r requirements.txt
```

## 4. 启动项目
```bash
streamlit run app.py
```

## 5. 配置说明
在左侧栏填写以下配置：

- SiliconFlow API Key（用于语音转写）
- DeepSeek API Key（用于文本任务）
- DeepSeek Base URL（默认：https://api.deepseek.com）
- DeepSeek Model（默认：deepseek-chat）
- STT Endpoint（默认：https://api.siliconflow.cn/v1/audio/transcriptions）
- STT Model（默认：FunAudioLLM/SenseVoiceSmall）

说明：
- 项目不会硬编码或保存你的 key。
- 若 key 为空或无效，对应功能会调用失败。

## 6. 使用流程
### 6.1 随机素材训练
1. 选择素材类别。
2. 点击“加载新素材”，系统会拉取并下载对应音频到 data/mp3。
3. 点击“Magic Button”执行完整流程。

### 6.2 上传音频训练
1. 上传本地音频（mp3/wav/m4a/mp4）。
2. 选择翻译方向。
3. 点击需要的处理按钮。

## 7. 目录结构
```text
.
├── app.py
├── requirements.txt
├── README.md
├── interpreting_app/
│   ├── audio_ai.py
│   ├── config.py
│   ├── llm.py
│   ├── media.py
│   ├── repository.py
│   └── ui.py
├── data/
│   ├── materials.json
│   └── mp3/
├── storage/
│   └── history.json
└── third_party/
    └── Spider-for-Bilibili/
```

## 8. 第三方模块说明
Spider-for-Bilibili 用于 B站视频信息抓取与下载。

- 路径：third_party/Spider-for-Bilibili
- 主要用途：按 BV 链接下载视频/音频
- 可选配置：在对应 header/cookie 配置文件中设置登录信息

