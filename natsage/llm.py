"""
llm.py - 大模型 API 封装

支持两种服务，都兼容 OpenAI 的接口格式：
  1. DeepSeek（默认）：https://api.deepseek.com
  2. 火山方舟 Ark（豆包）：https://ark.cn-beijing.volces.com/api/v3

API Key 通过环境变量读取，推荐写在项目根目录的 .env 文件里
（启动前先运行 pip install python-dotenv，或在命令行手动 export）。
"""
import os

import requests

# 两种可切换的大模型服务配置
PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
    "ark": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-1-5-pro-32k-250115",  # 换成你自己的推理接入点 ID
        "api_key_env": "ARK_API_KEY",
    },
}


def _load_dotenv():
    """读取项目根目录的 .env 文件（格式 KEY=VALUE），写入环境变量。

    用标准库实现，不依赖 python-dotenv，减少安装步骤。
    """
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def chat(prompt, system="你是网络工程专家，回答简洁、专业、可操作。", provider="deepseek"):
    """发送一次对话请求，返回模型回答的文本。"""
    _load_dotenv()

    conf = PROVIDERS[provider]
    api_key = os.environ.get(conf["api_key_env"])
    if not api_key:
        return (
            "[提示] 缺少 API Key：请复制 .env.example 为 .env，"
            f"在里面填写 {conf['api_key_env']}=你的key，"
            "并安装依赖：pip install -r requirements.txt"
        )

    url = conf["base_url"] + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": conf["model"],
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }

    resp = None
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"[错误] 请求失败：{e}"
    except Exception as e:
        detail = resp.text[:300] if resp is not None else "无返回"
        return f"[错误] 解析返回失败：{e}，原始返回：{detail}"
