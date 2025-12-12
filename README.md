# 🚑 AI 智能报错修复助手 (SLM-LLM Hybrid Debugger)

一个专为开发者设计的、**隐私优先**的报错诊断及代码修复 Web 应用。

本项目结合了**本地超轻量级模型 (SLM)** 和**云端专家级大模型 (LLM)** 的优势，在不上传完整、冗长、可能包含敏感信息的堆栈日志的前提下，获取高质量的代码修复建议。

## ✨ 核心特性

* **🛡️ 隐私保护**：使用本地运行的 **Ollama 模型**（如 Qwen2.5-Coder:1.5B）清洗原始、冗长的报错堆栈，提取关键信息。
* **💡 高效诊断**：只将**精简后的日志摘要**发送给云端大模型（如 DeepSeek），大幅减少隐私暴露风险，同时节省 API 费用和响应时间。
* **💻 跨平台 Web 界面**：基于 **Streamlit** 构建的简洁用户界面，无需复杂的配置即可在浏览器中使用。
* **🚀 快速修复**：利用 DeepSeek 等高性能模型，提供详细的错误原因分析和修改后的代码示例。

## ⚙️ 技术栈

* **Web 框架**：Streamlit (Python)
* **本地模型运行时**：Ollama (用于运行 SLM)
* **本地清洗模型 (SLM)**：`qwen2.5-coder:1.5b` (或其他轻量级模型)
* **云端专家模型 (LLM)**：DeepSeek-Chat (或其他支持 OpenAI 接口的云服务)
* **依赖管理**：`requests`, `openai`, `python-dotenv`

## 🚀 快速开始

### 前提条件

1.  **Python 环境**：确保 Python 3.8+ 已安装并配置了 PATH 环境变量。
2.  **Ollama 服务**：你的本地机器需要运行 Ollama 服务。
    * 启动服务：`ollama serve`
    * 拉取模型：`ollama pull qwen2.5-coder:1.5b`
3.  **API Key**：拥有 DeepSeek 或其他云端 LLM 服务的 API Key。

### 步骤 1: 克隆仓库 & 安装依赖

```bash
# 假设您的项目文件夹名为 ELS
cd ELS 
# 创建虚拟环境（推荐）
python -m venv venv
./venv/Scripts/activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安装所有依赖
pip install streamlit requests python-dotenv openai
```

### 步骤 2: 配置 API Key

在项目根目录下创建 `.env` 文件并填入密钥：

```bash
# .env 文件内容
DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY_HERE"
```

> 也可以在启动应用后通过侧边栏输入密钥。

### 步骤 3: 运行应用

在终端中启动 Web 服务：

```bash
streamlit run app.py
```

服务启动后，浏览器将自动打开应用页面 (http://localhost:8501)。

## 💡 使用指南

* 粘贴代码：在左侧输入框粘贴出现问题的代码片段。
* 粘贴日志：在右侧输入框粘贴完整的报错堆栈信息（Traceback）。
* 开始诊断：点击 🚀 开始诊断 按钮。
* 查看结果：查看进度及云端专家模型提供的修复建议与代码示例。

## 🤝 贡献与改进

1. Fork 本仓库。
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交修改：`git commit -m "Add some AmazingFeature"`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 发起 Pull Request。