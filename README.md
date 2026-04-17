# AI+口译训练平台（Streamlit）

## 1. 功能概览
- 双语转换：英译中 / 中译英
- 源语重述：同语言同义转述
- 分层训练：初级 / 中级 / 高级
- 音频播放：支持 B 站内嵌播放与直链兜底
- 上传音频：先用硅基流动语音转写，再用 DeepSeek 做翻译或源语重述
- 历史记录：训练题面、参考答案、模型答案可持久化到 JSON
- 大模型调用：DeepSeek Chat + 硅基流动 SenseVoice

## 2. 安装依赖
```bash
pip install -r requirements.txt
```

## 3. 启动
```bash
streamlit run app.py
```

## 4. API Key 说明
- 系统不会硬编码 key。
- 请在侧边栏填写 SiliconFlow API Key。
- 文本模型默认使用 `https://api.deepseek.com` 和 `deepseek-chat`。
- 语音转写默认使用 `FunAudioLLM/SenseVoiceSmall`。
- 若不填 key，模型调用会被拒绝。

## 5. 数据文件
- 训练素材：`data/materials.json`
- 历史记录：`storage/history.json`

## 6. 使用方式
- 左侧栏先测试文本模型和语音模型连通性。
- 主界面可在“素材训练”和“上传音频训练”两个标签页间切换。
- 上传音频页支持“仅转写”“转写并翻译”“转写并重述”。

## 7. 可扩展方向（当前按作业要求未实现）
- 智能评分
- 自动点评与优化建议
- 更大规模素材库与批量管理
