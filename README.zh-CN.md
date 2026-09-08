# CadFlow Skill

面向 [CadFlow](https://pypi.org/project/cadflow/0.2.0/) 的一份可独立安装
[Agent Skill](https://agentskills.io/specification)。同一目录可用于 Codex、Pi
和 Claude Code。宿主 agent 按 Skill 准备 CadFlow 环境，再用自己的文件与终端
工具编写、运行普通 Python 程序。

CadFlow 原生 Python API 是唯一建模接口。本仓库不再提供 CAD agent、后端、
Viewer 或执行服务。

[English](README.md) · 简体中文

## 内容

```text
skills/cadflow/
├── SKILL.md                 # 触发条件、环境准备、最小用法
├── agents/openai.yaml       # Codex / ChatGPT 可选展示元数据
├── references/              # API、易错点、测量与导出
└── examples/                # 零件与装配示例
```

Skill 对应 **CadFlow 0.2.0**。PyPI 当前 wheel：

- Linux x86_64、CPython 3.12（`manylinux_2_31`）
- macOS 12+ arm64、CPython 3.13

元数据里的 Python 范围更宽，但 0.2.0 只发布了这两个 wheel。其他组合安装失败
属于发布包限制。

## 安装 Skill

正文在 `skills/cadflow`。本仓库同时把该目录链接到 `.agents/skills/cadflow`、
`.pi/skills/cadflow` 和 `.claude/skills/cadflow`，克隆后 Codex / Pi / Claude Code
可按项目 Skill 加载，无需复制三份。在其他工作目录里，把同一文件夹链过去：

### Pi

```bash
mkdir -p ~/.pi/agent/skills
ln -sfn /path/to/CadFlow-Harness/skills/cadflow ~/.pi/agent/skills/cadflow
```

项目内：`mkdir -p .pi/skills && ln -sfn ../skills/cadflow .pi/skills/cadflow`。
也可用 `pi --skill /path/to/skills/cadflow`。命令：`/skill:cadflow`。

### Codex

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/CadFlow-Harness/skills/cadflow ~/.agents/skills/cadflow
```

项目内：`mkdir -p .agents/skills && ln -sfn ../skills/cadflow .agents/skills/cadflow`。
Codex 会扫描从工作目录到仓库根的 `.agents/skills`，以及 `~/.agents/skills`。
用 `$cadflow` 或 `/skills`。

### Claude Code

```bash
mkdir -p ~/.claude/skills
ln -sfn /path/to/CadFlow-Harness/skills/cadflow ~/.claude/skills/cadflow
```

项目内：`mkdir -p .claude/skills && ln -sfn ../skills/cadflow .claude/skills/cadflow`。
命令：`/cadflow`。Claude Code 需要先登录（`claude` / `/login`）才会加载项目 Skill。

安装后的 Skill 不得依赖该目录之外的仓库文件。

## 使用

向 agent 提出零件或装配需求。它应当：

1. 在隔离环境中执行 `uv pip install cadflow==0.2.0`（或 `pip`）。
2. 编写 `import cadflow as cad` 的普通 Python 程序。
3. 用该环境的解释器运行。
4. 用测量结果核对几何，并用 CadFlow 重新打开导出的 STEP。

```bash
uv venv --python 3.13 .venv     # Linux x86_64 用 3.12
uv pip install --python .venv/bin/python cadflow==0.2.0
.venv/bin/python - <<'PY'
import cadflow as cad
with cad.Model() as model:
    print(cad.__version__, model.box(2, 3, 4).volume)
PY
```

不再需要旧后端、Viewer、额外模型 API Key 或自建执行服务。宿主自己的模型认证
不属于 Skill 的运行依赖。

## 维护检查

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python cadflow==0.2.0 pytest pyyaml
.venv/bin/python -m pytest
.venv/bin/python skills/cadflow/examples/mounting_plate.py
.venv/bin/python skills/cadflow/examples/hinge_assembly.py
```

这些测试只检查分发完整性和示例能否对着发布包跑通，不是用户建模管线。

## 许可证

MIT，见 [LICENSE](LICENSE)。CadFlow 是独立的 PyPI 包。
