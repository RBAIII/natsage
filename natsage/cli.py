"""
cli.py - natsage 命令行入口

用法示例：
  python -m natsage.cli ask "OSPF邻居起不来"
  python -m natsage.cli audit examples/campus.cfg
  python -m natsage.cli topo "双核心交换机-汇聚-接入-终端"
"""
import argparse

from natsage import auditor, config_parser, topo
from natsage.llm import chat


def main():
    parser = argparse.ArgumentParser(
        prog="natsage",
        description="NetSage：AI 网络排障助手（故障问答 / 配置审查 / 拓扑生成）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # 子命令 1：ask 故障问答
    p_ask = sub.add_parser("ask", help="输入故障现象，AI 给出排查步骤")
    p_ask.add_argument("question", help="故障描述，例如：OSPF邻居起不来")

    # 子命令 2：audit 配置审查
    p_audit = sub.add_parser("audit", help="审查华为设备配置文件")
    p_audit.add_argument("config_file", help="配置文件路径，例如 examples/campus.cfg")

    # 子命令 3：topo 拓扑生成
    p_topo = sub.add_parser("topo", help="根据描述生成网络拓扑图")
    p_topo.add_argument("description", help="网络描述，例如：双核心交换机-汇聚-接入-终端")

    args = parser.parse_args()

    if args.command == "ask":
        system = (
            "你是网络工程师，根据故障现象给出排查步骤：先列出可能原因，"
            "再给出具体排查命令（华为/思科均可），最后给出修复建议。用中文。"
        )
        print(chat(args.question, system=system))

    elif args.command == "audit":
        text = config_parser.read_file(args.config_file)
        parsed = config_parser.parse_config(text)

        print("===== 本地规则检查 =====")
        issues = auditor.local_check(parsed)
        if issues:
            for issue in issues:
                print(" -", issue)
        else:
            print(" - 未发现明显的本地规则问题")

        print("\n===== 大模型深度审查（请稍候）=====")
        print(auditor.ai_check(text))

    elif args.command == "topo":
        print("正在调用大模型生成拓扑图...")
        code = topo.generate_mermaid(args.description)
        topo.save_topo(code)


if __name__ == "__main__":
    main()
