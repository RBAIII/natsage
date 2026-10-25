"""
config_parser.py - 设备配置解析

从华为 vrpcfg.cfg 文本中提取 ACL、VLAN、接口、NAT 等信息，供配置审查使用。
"""
import re


def read_file(path):
    """读取配置文件内容（文本）。"""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_config(text):
    """
    解析配置文本，返回字典：
    {
        "acls": [...],       # ACL 相关行（acl number / rule ...）
        "vlans": [...],      # VLAN 编号列表
        "interfaces": [...], # interface 行
        "nat_rules": [...],  # NAT 相关行
    }
    """
    result = {"acls": [], "vlans": [], "interfaces": [], "nat_rules": []}

    current_acl = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # 抓 ACL：acl number 3001 后面的 rule 行都归入当前 ACL
        if line.startswith("acl number"):
            current_acl = line
            result["acls"].append(line)
        elif current_acl and line.startswith("rule "):
            result["acls"].append("  " + line)

        # 抓 VLAN：vlan batch 10 20 30 或 vlan 10
        if line.startswith("vlan batch"):
            result["vlans"] += line.split()[2:]
        else:
            m = re.match(r"^vlan\s+(\d+)", line)
            if m:
                result["vlans"].append(m.group(1))

        # 抓接口
        if line.startswith("interface "):
            result["interfaces"].append(line)

        # 抓 NAT 规则
        if "nat outbound" in line or "nat server" in line:
            result["nat_rules"].append(line)

    return result
