# natsage（NetSage）

AI 网络排障助手：输入故障现象或设备配置，AI 帮你排查；还能根据网络描述自动生成拓扑图。

## 功能

| 命令 | 作用 |
|---|---|
| `python -m natsage.cli ask "OSPF邻居起不来"` | 故障问答：AI 给出排查步骤与命令 |
| `python -m natsage.cli audit examples/campus.cfg` | 配置审查：本地规则 + 大模型深度审查 |
| `python -m natsage.cli topo "双核心-汇聚-接入"` | 拓扑生成：文字描述 → Mermaid 拓扑图 |

## 快速开始

1. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 配置 API Key：复制 `.env.example` 为 `.env`，填入你的 Key：

   ```bash
   cp .env.example .env
   # 编辑 .env，填写 DEEPSEEK_API_KEY=你的key
   ```

   DeepSeek Key 在 [platform.deepseek.com](https://platform.deepseek.com) 申请（新用户送额度）。

3. 运行：

   ```bash
   python -m natsage.cli ask "OSPF邻居起不来"
   python -m natsage.cli audit examples/campus.cfg
   python -m natsage.cli topo "双核心交换机-汇聚交换机-接入交换机-终端"
   ```

## 项目结构

```
natsage/
├── cli.py            # 命令行入口（ask / audit / topo）
├── llm.py            # 大模型 API 封装（DeepSeek / 火山方舟豆包）
├── config_parser.py  # 华为设备配置解析
├── auditor.py        # 配置审查（本地规则 + AI 深度审查）
└── topo.py           # AIGC 拓扑图生成
examples/
└── campus.cfg        # 示例配置（脱敏）
```

## 切换模型

默认使用 DeepSeek。想用火山方舟（豆包），在 `.env` 里配置 `ARK_API_KEY`，
并在代码调用处传入 `provider="ark"`。

## 免责声明

本项目用于学习和演示，AI 审查结果仅供参考，生产环境请以实际经验与官方文档为准。
ps：第一次做这个东西，做的不好
