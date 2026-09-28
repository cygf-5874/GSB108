"""tomslice 的错误类型。

`TomlError` 的字段名与含义是契约的一部分，不得改（可以新增子类）。
"""


class TomlError(Exception):
    """解析 TOML 子集时出错。

    属性
    ----
    msg:
        人类可读的错误信息。
    line:
        出错位置所在行，从 **1** 起。
    col:
        出错位置所在列，从 **1** 起，指向**出错 token 的首字符**。
    """

    def __init__(self, msg: str, line: int, col: int) -> None:
        super().__init__(msg)
        self.msg = msg
        self.line = line
        self.col = col

    def __str__(self) -> str:
        return "line %d, col %d: %s" % (self.line, self.col, self.msg)
