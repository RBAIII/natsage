"""
topo.py - AIGC 拓扑图生成

输入网络描述，让大模型生成 Mermaid 图代码，保存为 .mmd 文件。
如果电脑装了 mermaid-cli (mmdc)，会自动渲染成 PNG 图片。
"""
import re
import subprocess

from natsage.llm import chat


def generate_mermaid(description, provider="deepseek"):
    """根据网络描述让大模型生成 mermaid 拓扑图代码。"""
    system = "你是网络架构师，擅长用 mermaid 画网络拓扑图。只输出 mermaid 代码，不要输出任何解释。"
    prompt = (
        "请用 mermaid 的 graph TD 语法画一张网络拓扑图，要求：\n"
        "- 路由器用双层方框 {{...}}，交换机用方框 [...], 终端用圆角框(...)\n"
        "- 防火墙、服务器等设备名称写清楚\n"
        "- 链路上标注协议或链路类型\n\n"
        f"网络描述：{description}"
    )
    code = chat(prompt, system=system, provider=provider)

    # 去掉大模型可能包裹的 ```mermaid 代码块标记
    code = re.sub(r"```(?:mermaid)?", "", code).strip()
    return code


def save_topo(mermaid_code, path="topo.mmd"):
    """保存 mermaid 代码到文件；若系统装了 mmdc 则顺便渲染成 PNG。"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(mermaid_code)
    print(f"[OK] 已保存拓扑图源码：{path}")

    png_path = path.replace(".mmd", ".png")
    try:
        subprocess.run(
            ["mmdc", "-i", path, "-o", png_path],
            check=True, timeout=60, capture_output=True,
        )
        print(f"[OK] 已生成拓扑图图片：{png_path}")
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("[提示] 未安装 mermaid-cli，跳过图片渲染。")
        print("      想生成图片可执行：npm install -g @mermaid-js/mermaid-cli")
