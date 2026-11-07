#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在当前项目里初始化 .ai/ 工作目录。

用法：
    python init_workspace.py [项目目录]       # 默认当前目录
    python init_workspace.py . --lite        # 精简版规格，适合小需求

只新增文件，已存在的同名文件不会被覆盖。
"""
import argparse
import sys
from pathlib import Path

CONTEXT_FULL = """# <需求名称>

> 状态：草稿
> 建立时间：{date}
> 最后更新：{date}

## 1. 目标

<!-- 一句话，不用术语。站在用户角度说清「做完之后，什么变得不一样了」。 -->

## 2. 范围

### 做什么

- 

### 不做什么

<!-- 与上一节同等重要。写具体，不要写「其他不做」。 -->

- 
- 

## 3. 验收标准

<!-- 每条都要能回答「怎么证明它做到了」。写不出证明方式的不写。 -->

| 编号 | 标准 | 怎么证明 |
|---|---|---|
| AC-1 |  |  |
| AC-2 |  |  |

## 4. 约束

| 类别 | 内容 |
|---|---|
| 技术栈 |  |
| 目录 |  |
| 命名 |  |
| 不可动 |  |
| 性能 |  |

## 5. 子任务与依赖

| 编号 | 子任务 | 依赖 | 验收判据 |
|---|---|---|---|
| T1 |  | — |  |
| T2 |  | T1 |  |

## 6. 假设

<!-- 用户没有明确回答、由 AI 代为决定的事项，集中写在这里，方便日后追溯。 -->
"""

CONTEXT_LITE = """# <需求名称>

> 状态：草稿
> 建立时间：{date}

## 目标

<!-- 一句话说清做完之后什么变得不一样了。 -->

## 范围

做什么：

- 

不做什么：

- 

## 验收标准

| 编号 | 标准 | 怎么证明 |
|---|---|---|
| AC-1 |  |  |

## 约束

- 技术栈：
- 不可动：

## 子任务

| 编号 | 子任务 | 依赖 | 验收判据 |
|---|---|---|---|
| T1 |  | — |  |
"""

TICKETS = """# <需求名称> · 子任务

> 对应规格：./CONTEXT.md
> 总数：0　完成：0

## T1　<子任务名称>

| 项 | 内容 |
|---|---|
| 状态 | todo |
| 涉及文件 |  |
| 依赖 | — |
| 可并行 | 否 |
| 判据 |  |

---

## 待办（实现过程中发现，本轮不做）

- [ ] 
"""

REVIEW = """# 评审记录

> 评审对象：
> 评审时间：{date}
> 规格：./CONTEXT.md

## A 路 · 仓库规范

### 阻断

- 

### 建议

- 

## B 路 · 规格一致性

| 验收标准 | 结论 | 说明 |
|---|---|---|
| AC-1 | 通过 / 多做 / 少做 / 做偏 |  |

## 结论

通过 / 有条件通过（列条件） / 打回（列问题）

## 回归验收

| 验收标准 | 验证方式 | 结果 | 证据 |
|---|---|---|---|
| AC-1 |  |  |  |
"""


def write(path: Path, content: str) -> str:
    if path.exists():
        return "skip"
    path.write_text(content, encoding="utf-8")
    return "create"


def main() -> int:
    ap = argparse.ArgumentParser(description="初始化 .ai/ 工作目录")
    ap.add_argument("target", nargs="?", default=".", help="项目目录，默认当前目录")
    ap.add_argument("--lite", action="store_true", help="生成精简版规格，适合小需求")
    args = ap.parse_args()

    root = Path(args.target).expanduser().resolve()
    if not root.is_dir():
        print(f"[x] 目录不存在：{root}")
        return 1

    date = __import__("datetime").date.today().isoformat()
    ai = root / ".ai"
    ai.mkdir(exist_ok=True)

    spec = CONTEXT_LITE if args.lite else CONTEXT_FULL
    plan = {
        ai / "CONTEXT.md": spec.format(date=date),
        ai / "tickets.md": TICKETS,
        ai / "review.md": REVIEW.format(date=date),
    }

    for path, content in plan.items():
        result = write(path, content)
        mark = "[+]" if result == "create" else "[=]"
        print(f"{mark} {path.relative_to(root)}")

    print("\n下一步：填写 CONTEXT.md 的范围与验收标准，确认后再拆 tickets。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
