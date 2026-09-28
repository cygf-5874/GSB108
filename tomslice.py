"""tomslice —— TOML 子集解析器（Python 3 标准库）。

本文件只给出公开签名，方法体抛 `NotImplementedError`，需要按 README
「对外契约」实现。约束：不许用 `tomllib` / `tomli` / `toml` 等任何现成解析器。
"""

from __future__ import annotations

from typing import Any, Dict

from errors import TomlError


def loads(text: str) -> Dict[str, Any]:
    """把一个 TOML **子集**文本解析成等价的 `dict`（保持插入顺序）。

    子集之外的输入（例如日期时间）抛 `TomlError`，并带上 `line` / `col`。
    """
    raise NotImplementedError
