import streamlit as st
import os
import time
import requests
from dotenv import load_dotenv
from openai import OpenAI

# --- 页面配置 ---
st.set_page_config(
    page_title="AI 智能报错修复助手",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 核心逻辑函数 (复用原脚本逻辑) ---

def clean_error_log_with_slm(raw_log, model_name):
    """调用本地 Ollama 清洗日志"""
    url = "http://localhost:11434/api/generate"
    prompt = f"""
    你是一个报错日志清洗工具。请从下面的杂乱日志中提取：
    1. 错误类型 (Error Type)
    2. 导致错误的用户代码行号 (User Code Line)
    3. 核心报错信息 (Core Message)
    
    忽略所有系统库(System Libs)和框架层(Framework)的堆栈信息。
    只输出纯文本摘要，不要Markdown。
    
    日志内容：
    {raw_log}
    """
    
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "❌ 本地清洗失败: 返回缺少 response 字段")
    except requests.RequestException as exc:
        return f"❌ 本地连接失败 (请检查 Ollama 是否运行): {exc}"
    except Exception as e:
        return f"❌ 未知错误: {str(e)}"

def ask_expert_llm(user_code, error_summary, api_key, model="deepseek-chat"):
    """调用云端 DeepSeek 分析"""
    if not api_key:
        return "⚠️ 未检测到 API Key，请在左侧侧边栏输入或配置 .env 文件。"

    prompt = f"""
    我遇到一个报错，请帮我修复。

    【我的代码】：
    {user_code}

    【报错关键信息】(由本地助手提取)：
    {error_summary}

    请分析原因并给出修改后的代码。请使用 Markdown 格式输出。
    """

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as exc:
        return f"❌ 云端调用失败: {exc}"

# --- 界面 UI 构建 ---

# 1. 侧边栏：设置与介绍
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 尝试自动加载环境变量
    load_dotenv()
    env_key = os.getenv("DEEPSEEK_API_KEY", "")
    
    api_key = st.text_input("DeepSeek API Key", value=env_key, type="password", help="如果没有设置环境变量，请在此处输入")
    ollama_model = st.text_input("本地 Ollama 模型", value="qwen2.5-coder:1.5b", help="请确保本地 Ollama 已安装此模型")
    
    st.markdown("---")
    st.markdown("""
    ### 📖 关于本工具
    这是一个 **隐私优先** 的报错修复助手。
    
    **工作原理：**
    1. **本地小模型** (Ollama) 首先运行，清洗冗长的报错堆栈，提取关键信息。
    2. **云端大模型** (DeepSeek) 接收精简后的信息和代码，提供修复方案。
    
    这样做既保护了隐私，又节省了 Token。
    """)

# 2. 主页面：标题与输入
st.title("🚑 AI 智能报错修复助手")
st.markdown("遇到 Bug 了？别担心。粘贴你的代码和报错日志，AI 会帮你找出问题所在。")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ 你的代码 (Python)")
    user_code = st.text_area("粘贴相关代码片段", height=300, placeholder="def my_function():...")

with col2:
    st.subheader("2️⃣ 报错日志 (Traceback)")
    error_log = st.text_area("粘贴完整报错信息", height=300, placeholder="Traceback (most recent call last)...")

# 3. 执行按钮与结果展示
if st.button("🚀 开始诊断", type="primary", use_container_width=True):
    if not user_code or not error_log:
        st.warning("⚠️ 请同时输入代码和报错日志。")
    else:
        # 使用 st.status 创建一个动态的状态容器
        with st.status("正在进行 AI 诊断...", expanded=True) as status:
            
            # 第一步：本地清洗
            st.write("🔍 [Step 1] 正在唤醒本地小模型 (Ollama) 清洗日志...")
            start_time = time.time()
            clean_log = clean_error_log_with_slm(error_log, ollama_model)
            
            if "❌" in clean_log:
                status.update(label="本地清洗失败", state="error")
                st.error(clean_log)
                st.stop()
            else:
                st.write(f"✅ 日志清洗完成 (耗时 {time.time()-start_time:.2f}s)")
                # 在这里展示清洗后的结果给用户看（增加透明度）
                with st.expander("👀 点击查看清洗后的关键报错信息"):
                    st.code(clean_log, language="text")

            # 第二步：云端分析
            st.write("🧠 [Step 2] 正在发送给云端专家 (DeepSeek)...")
            solution = ask_expert_llm(user_code, clean_log, api_key)
            
            if "❌" in solution or "⚠️" in solution:
                status.update(label="云端分析遇到问题", state="error")
                st.error(solution)
            else:
                status.update(label="✅ 诊断完成！", state="complete")
                
                st.divider()
                st.subheader("💡 修复建议")
                st.markdown(solution)