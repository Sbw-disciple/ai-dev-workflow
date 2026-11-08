# Changelog

## 0.6.0 — 2026-11-08

补上前半段：动工前怎么定内容、怎么拆步。

### 变更

- 新增「四个动作」：定内容 → 拆步 → 做 → 验。SKILL.md 的骨架照此重排
- `TASK.md` 增加「分几步」一节，每步一个勾选框，做完立刻改 `[x]`
- 定内容给出五个问题：交付物、谁验收、截止时间、最小可交付、放弃条件
- 拆步要求 2–6 步、具体到文件与动作，拆完停下等确认
- `REPORT.md` 增加「复盘」三行：哪个判断错了 / 下次怎么改 / 进 rules.md 吗
- `task.py --check` 新增三条检查：有步骤没打勾、复盘三行没写全、`TASK.md` 没有「分几步」
- 拆步与验收标准的写法对照补进 `templates.md`

### 说明

结构取自 [snarktank/ai-dev-tasks](https://github.com/snarktank/ai-dev-tasks)（PRD → 任务 → 逐项执行），
压成两个文件、去掉分支管理与双层任务编号。

## 0.5.0 — 2026-11-08

按「一个人用」重做，大幅收缩。

### 变更

- 四档压成三档：随手 / 小活 / 正经。去掉 L0–L3 编号，改用「多大事」这类直觉判断
- 七阶段压成三阶段：想清楚 / 做 / 验
- 产物从五件套压成两个文件：`TASK.md`（验收标准）+ `REPORT.md`（证据）
- 八条红线剪成五条，只留一个人真会踩的：删文件、装依赖改配置、改别人会用的东西、碰别人仓库、没验证就交付
- 新增 `scripts/task.py --check`：检查验收标准数量、占位符、报告缺项、无证据的「通过」、没写原因的「未验」。退出码 0/1/2
- `references/` 从 12 份压成 2 份：`rules.md`（编码、提交、Windows 坑）、`templates.md`（模板与样例）
- README 重写，去掉流程图与团队相关表述

### 移除

- `references/process/`（5 份）、`references/standards/`（4 份）、`checklists.md`、`report-template.md`
- `scripts/init_workspace.py`、`verify-frontend.ps1`、`verify-backend.ps1`、`write-worklog.ps1`
- `assets/workflow.svg`（画的是七阶段，已不适用）

删掉的内容都在 `v0.4.1` 标签里，需要时 `git show v0.4.1:<路径>` 取回。

### 数字

23 个文件 / 文档 1554 行 → 9 个文件 / 文档 484 行。

## 0.4.1 — 2026-11-08

补上 L2 的确认点。

### 变更

- L2 档在阶段 3 结束后停一次：把「范围外」与 3–5 条验收标准贴给用户，10 行以内，拿到一句「行」再动代码
- 定档规则同步：L1 自己定，L2 有确认点，L3 需点头
- `stages.md` 阶段 3 的 Gate 2 按档位区分详略

### 背景

0.4.0 跑真实项目时发现：L2 是主力档，但只有 L1 的「直接做」和 L3 的双 Gate 两端，中间是空的，用户全程没有介入机会。

## 0.4.0 — 2026-11-08

收窄适用范围，只面向 WorkBuddy + DeepSeek。

### 移除

- `references/standards/mobile.md`：ArkTS / 鸿蒙方向不再使用
- 检查清单里的「移动端」一节，报告模板中的移动端选项
- 与特定客户端绑定的安装路径与调用语法，只保留 WorkBuddy 的 `~/.workbuddy/skills`

### 说明

- 明确声明适用环境为 WorkBuddy + DeepSeek，不再兼容其他客户端的目录约定
- 来源仓库已获作者授权

## 0.3.0 — 2026-11-08

解决两个上手问题：**第一次怎么开始**、**第二天怎么接上**。

### 新增

- **四档流程**：L0 直达 / L1 快改 / L2 轻量 / L3 完整，按改动规模自动定档并声明，用户一句话可改档
- **续跑**：开工先读 `.ai/`，输出「上次做到哪 / 还差什么 / 建议下一步」，说「继续」就接着做，不重新澄清
- **归档**：开新需求时把旧的 `.ai/` 三件套移到 `archive/`，不删除
- `references/process/stages.md`：七阶段细则从 `SKILL.md` 下沉，按档位跳着读

### 变更

- `SKILL.md` 改为「续跑 + 定档 + 阶段速查表 + 八条红线 + 加载索引」，七阶段正文移入 `stages.md`
- 阶段 1 到 7 标注了各档位做到哪一步就停
- 报告分两档：L1 三行、L2 简版五节、L3 完整八节
- 碰八条红线自动升 L3，且升 L3 需用户确认

## 0.2.0 — 2026-11-08

把「过程」和「标准」合成一个 skill。

### 新增

- `references/standards/` 标准层五份：`shared.md`、`frontend.md`、`backend-agent.md`、`mobile.md`、`examples.md`
- `references/checklists.md` 七段清单：开始前、方案、实现、前端、后端、Agent、完成前
- `references/report-template.md` 完成报告模板，强制区分「通过 / 失败 / 未运行」
- `scripts/write-worklog.ps1` 追加操作日志，阻止路径逃出项目根目录
- `scripts/verify-frontend.ps1` 按锁文件识别包管理器，跑格式、Lint、类型、测试、构建
- `scripts/verify-backend.ps1` 识别 Maven、Gradle、Python、Go、Rust、.NET、Node
- `.ai/operations.md` 与 `.ai/reports/` 进入产物目录

### 变更

- `SKILL.md` 从 252 行压到「路由 + 七阶段 + 八条红线」，细则全部下沉到 `references/`
- 按任务形状决定加载量：小改只读一份规范，大改才全量加载
- `references/` 拆成 `process/` 与 `standards/` 两层，五个过程模板移到 `process/`
- `init_workspace.py` 增加 `--check` 只检查模式；默认同时建 `operations.md` 与 `reports/`
- 工作记录统一到 `.ai/`，不再使用 `docs/ai-worklogs/`

### 移除

- 与特定客户端绑定的路径与调用语法；`agents/openai.yaml` 不再携带
- 前后端示例合并为 `standards/examples.md`

## 0.1.0 — 2026-11-07

首个版本。

- 七阶段流程：读项目 → 澄清 → 方案与对抗审查 → 写规格 → 拆 tickets → 逐张实现 → 两路评审 → 回归
- 三个产物模板：`CONTEXT.md`、`tickets.md`、`review.md`
- `scripts/init_workspace.py`：一键初始化 `.ai/`，支持 `--lite`
- 降级模式：无测试框架时用可观察判据替代单测
- 参考文档：规格模板、拆分模板、评审清单、五种误用、来源说明
