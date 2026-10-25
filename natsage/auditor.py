"""
auditor.py - 配置审查

先用几条本地规则做快速检查（不花 API 费用），
再调用大模型对完整配置做深度审查。
"""
from natsage import config_parser
from natsage.llm import chat


def local_check(parsed):
    """本地规则快速检查，返回问题列表。"""
    issues = []

    # 规则1：有接口但没有任何 NAT 配置 -> 内网可能无法访问外网
    if parsed["interfaces"] and not parsed["nat_rules"]:
        issues.append("提示：配置了多个接口但未发现 NAT 配置，内网用户可能无法访问外网。")

    # 规则2：没有 VLAN 配置
    if len(set(parsed["vlans"])) == 0:
        issues.append("提示：未发现任何 VLAN 配置，若该设备是交换机请检查 VLAN 划分。")

    # 规则3：ACL 只有 deny 没有 permit -> 可能把所有流量都拦掉了
    acl_text = "\n".join(parsed["acls"])
    has_deny = "deny" in acl_text
    has_permit = "permit" in acl_text
    if has_deny and not has_permit:
        issues.append("警告：ACL 中只有拒绝规则没有放行规则，可能导致所有流量被拦截。")

    return issues


def ai_check(config_text, provider="deepseek"):
    """把完整配置发给大模型做深度审查，返回审查结果文本。"""
    system = (
        "你是资深网络工程师，请从配置正确性、安全隐患、性能问题三个角度审查华为设备配置，"
        "逐条列出问题并给出修改建议。用中文回答，编号列出。"
    )
    prompt = "请审查以下华为设备配置文件：\n\n" + config_text
    return chat(prompt, system=system, provider=provider)
