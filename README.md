# tomslice

`tomslice` 是一个纯标准库的 **TOML 子集**解析器：只读不写，解析失败时给出
**具体的行号与列号**。标准库的 `tomllib` 既不负责给你定位、也不接受「只解析子集」，
所以这里自己写一份。

- 语言 / 运行：Python 3，只用标准库（**不许**用 `tomllib` / `tomli` / `toml`），无第三方依赖。
- 自检：`bash scripts/check.sh`（内部调用 `check/check.py`，那是固定验收程序，**别改**）。
- 起点：`tomslice.py` 只有类型与签名，方法体抛 `NotImplementedError`；`python3 -c "import tomslice"` 通过。

## 怎么跑

```bash
python3 -c "import tomslice"            # 退出码 0
bash scripts/check.sh                    # 固定验收（10 个场景）
bash scripts/check.sh -list              # 列出全部场景
bash scripts/check.sh --only errloc      # 只跑一组
```

前提：Python 3.7+（本仓库按 3.13 验证）。不引入任何第三方依赖。

## 目录

```
.
├── .gitattributes
├── .gitignore
├── README.md
├── PROMPT.md             本题的 User Prompt（逐字）
├── errors.py             TomlError（带 line/col，已给全，勿改字段）
├── tomslice.py           公开签名（方法体抛 NotImplementedError，待实现）
├── check/check.py        固定验收程序：10 个场景（勿改）
└── scripts/check.sh      薄封装
```

## 对外契约（10 条）

1. `loads(text: str) -> dict`：解析一个 **TOML 子集**，返回等价于 `dict` 的结构。
2. 支持：`key = value`（裸键、引号键）、`[table]`、`[[array of tables]]`、注释 `#`、
   基本字符串 `"…"`（含转义 `\n \t \\ \" \uXXXX`）、字面字符串 `'…'`、
   整数（十进制 / `0x` / `0o` / `0b`、下划线分隔）、浮点（含 `inf` / `nan` / 指数）、
   布尔、数组（可跨行、可尾逗号）。
3. 日期时间**不在**子集内 —— 遇到 `1979-05-27` 这类输入返回 `TomlError`（**不要**尝试解析）。
4. 重复键（同层同名）返回 `TomlError`；表与键同名也报错。
5. **错误定位**：`TomlError.line` 从 1 起、`col` 从 1 起，指向**出错 token 的首字符**；
   多行数组里的错误要报在**实际出错的那一行**。
6. 字符串里的转义非法（如 `"\x"`、`\u` 不足 4 位）报 `TomlError`，位置指向转义序列起点。
7. 整数前导 0（`01`）非法、浮点 `1.`、`.1` 非法、`1e` 非法 → 均报 `TomlError`。
8. 返回的 `dict` 必须**保持插入顺序**（Python 3.7+ 语义），且 `[table]` 嵌套层级正确。
9. 空输入、只有注释、只有空白 → 返回 `{}`。
10. **禁止**使用 `tomllib` / `tomli` / `toml` 等任何现成解析器（含标准库的 `tomllib`）——
    本题就是要自己写；结果与 `dict` 迭代顺序无关。

> `errors.py` 里 `TomlError` 的字段（`msg` / `line` / `col`）是契约的一部分，不得改。
> `loads` 只接受 `str`；可以新增模块 / 辅助函数 / 类。

## 验收

`check/` 是固定验收程序，**不要修改**。场景分五组，共 10 个：

| 组 | 场景 | 覆盖 |
| --- | --- | --- |
| `value` | `strings-and-literal` | 契约 2、6：转义与字面串、非法转义报错 |
| `value` | `integers-and-underscores` | 契约 2、7：各进制、下划线、前导 0 非法 |
| `value` | `floats-inf-nan` | 契约 2、7：浮点含 `inf`/`nan`、`1.`/`.1`/`1e` 非法 |
| `struct` | `table-nesting` | 契约 2、8：嵌套表、数组（跨行 / 尾逗号 / 嵌套）、插入顺序 |
| `struct` | `array-of-tables` | 契约 2、8：`[[table]]` 追加 |
| `dup` | `duplicate-key` | 契约 4：同层重复键报错 |
| `dup` | `table-key-collision` | 契约 4：表与键同名报错 |
| `errloc` | `multiline-array` | 契约 3、5：跨行数组里定位到实际出错行、日期报错 |
| `errloc` | `escape-col` | 契约 5、6：非法转义指向转义起点 |
| `edge` | `empty-comment-datetime` | 契约 3、9：空 / 纯注释 → `{}`；日期时间报错 |

```bash
python3 -c "import tomslice"   # 退出码 0
bash scripts/check.sh           # 退出码 0，10 个场景全过
```

## User Prompt

```
能读不能写、还不给行号 —— 这就是要自己写一份的原因。tomslice 是 Python 3 的
TOML 子集解析器，只用标准库，构建不需要额外步骤，
自检走 `scripts/check.sh`（`check/` 是固定验收程序，别改）。

`tomslice.py` 现在只有类型和签名，方法体全抛 `NotImplementedError`；
`errors.py` 里的 `TomlError` 带 `line`/`col` 两个字段，已经给全。

任务：按 README「对外契约」的 10 条实现，让固定件全过。

验收：
- python3 -c "import tomslice" 退出码 0；
- python3 check/check.py 退出码 0，10 个场景全过（value 3 + struct 2 + dup 2 + errloc 2 + edge 1）。

约束：
1. 不改 `check/`、不改 `errors.py` 里 `TomlError` 的字段；可以新增模块。
2. 只用标准库，**不许**用 `tomllib`、`tomli`、`toml` 等任何现成解析器。
3. 别自作主张支持日期时间 —— 子集外的东西一律报错。
4. 错误位置要能定位到具体的行列。
```
