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
