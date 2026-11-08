# Changelog

## 0.2.0 — 2026-11-08

把「过程」和「标准」合成一个 skill。

### 新增

- `references/standards/` 标准层五份：`shared.md`、`frontend.md`、`backend-agent.md`、`mobile.md`、`examples.md`
- `references/checklists.md` 八段清单：开始前、方案、实现、前端、后端、Agent、移动端、完成前
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

- 与 Codex 绑定的路径与调用语法；`agents/openai.yaml` 不再携带
- 前后端示例合并为 `standards/examples.md`

## 0.1.0 — 2026-11-07

首个版本。

- 七阶段流程：读项目 → 澄清 → 方案与对抗审查 → 写规格 → 拆 tickets → 逐张实现 → 两路评审 → 回归
- 三个产物模板：`CONTEXT.md`、`tickets.md`、`review.md`
- `scripts/init_workspace.py`：一键初始化 `.ai/`，支持 `--lite`
- 降级模式：无测试框架时用可观察判据替代单测
- 参考文档：规格模板、拆分模板、评审清单、五种误用、来源说明
