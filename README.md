# AI 开发工作流（个人版）

> 三档、两个文件、一条命令。给一个人用，不追求覆盖所有场景。

这是一份装进 WorkBuddy 的技能，作用只有一个：**让 AI 动手前先把「怎么算做完」写下来，做完留下能验证的证据。**

不是项目管理工具，不是团队协作规范，也不打算兼容别的客户端。

## 三档

| 档 | 什么情况 | 做什么 |
|---|---|---|
| 随手 | 改错字、调数值、单文件 ≤20 行 | 直接改，不留痕 |
| 小活 | 1–3 个文件，一次能验完 | 一个 `.ai/TASK.md` |
| 正经 | 跨模块、要交付、碰红线 | `TASK.md` + `REPORT.md` |

拿不准往上取一档。走错档的代价：多写十行字，比返工便宜。

## 两个文件

```
项目根/.ai/
├── TASK.md     要做什么、怎么算做完（3–5 条可判定的验收标准）、不做什么
└── REPORT.md   改了什么、每条验收的证据、没验的为什么没验
```

就这两个。没有 tickets、没有 review、没有 operations 日志——一个人写代码时，那些多半没人看。

## 60 秒上手

```bash
# 1. 在项目里建骨架
python ~/.workbuddy/skills/ai-dev-workflow/scripts/task.py .

# 2. 填 .ai/TASK.md 的「怎么算做完」，至少 3 条

# 3. 干活。干完填 .ai/REPORT.md

# 4. 自检，必须 exit 0
python ~/.workbuddy/skills/ai-dev-workflow/scripts/task.py . --check
```

`--check` 会真的拦人，不是摆设：

| 检查 | 结果 |
|---|---|
| 没有 `.ai/TASK.md` | exit 2，任务未开始 |
| 验收标准少于 3 条 | exit 1 |
| 模板占位符没填 | exit 1，并指出第一处 |
| 报告缺某条验收项 | exit 1，并指出编号 |
| 写了「通过」但没证据 | exit 1 |
| 「没验的」没写原因 | exit 1 |
| 全部合格 | exit 0 |

退出码：`0` 通过 / `1` 有问题 / `2` 只是提示（没开始或没收尾）。

## 五条红线

删文件 · 装依赖改全局配置 · 改别人会用的东西 · 碰不属于你的仓库 · 没验证就说做完了。

碰到任一条，先说「事实 / 影响 / 两个选项 / 推荐哪个」，等确认再动。

## 目录

```
SKILL.md                 主文件，读完这一个就够用
references/rules.md      代码怎么写、提交怎么写、Windows 有哪些坑
references/templates.md  两个模板 + 填满的样例 + 验收标准写法对照
scripts/task.py          建骨架 / 自检
```

## 安装

```bash
git clone git@github.com:Sbw-disciple/ai-dev-workflow.git ~/.workbuddy/skills/ai-dev-workflow
```

或者把仓库里的目录整个复制到 `~/.workbuddy/skills/ai-dev-workflow`，重启 WorkBuddy，在技能列表里确认加载。

只面向 **WorkBuddy + DeepSeek**，不提供其他客户端的安装路径。

## 来源

流程骨架受了三份公开工作的影响：[github/spec-kit](https://github.com/github/spec-kit)（规格驱动）、
[snarktank/ai-dev-tasks](https://github.com/snarktank/ai-dev-tasks)（PRD → 任务 → 逐条实现）、
[lengchang-haoyuan 的代码规范技能](https://github.com/lengchang-haoyuan/frontend-backend-code-standards-Skill-)（规则要写成可执行的话）。

0.5.0 做了大幅收缩：从 23 个文件 1554 行删到 9 个文件 484 行。
被删掉的前端 / 后端 / Agent 规范仍在 `v0.4.1` 标签里，需要时用 `git show v0.4.1:<路径>` 取回。
