# 示例

只借鉴边界和错误处理，不照搬框架、文件名、类型。项目不是 TypeScript 时按同等语义理解。

## 1. 前端：API 边界

不推荐——响应结构、错误和空值语义直接扩散到页面：

```ts
const response = await fetch(`/api/users/${id}`);
const user = await response.json();
title.value = user.profile.display_name;
```

推荐——在边界验证并映射成视图模型：

```ts
type UserVM = { id: string; name: string; avatar: string | null };

async function fetchUser(id: string): Promise<UserVM> {
  const res = await http.get(`/api/users/${id}`);
  if (!res.ok) throw new ApiError(res.status, "读取用户失败");
  const raw = await res.json();
  return {
    id: String(raw.id),
    name: raw.profile?.display_name ?? "未命名",
    avatar: raw.profile?.avatar_url || null,
  };
}
```

差别不在写法，在**失败和缺失有明确归属**：页面拿到的一定是 `UserVM` 或一个可展示的 `ApiError`，不用每次访问都判空。

## 2. 前端：异步状态

不推荐——只处理了成功：

```ts
const data = ref<Item[]>([]);
async function load() {
  data.value = await api.list();
}
```

推荐——把实际会出现的状态都摆出来，并防竞态：

```ts
const data = ref<Item[]>([]);
const state = ref<"idle" | "loading" | "empty" | "error">("idle");
let seq = 0;

async function load() {
  const my = ++seq;
  state.value = "loading";
  try {
    const list = await api.list();
    if (my !== seq) return;          // 旧请求回来直接丢弃
    data.value = list;
    state.value = list.length ? "idle" : "empty";
  } catch (e) {
    if (my !== seq) return;
    state.value = "error";
  }
}
```

## 3. 后端：分层

不推荐——Controller 直接查库、判业务、拼实体：

```text
Controller:
  entity = database.find(request.id)
  if entity.owner != currentUser: return 403
  entity.status = "approved"
  database.save(entity)
  return entity
```

推荐——各层只做自己的事：

```text
Controller:  受理请求 → 校验入参 → 调 UseCase → 映射响应
UseCase:     加载聚合 → 授权判断 → 执行领域规则 → 事务提交
Repository:  按条件查询 → 返回领域对象
```

顺带修掉三个隐患：实体直接外泄、授权藏在 Controller 里、事务边界不明。

## 4. Agent：工具调用

不推荐——把模型输出当命令执行：

```python
tool = resp.tool_calls[0]
result = subprocess.run(tool.arguments["cmd"], shell=True, capture_output=True)
```

推荐——schema 校验、最小权限、超时、审计：

```python
call = validate_tool_call(resp, schema=TOOL_SCHEMA)      # 不合法直接拒
if call.name not in ALLOWED_READ_TOOLS:                   # 写工具需额外确认
    return reject("readonly_mode")
if not path_within(call.args["path"], WORKSPACE):         # 路径不能逃逸
    return reject("path_escape")
out = run_with_timeout(call, seconds=20, cwd=WORKSPACE)   # 不走 shell
audit(call, out, tenant=ctx.tenant)                       # 记审计
return truncate(out, 4000)                                # 结果有上限
```

四道闸门缺一不可：**校验、权限、范围、超时**。任何一道漏掉，模型的一次幻觉就是一次事故。
