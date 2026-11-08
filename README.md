# AI 开发工作流（个人版）

> 先定内容，再拆成看得见的几步，做完拿证据对一遍。

装进 WorkBuddy 的技能。作用只有三件：**想清楚做什么**、**拆成能落地的步**、**留下能核对的证据**。

不是项目管理工具，不是团队协作规范，也不打算兼容别的客户端。

## 四个动作

| # | 动作 | 做什么 | 落在哪 |
|---|---|---|---|
| 1 | 定内容 | 交付物、验收标准、不做什么、放弃条件 | `TASK.md` |
| 2 | 拆步 | 2–6 步，每步具体到文件和动作 | `TASK.md` 的「分几步」 |
| 3 | 做 | 一次一步，先写判据再改，做完打勾 | `- [x]` |
| 4 | 验 | 逐条对验收、贴证据、写复盘 | `REPORT.md` |

第 2 步结束要停一次，把步骤清单贴出来等确认。拆错了后面全白做。

## 定内容时问五个问题

1. 交付物是什么，能拿在手里的是什么
2. 谁验收、按什么标准（老师按评分点、比赛按评分表、自己的东西按你自己）
3. 最晚什么时候要
4. 最小可交付：砍到只剩什么也算完成
5. 放弃条件：出现什么情况就停

第 4、5 条最容易被跳过，也最容易后悔。

## 三档

| 档 | 什么情况 | 做什么 |
|---|---|---|
| 随手 | 改错字、调数值、单文件 ≤20 行 | 直接改，不建 `.ai/` |
| 小活 | 1–3 个文件，一次能验完 | 只填 `TASK.md` 前半 |
| 正经 | 跨模块、要交付、碰红线 | 四个动作全走 |

## 两个文件

```
项目根/.ai/
├── TASK.md     定内容 + 分几步（带勾选框）
└── REPORT.md   改了什么、每条验收的证据、复盘三行、没验的
```

## 60 秒上手

```bash
# 1. 建骨架
python ~/.workbuddy/skills/ai-dev-workflow/scripts/task.py .

# 2. 填 TASK.md：五条内容 + 2~6 步

# 3. 一步一勾，做完填 REPORT.md

# 4. 自检，必须 exit 0
python ~/.workbuddy/skills/ai-dev-workflow/scripts/task.py . --check
```

`--check` 会真的拦人：

| 检查 | 退出码 |
|---|---|
| 没有 `.ai/TASK.md` | 2 |
| 验收标准少于 3 条 | 1 |
| 模板占位符没填 | 1 |
| **还有步骤没打勾就写了报告** | 1 |
| 报告缺某条验收项 | 1 |
| 写了「通过」但没证据 | 1 |
| **「复盘」三行没写全** | 1 |
| 「没验的」没写原因 | 1 |
| 全部合格 | 0 |

## 五条红线

删文件 · 装依赖改全局配置 · 改别人会用的东西 · 碰不属于你的仓库 · 没验证就说做完了。

碰到任一条，先说「事实 / 影响 / 两个选项 / 推荐哪个」，等确认再动。

## 目录

```
SKILL.md                 主文件，读完就够用
references/rules.md      编码、提交、Windows 坑
references/templates.md  两个模板 + 填满的样例 + 拆步写法对照
scripts/task.py          建骨架 / 自检
```

## 安装

```bash
git clone git@github.com:Sbw-disciple/ai-dev-workflow.git ~/.workbuddy/skills/ai-dev-workflow
```

或者把仓库里的目录整个复制到 `~/.workbuddy/skills/ai-dev-workflow`，重启 WorkBuddy，在技能列表里确认加载。

只面向 **WorkBuddy + DeepSeek**，不提供其他客户端的安装路径。

## 来源

- [snarktank/ai-dev-tasks](https://github.com/snarktank/ai-dev-tasks)：PRD → 任务清单 → 逐项打勾，0.6.0 的四个动作直接来自这里
- [github/spec-kit](https://github.com/github/spec-kit)：规格驱动开发
- [lengchang-haoyuan 的代码规范技能](https://github.com/lengchang-haoyuan/frontend-backend-code-standards-Skill-)：规则要写成可执行的话

被删掉的前端 / 后端 / Agent 规范仍在 `v0.4.1` 标签里，需要时 `git show v0.4.1:<路径>` 取回。
