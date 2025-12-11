import os
import requests
from openai import OpenAI

# 1. 定义调用本地小模型的函数 (通过 Ollama API)
def clean_error_log_with_slm(raw_log, url="http://localhost:11434/api/generate", model="qwen2.5-coder:1.5b", timeout=15):
    
    # 专门为提取关键信息设计的 Prompt
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
        "model": model,  # 使用超轻量模型
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(url, json=data, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"本地清洗失败: {exc}"

    try:
        payload = response.json()
    except ValueError:
        return "本地清洗失败: 返回内容不是 JSON"

    return payload.get("response", "本地清洗失败: 返回缺少 response 字段")

# 2. 定义调用云端大模型的函数 (OpenAI 示例)
def ask_expert_llm(user_code, error_summary, model="gpt-4.1-mini", timeout=20):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "云端调用失败: 缺少环境变量 OPENAI_API_KEY"

    prompt = f"""
    我遇到一个报错，请帮我修复。

    【我的代码】：
    {user_code}

    【报错关键信息】(由本地助手提取)：
    {error_summary}

    请分析原因并给出修改后的代码。
    """

    client = OpenAI(api_key=api_key)

    try:
        resp = client.responses.create(
            model=model,
            input=[{"role": "user", "content": prompt}],
            max_output_tokens=800,
            temperature=0.3,
            timeout=timeout,
        )
    except Exception as exc:  # SDK 抛出的网络/鉴权/配额等错误
        return f"云端调用失败: {exc}"

    try:
        return resp.output_text
    except Exception:
        return "云端调用失败: 返回内容无法解析"

# --- 模拟运行 ---
if __name__ == "__main__":
    # 模拟一个超长的 Python 报错堆栈
    long_noisy_log = """
    Traceback (most recent call last):
      File "/usr/local/lib/python3.9/site-packages/pandas/core/indexes/base.py", line 3629, in get_loc
        return self._engine.get_loc(casted_key)
      File "pandas/_libs/index.pyx", line 136, in pandas._libs.index.IndexEngine.get_loc
      ... (省略 50 行 Pandas 内部错误) ...
      File "/Users/student/homework/data_analysis.py", line 42, in calculate_avg
        result = df['score'] / df['weight']
      File "/usr/local/lib/python3.9/site-packages/pandas/core/frame.py", line 3807, in __getitem__
        indexer = self.columns.get_loc(key)
    KeyError: 'weight'
    """
    
    user_source_code = "def calculate_avg(df): return df['score'] / df['weight']"

    print("正在使用本地小模型清洗日志...")
    summary = clean_error_log_with_slm(long_noisy_log)
    print(f"清洗结果：\n{summary}\n")
    
    cloud_result = ask_expert_llm(user_source_code, summary)
    print("------ 云端回答 ------")
    print(cloud_result)