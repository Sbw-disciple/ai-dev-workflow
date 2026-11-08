# AI 开发工作流

> **AI 工作开发** —— 一套规格驱动的 AI 编程流程，附前后端、Agent、移动端代码标准。

流程管「什么时候该写」，标准管「写成什么样」。两件都做到，AI 才从「写得快」变成「写得对」。

![工作流框架](assets/workflow.svg)

## 60 秒上手

```bash
# 1. 安装
git clone git@github.com:Sbw-disciple/ai-dev-workflow.git ~/.workbuddy/skills/ai-dev-workflow

# 2. 在任意项目里初始化记录目录
python ~/.workbuddy/skills/ai-dev-workflow/scripts/init_workspace.py <你的项目>

# 3. 直接说需求，加一句触发词
#    「给记录页加按日期筛选，按流程来」
```

不需要配置，不需要改代码，不需要记命令。触发词：`按流程来` / `先写规格` / `拆一下任务` / `review 一下`。

## 它解决什么

| 失效 | 表现 | 解法 |
|---|---|---|
| 对话一长就忘 | 上下文被压缩，前面定过的约束慢慢丢失 | 规格外置到 `.ai/CONTEXT.md` |
| 自己审自己 | 方案它出，审查它做，结论必然「合理」 | 审查换一个没参与过的立场 |
| 测试变成背书 | 先写代码再补测试，测试只是给现有行为拍照 | 先定判据，跑红再实现 |
| 一次改太多 | 一个提交几十个文件，出问题无法定位 | 一张 ticket 一次改动 |
| 代码对了但不像这个项目 | 风格、分层、错误处理各写一套 | 动手前读项目，按技术栈加载标准 |
| 不知道哪里没验证 | 「都跑过了」，其实一半没跑 | 报告里强制写「未执行/未通过的检查」 |

## 两部分

### 过程：七道闸门

```
阶段 0  读项目            静默，只读文件
阶段 1  澄清              一次一问，每问自带建议答案
阶段 2  方案 + 对抗审查    换视角挑错，合并后再给人看   ── Gate 1
阶段 3  写规格 .ai/CONTEXT.md                        ── Gate 2
阶段 4  拆 tickets .ai/tickets.md
阶段 5  逐张实现           先判据，后代码
阶段 6  两路评审 .ai/review.md
阶段 7  回归验收           按规格逐条过 + 完成报告
```

人的介入点只有两个：确认方案、确认规格。其余交给模型，但每一步都有文件留痕。

### 标准：按技术栈加载

| 规范 | 覆盖 |
|---|---|
| `standards/shared.md` | 优先级、变更范围、依赖、错误处理、编码与时区金额、注释、八条红线、工作记录 |
| `standards/frontend.md` | 目录职责、组件、类型、请求与状态、表单、样式与可访问性、安全、性能、测试 |
| `standards/backend-agent.md` | 分层、API 与 DTO、认证授权、事务、并发重试、日志、Agent 工具安全、提示注入、评估 |
| `standards/mobile.md` | 生命周期、长列表、路由、权限、离线、持久化、适配、线程 |
| `standards/examples.md` | 四个对照示例：API 边界、异步状态、分层、工具调用 |
| `checklists.md` | 八段清单：开始前、方案、实现、前端、后端、Agent、移动端、完成前 |

**不要一次全读。** 改文案只读 `shared.md`（一份，约 110 行）；新功能才加载三四份。全塞进上下文会稀释注意力，重点反而抓不住。

## 四个档位

不用记触发词，也不用手动选。开始任何任务时先定档，一句话告诉你选了几档；不满意一句话就改。

| 档 | 名字 | 适用 | 走几步 | 产物 |
|---|---|---|---|---|
| **L0** | 直达 | 单文件、≤20 行、不碰公共接口 | 无 | 无 |
| **L1** | 快改 | 1–2 文件，一次能验收 | 判据 → 改 → 自验 | 一行日志 |
| **L2** | 轻量 | 3–7 文件，需要澄清但不用拆解 | 澄清 → 精简规格 → 实现 → 回归 | 精简规格 + 简版报告 |
| **L3** | 完整 | 跨模块 / 碰红线 / 要拆解 / 多人 | 七阶段全套 | 五件套 + 完整报告 |

三条规则：

- **拿不准取高一档**。L1 升 L2 的成本是十分钟，L2 装 L1 的成本是返工
- **碰八条红线自动升 L3**，升 L3 要你点头
- **执行中发现自己超范围**（多改了文件、碰了接口），立刻升档并说明，不许偷偷做完再报

## 隔天回来能接上

`.ai/` 里的东西不只是给人看的。每次开工先读它：

```
上次做到哪 / 还差什么 / 建议下一步
```

然后你只要说「继续」，它就从第一张没完成的任务接着做，不重新澄清、不重复问已经答过的问题。要开新需求才会归档旧的（移到 `.ai/archive/`，不删）。

## 产物

```
项目根/
└── .ai/
    ├── CONTEXT.md      规格：目标、范围、验收标准、约束、子任务
    ├── tickets.md      子任务清单与状态
    ├── review.md       两路评审记录与回归结果
    ├── operations.md   操作日志：时间、操作、目标、原因、结果、恢复方式
    ├── reports/        完成报告，一次任务一份
    └── archive/        旧需求归档，移入不删除
```

五个都提交进仓库——它们是团队共享的决策记录，不是临时文件。初始化：

```bash
python scripts/init_workspace.py .            # 完整版
python scripts/init_workspace.py . --lite     # 只建精简规格，适合小需求
python scripts/init_workspace.py . --check    # 只检查不写入
```

已存在的文件默认跳过，重复跑不会覆盖你的内容。

## 没有测试框架怎么办

移动端、小程序、桌面端常常没有可跑的单测。不硬套 TDD，但要保住它想要的东西——**可执行的验收判据**：

- 纯逻辑（计算、换算、解析、状态机）抽成不依赖 UI 的函数，必须有测试或验证脚本
- UI 与交互用验收判据代替：进入看到什么、点击后什么变化、异常输入怎么提示
- 每次只回归受影响页面，控制手测成本

写不出判据的地方，通常就是需求没想清楚。

## 验证脚本

```powershell
# 前端：按锁文件识别 npm/pnpm/Yarn/Bun，再从 package.json 找格式化、Lint、类型、测试、构建
./scripts/verify-frontend.ps1 -ProjectRoot "<前端根目录>"

# 后端：识别 Maven、Gradle、Python、Go、Rust、.NET、Node
./scripts/verify-backend.ps1 -ProjectRoot "<后端根目录>"

# 追加操作日志（会阻止路径逃出项目根目录）
./scripts/write-worklog.ps1 -ProjectRoot "<项目根>" -Operation "..." -Target "..." -Reason "..." -Result "..."
```

脚本只识别并执行项目**已有**的命令，不安装依赖，不自动 `--fix`。项目有 CI 时以 CI 命令为准。

## 安装到别处

| 环境 | 目录 |
|---|---|
| WorkBuddy | `~/.workbuddy/skills/ai-dev-workflow` |
| Codex | `~/.codex/skills/ai-dev-workflow` |
| 手动 | 把仓库整个目录复制过去，重启客户端 |

没有 skill 机制的工具也能用：把 `SKILL.md` 当项目规则引入（Claude Code 放 `CLAUDE.md`，Cursor 放 `.cursor/rules/`）。流程不依赖任何工具特性，只要求模型能读写文件。

## 目录结构

```
ai-dev-workflow/
├── SKILL.md                      入口：路由 + 七阶段 + 八条红线
├── README.md
├── CHANGELOG.md  LICENSE  .gitignore
├── assets/workflow.svg
├── references/
│   ├── process/                  过程层
│   │   ├── stages.md             七阶段细则、反模式、降级方案
│   │   ├── spec-template.md
│   │   ├── tickets-template.md
│   │   ├── review-checklist.md
│   │   ├── antipatterns.md
│   │   └── origin.md
│   ├── standards/                标准层
│   │   ├── shared.md
│   │   ├── frontend.md
│   │   ├── backend-agent.md
│   │   ├── mobile.md
│   │   └── examples.md
│   ├── checklists.md
│   └── report-template.md
└── scripts/
    ├── init_workspace.py
    ├── verify-frontend.ps1
    ├── verify-backend.ps1
    └── write-worklog.ps1
```

## 来源

过程骨架来自一位开发者公开分享的九步实践（`/grill-me` → `/to-spec` → `/to-tickets` → `/tdd` → `/code-review`），代码标准来自 [lengchang-haoyuan](https://github.com/lengchang-haoyuan/frontend-backend-code-standards-Skill-) 的规范集。本仓库剥离了与工具的绑定，合成七阶段流程 + 分层标准，并补充了移动端与无测试框架的降级方案。详见 [references/process/origin.md](references/process/origin.md)。

## License

[MIT](LICENSE)
