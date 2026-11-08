# Changelog

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
