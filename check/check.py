#!/usr/bin/env python3
"""tomslice 的固定验收程序。

场景（10 个）：value 3 + struct 2 + dup 2 + errloc 2 + edge 1。

本文件属于固定判据，解题者不得修改。期望值全部硬编码；判据不依赖墙钟、
机器速度、`dict` 迭代顺序或随机源。
"""

import argparse
import math
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from errors import TomlError  # noqa: E402
from tomslice import loads  # noqa: E402


def _verdict(ok, expected, actual):
    return (bool(ok), expected, actual)


def _expect_error(text):
    """返回 None 表示确实抛了 TomlError；否则返回问题描述。"""
    try:
        loads(text)
    except TomlError:
        return None
    except NotImplementedError:
        raise
    except Exception as exc:  # noqa: BLE001
        return "抛了 %s" % type(exc).__name__
    return "未抛"


# --------------------------------------------------------------------------
# value group
# --------------------------------------------------------------------------

_STR_TEXT = (
    'a = "line\\nbreak"\n'
    'b = "tab\\there"\n'
    'c = "quote\\"end"\n'
    'd = "back\\\\slash"\n'
    'e = "\\u0041\\u00e9"\n'
    "f = 'raw\\n literal'\n"
    "g = ''\n"
    'h = ""\n'
)

_STR_WANT = {
    "a": "line\nbreak",
    "b": "tab\there",
    "c": 'quote"end',
    "d": "back\\slash",
    "e": "A\u00e9",
    "f": "raw\\n literal",
    "g": "",
    "h": "",
}


def scenario_value_strings_and_literal():
    problems = []
    got = loads(_STR_TEXT)
    if got != _STR_WANT:
        problems.append("字符串=%r(期望 %r)" % (got, _STR_WANT))
    for bad in ('s = "a\\x41"', 's = "\\u12"', 's = "\\uZZZZ"'):
        issue = _expect_error(bad)
        if issue:
            problems.append("%r:%s" % (bad, issue))
    ok = not problems
    return _verdict(ok, "转义与字面串正确、非法转义报错", "通过" if ok else ";".join(problems))


_INT_TEXT = (
    "a = 42\n"
    "b = -7\n"
    "c = +3\n"
    "d = 0\n"
    "e = 0x1F\n"
    "f = 0o17\n"
    "g = 0b1010\n"
    "h = 1_000_000\n"
    "i = 0xFF_FF\n"
)

_INT_WANT = {
    "a": 42, "b": -7, "c": 3, "d": 0,
    "e": 31, "f": 15, "g": 10, "h": 1000000, "i": 65535,
}


def scenario_value_integers_and_underscores():
    problems = []
    got = loads(_INT_TEXT)
    if got != _INT_WANT:
        problems.append("整数=%r(期望 %r)" % (got, _INT_WANT))
    for bad in ("v = 01", "v = 0x", "v = 0o8", "v = 1__0", "v = _1", "v = 1_"):
        issue = _expect_error(bad)
        if issue:
            problems.append("%r:%s" % (bad, issue))
    ok = not problems
    return _verdict(ok, "各进制整数与下划线正确、非法数字报错", "通过" if ok else ";".join(problems))


_FLOAT_TEXT = (
    "a = 3.14\n"
    "b = -2.5e3\n"
    "c = 6.022e23\n"
    "d = 5e-3\n"
    "e = 1_000.5\n"
    "f = inf\n"
    "g = -inf\n"
    "h = nan\n"
    "i = +inf\n"
)


def scenario_value_floats_inf_nan():
    problems = []
    got = loads(_FLOAT_TEXT)
    want_finite = {"a": 3.14, "b": -2500.0, "c": 6.022e23, "d": 0.005, "e": 1000.5}
    if not isinstance(got, dict):
        problems.append("结果不是 dict: %r" % (got,))
    else:
        for key, want in want_finite.items():
            if got.get(key) != want:
                problems.append("%s=%r(期望 %r)" % (key, got.get(key), want))
        for key, want in (("f", math.inf), ("i", math.inf), ("g", -math.inf)):
            val = got.get(key)
            if not (isinstance(val, float) and val == want):
                problems.append("%s=%r(期望 %r)" % (key, val, want))
        nan = got.get("h")
        if not (isinstance(nan, float) and math.isnan(nan)):
            problems.append("h=%r(期望 nan)" % (nan,))
    for bad in ("v = 1.", "v = .1", "v = 1e", "v = 1e+", "v = 1.2.3"):
        issue = _expect_error(bad)
        if issue:
            problems.append("%r:%s" % (bad, issue))
    ok = not problems
    return _verdict(ok, "浮点含 inf/nan 正确、非法浮点报错", "通过" if ok else ";".join(problems))


# --------------------------------------------------------------------------
# struct group
# --------------------------------------------------------------------------

_STRUCT_TEXT = (
    "[server]\n"
    'host = "a"\n'
    "port = 80\n"
    "\n"
    "[server.limits]\n"
    "rate = 1.5\n"
    "\n"
    "[client]\n"
    'name = "b"\n'
    'tags = ["x", "y"]\n'
    "\n"
    "[grid]\n"
    "matrix = [[1, 2], [3, 4]]\n"
    "ys = [\n"
    '  "a",\n'
    '  "b",\n'
    "]\n"
)

_STRUCT_WANT = {
    "server": {"host": "a", "port": 80, "limits": {"rate": 1.5}},
    "client": {"name": "b", "tags": ["x", "y"]},
    "grid": {"matrix": [[1, 2], [3, 4]], "ys": ["a", "b"]},
}


def scenario_struct_table_nesting():
    problems = []
    got = loads(_STRUCT_TEXT)
    if got != _STRUCT_WANT:
        problems.append("结构=%r(期望 %r)" % (got, _STRUCT_WANT))
    else:
        if list(got.keys()) != ["server", "client", "grid"]:
            problems.append("顶层顺序=%r" % (list(got.keys()),))
        if list(got["server"].keys()) != ["host", "port", "limits"]:
            problems.append("server 顺序=%r" % (list(got["server"].keys()),))
    ok = not problems
    return _verdict(ok, "嵌套表 + 数组（含跨行/尾逗号）", "通过" if ok else ";".join(problems))


_ARRAY_TABLE_TEXT = (
    "[[srv]]\n"
    'name = "a"\n'
    "port = 1\n"
    "\n"
    "[[srv]]\n"
    'name = "b"\n'
    "port = 2\n"
    "\n"
    "[other]\n"
    "enabled = true\n"
)

_ARRAY_TABLE_WANT = {
    "srv": [{"name": "a", "port": 1}, {"name": "b", "port": 2}],
    "other": {"enabled": True},
}


def scenario_struct_array_of_tables():
    problems = []
    got = loads(_ARRAY_TABLE_TEXT)
    if got != _ARRAY_TABLE_WANT:
        problems.append("结果=%r(期望 %r)" % (got, _ARRAY_TABLE_WANT))
    ok = not problems
    return _verdict(ok, "数组套表两次追加", "通过" if ok else ";".join(problems))


# --------------------------------------------------------------------------
# dup group
# --------------------------------------------------------------------------

def scenario_dup_duplicate_key():
    problems = []
    for bad in ("a = 1\na = 2\n", "[t]\nx = 1\nx = 2\n", "a = 1\nb = 2\nb = 3\n"):
        issue = _expect_error(bad)
        if issue:
            problems.append("%r:%s" % (bad, issue))
    ok = not problems
    return _verdict(ok, "同层重复键报错", "通过" if ok else ";".join(problems))


def scenario_dup_table_key_collision():
    problems = []
    for bad in ("a = 1\n[a]\nb = 2\n", "[a]\nx = 1\n[a]\ny = 2\n", "[a]\n[a.b]\nz = 1\n[a]\n"):
        issue = _expect_error(bad)
        if issue:
            problems.append("%r:%s" % (bad, issue))
    ok = not problems
    return _verdict(ok, "表与键同名报错", "通过" if ok else ";".join(problems))


# --------------------------------------------------------------------------
# errloc group
# --------------------------------------------------------------------------

def _error_pos(text):
    """返回 (line, col)，或 ("none", 描述)。"""
    try:
        loads(text)
    except TomlError as exc:
        return (exc.line, exc.col)
    except NotImplementedError:
        raise
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__)
    return ("none", "未抛")


def scenario_errloc_multiline_array():
    problems = []
    bad_token = "items = [\n    1,\n    2,\n    x,\n]\n"
    got = _error_pos(bad_token)
    if got != (4, 5):
        problems.append("坏 token→%r(期望 (4, 5))" % (got,))
    bad_date = "a = [\n  1,\n  1979-05-27,\n  3,\n]\n"
    got = _error_pos(bad_date)
    if got != (3, 3):
        problems.append("多行数组里的日期→%r(期望 (3, 3))" % (got,))
    ok = not problems
    return _verdict(ok, "定位到实际出错的行", "通过" if ok else ";".join(problems))


def scenario_errloc_escape_col():
    problems = []
    cases = (
        ('s = "a\\x41"\n', (1, 7)),
        ('t = "abc\\u12"\n', (1, 9)),
        ('u = "\\q"\n', (1, 6)),
    )
    for text, want in cases:
        got = _error_pos(text)
        if got != want:
            problems.append("%r→%r(期望 %r)" % (text, got, want))
    ok = not problems
    return _verdict(ok, "指向转义序列起点", "通过" if ok else ";".join(problems))


# --------------------------------------------------------------------------
# edge group
# --------------------------------------------------------------------------

def scenario_edge_empty_comment_datetime():
    problems = []
    for text in ("", "\n\n\t\n", "# just a comment", "  # c\n\n\t# d\n", "# no newline at eof"):
        try:
            got = loads(text)
        except Exception as exc:  # noqa: BLE001
            problems.append("%r 抛了 %s" % (text, type(exc).__name__))
            continue
        if got != {}:
            problems.append("%r→%r(期望 {})" % (text, got))
    for bad in ("d = 1979-05-27\n", "d = 07:32:00\n", "d = 1979-05-27T07:32:00Z\n"):
        issue = _expect_error(bad)
        if issue:
            problems.append("%r:%s" % (bad, issue))
    ok = not problems
    return _verdict(ok, "空/纯注释 → {}；日期时间报错", "通过" if ok else ";".join(problems))


SCENARIOS = (
    ("value", "strings-and-literal", scenario_value_strings_and_literal),
    ("value", "integers-and-underscores", scenario_value_integers_and_underscores),
    ("value", "floats-inf-nan", scenario_value_floats_inf_nan),
    ("struct", "table-nesting", scenario_struct_table_nesting),
    ("struct", "array-of-tables", scenario_struct_array_of_tables),
    ("dup", "duplicate-key", scenario_dup_duplicate_key),
    ("dup", "table-key-collision", scenario_dup_table_key_collision),
    ("errloc", "multiline-array", scenario_errloc_multiline_array),
    ("errloc", "escape-col", scenario_errloc_escape_col),
    ("edge", "empty-comment-datetime", scenario_edge_empty_comment_datetime),
)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="check.py")
    parser.add_argument("-list", dest="list_scenarios", action="store_true",
                        help="列出全部场景后退出")
    parser.add_argument("--only", dest="only", default=None,
                        help="只运行指定组")
    args = parser.parse_args(argv)

    if args.list_scenarios:
        for group, name, _func in SCENARIOS:
            print("%s/%s" % (group, name))
        return 0

    selected = [s for s in SCENARIOS if args.only is None or s[0] == args.only]
    passed = 0
    for group, name, func in selected:
        try:
            ok, expected, actual = func()
        except NotImplementedError:
            ok, expected, actual = False, "已实现", "NotImplementedError"
        except Exception as exc:  # noqa: BLE001
            ok, expected, actual = False, "无异常", "%s: %s" % (type(exc).__name__, exc)
        if ok:
            passed += 1
            print("PASS %s/%s" % (group, name))
        else:
            print("FAIL %s/%s  期望=%s 实际=%s" % (group, name, expected, actual))

    print("结果：通过 %d/%d" % (passed, len(selected)))
    return 0 if selected and passed == len(selected) else 1


if __name__ == "__main__":
    sys.exit(main())
