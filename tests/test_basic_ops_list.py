# -*- coding: utf-8 -*-
import re
from typing import Any, List, Optional

import pytest

from omegaconf import AnyNode, ListConfig, OmegaConf
from omegaconf.errors import UnsupportedKeyType, UnsupportedValueType
from omegaconf.nodes import IntegerNode, StringNode

from . import IllegalType, does_not_raise


def test_list_value() -> None:
    c = OmegaConf.create("a: [1,2]")
    assert {"a": [1, 2]} == c


def test_list_of_dicts() -> None:
    v = [dict(key1="value1"), dict(key2="value2")]
    c = OmegaConf.create(v)
    assert c[0].key1 == "value1"
    assert c[1].key2 == "value2"


def test_pretty_list() -> None:
    c = OmegaConf.create(["item1", "item2", dict(key3="value3")])
    expected = """- item1
- item2
- key3: value3
"""
    assert expected == c.pretty()
    assert OmegaConf.create(c.pretty()) == c


def test_pretty_list_unicode() -> None:
    c = OmegaConf.create(["item一", "item二", dict(key三="value三")])
    expected = """- item一
- item二
- key三: value三
"""
    assert expected == c.pretty()
    assert OmegaConf.create(c.pretty()) == c


def test_list_get_with_default() -> None:
    c = OmegaConf.create([None, "???", "found"])
    assert c.get(0, "default_value") == "default_value"
    assert c.get(1, "default_value") == "default_value"
    assert c.get(2, "default_value") == "found"


def test_iterate_list() -> None:
    c = OmegaConf.create([1, 2])
    items = [x for x in c]
    assert items[0] == 1
    assert items[1] == 2


def test_items_with_interpolation() -> None:
    c = OmegaConf.create(["foo", "${0}"])
    assert c == ["foo", "foo"]


def test_list_pop() -> None:
    c = OmegaConf.create([1, 2, 3, 4])
    assert c.pop(0) == 1
    assert c.pop() == 4
    assert c == [2, 3]
    with pytest.raises(IndexError):
        c.pop(100)


def test_in_list() -> None:
    c = OmegaConf.create([10, 11, dict(a=12)])
    assert 10 in c
    assert 11 in c
    assert dict(a=12) in c
    assert "blah" not in c


def test_list_config_with_list() -> None:
    c = OmegaConf.create([])
    assert isinstance(c, ListConfig)


def test_list_config_with_tuple() -> None:
    c = OmegaConf.create(())
    assert isinstance(c, ListConfig)


def test_items_on_list() -> None:
    c = OmegaConf.create([1, 2])
    with pytest.raises(AttributeError):
        c.items()


def test_list_enumerate() -> None:
    src: List[Optional[str]] = ["a", "b", "c", "d"]
    c = OmegaConf.create(src)
    for i, v in enumerate(c):
        assert src[i] == v
        assert v is not None
        src[i] = None

    for v in src:
        assert v is None


def test_list_delitem() -> None:
    c = OmegaConf.create([1, 2, 3])
    assert c == [1, 2, 3]
    del c[0]
    assert c == [2, 3]
    with pytest.raises(IndexError):
        del c[100]


def test_list_len() -> None:
    c = OmegaConf.create([1, 2])
    assert len(c) == 2


def test_nested_list_assign_illegal_value() -> None:
    c = OmegaConf.create(dict(a=[None]))
    with pytest.raises(UnsupportedValueType, match=re.escape("key a[0]")):
        c.a[0] = IllegalType()


def test_list_append() -> None:
    c = OmegaConf.create([])
    c.append(1)
    c.append(2)
    c.append({})
    c.append([])
    assert c == [1, 2, {}, []]


def test_pretty_without_resolve() -> None:
    c = OmegaConf.create([100, "${0}"])
    # without resolve, references are preserved
    c2 = OmegaConf.create(c.pretty(resolve=False))
    assert isinstance(c2, ListConfig)
    c2[0] = 1000
    assert c2[1] == 1000


def test_pretty_with_resolve() -> None:
    c = OmegaConf.create([100, "${0}"])
    # with resolve, references are not preserved.
    c2 = OmegaConf.create(c.pretty(resolve=True))
    assert isinstance(c2, ListConfig)
    c2[0] = 1000
    assert c[1] == 100


@pytest.mark.parametrize(  # type: ignore
    "index, expected", [(slice(1, 3), [11, 12]), (slice(0, 3, 2), [10, 12]), (-1, 13)]
)
def test_list_index(index: Any, expected: Any) -> None:
    c = OmegaConf.create([10, 11, 12, 13])
    assert c[index] == expected


def test_list_dir() -> None:
    c = OmegaConf.create([1, 2, 3])
    assert ["0", "1", "2"] == dir(c)


def test_getattr() -> None:
    c = OmegaConf.create(["a", "b", "c"])
    assert getattr(c, "0") == "a"
    assert getattr(c, "1") == "b"
    assert getattr(c, "2") == "c"
    with pytest.raises(AttributeError):
        getattr(c, "anything")


@pytest.mark.parametrize(  # type: ignore
    "input_, index, value, expected, expected_node_type",
    [
        (["a", "b", "c"], 1, 100, ["a", 100, "b", "c"], AnyNode),
        (["a", "b", "c"], 1, IntegerNode(100), ["a", 100, "b", "c"], IntegerNode),
        (["a", "b", "c"], 1, "foo", ["a", "foo", "b", "c"], AnyNode),
        (["a", "b", "c"], 1, StringNode("foo"), ["a", "foo", "b", "c"], StringNode),
    ],
)
def test_insert(
    input_: List[str], index: int, value: Any, expected: Any, expected_node_type: type
) -> None:
    c = OmegaConf.create(input_)
    c.insert(index, value)
    assert c == expected
    assert type(c.get_node(index)) == expected_node_type


@pytest.mark.parametrize(  # type: ignore
    "src, append, result",
    [
        ([], [], []),
        ([1, 2], [3], [1, 2, 3]),
        ([1, 2], ("a", "b", "c"), [1, 2, "a", "b", "c"]),
    ],
)
def test_extend(src: List[Any], append: List[Any], result: List[Any]) -> None:
    lst = OmegaConf.create(src)
    lst.extend(append)
    assert lst == result


@pytest.mark.parametrize(  # type: ignore
    "src, remove, result, expectation",
    [
        ([10], 10, [], does_not_raise()),
        ([], "oops", None, pytest.raises(ValueError)),
        ([0, dict(a="blah"), 10], dict(a="blah"), [0, 10], does_not_raise()),
        ([1, 2, 1, 2], 2, [1, 1, 2], does_not_raise()),
    ],
)
def test_remove(src: List[Any], remove: Any, result: Any, expectation: Any) -> None:
    with expectation:
        lst = OmegaConf.create(src)
        assert isinstance(lst, ListConfig)
        lst.remove(remove)
        assert lst == result


@pytest.mark.parametrize("src", [[], [1, 2, 3], [None, dict(foo="bar")]])  # type: ignore
@pytest.mark.parametrize("num_clears", [1, 2])  # type: ignore
def test_clear(src: List[Any], num_clears: int) -> None:
    lst = OmegaConf.create(src)
    for i in range(num_clears):
        lst.clear()
    assert lst == []


@pytest.mark.parametrize(  # type: ignore
    "src, item, expected_index, expectation",
    [
        ([], 20, -1, pytest.raises(ValueError)),
        ([10, 20], 10, 0, does_not_raise()),
        ([10, 20], 20, 1, does_not_raise()),
    ],
)
def test_index(
    src: List[Any], item: Any, expected_index: int, expectation: Any
) -> None:
    with expectation:
        lst = OmegaConf.create(src)
        assert lst.index(item) == expected_index


def test_index_with_range() -> None:
    lst = OmegaConf.create([10, 20, 30, 40, 50])
    assert lst.index(x=30) == 2
    assert lst.index(x=30, start=1) == 2
    assert lst.index(x=30, start=1, end=3) == 2
    with pytest.raises(ValueError):
        lst.index(x=30, start=3)

    with pytest.raises(ValueError):
        lst.index(x=30, end=2)


@pytest.mark.parametrize(  # type: ignore
    "src, item, count",
    [([], 10, 0), ([10], 10, 1), ([10, 2, 10], 10, 2), ([10, 2, 10], None, 0)],
)
def test_count(src: List[Any], item: Any, count: int) -> None:
    lst = OmegaConf.create(src)
    assert lst.count(item) == count


def test_sort() -> None:
    c = OmegaConf.create(["bbb", "aa", "c"])
    c.sort()
    assert ["aa", "bbb", "c"] == c
    c.sort(reverse=True)
    assert ["c", "bbb", "aa"] == c
    c.sort(key=len)
    assert ["c", "aa", "bbb"] == c
    c.sort(key=len, reverse=True)
    assert ["bbb", "aa", "c"] == c


def test_insert_throws_not_changing_list() -> None:
    c = OmegaConf.create([])
    with pytest.raises(ValueError):
        c.insert(0, IllegalType())
    assert len(c) == 0
    assert c == []


def test_append_throws_not_changing_list() -> None:
    c = OmegaConf.create([])
    with pytest.raises(ValueError):
        c.append(IllegalType())
    assert len(c) == 0
    assert c == []


def test_hash() -> None:
    c1 = OmegaConf.create([10])
    c2 = OmegaConf.create([10])
    assert hash(c1) == hash(c2)
    c2[0] = 20
    assert hash(c1) != hash(c2)


@pytest.mark.parametrize(
    "in_list1, in_list2,in_expected",
    [
        ([], [], []),
        ([1, 2], [3, 4], [1, 2, 3, 4]),
        (["x", 2, "${0}"], [5, 6, 7], ["x", 2, "x", 5, 6, 7]),
    ],
)
class TestListAdd:
    def test_list_plus(
        self, in_list1: List[Any], in_list2: List[Any], in_expected: List[Any]
    ) -> None:
        list1 = OmegaConf.create(in_list1)
        list2 = OmegaConf.create(in_list2)
        expected = OmegaConf.create(in_expected)
        ret = list1 + list2
        assert ret == expected

    def test_list_plus_eq(
        self, in_list1: List[Any], in_list2: List[Any], in_expected: List[Any]
    ) -> None:
        list1 = OmegaConf.create(in_list1)
        list2 = OmegaConf.create(in_list2)
        expected = OmegaConf.create(in_expected)
        list1 += list2
        assert list1 == expected


def test_deep_add() -> None:
    cfg = OmegaConf.create({"foo": [1, 2, "${bar}"], "bar": "xx"})
    lst = cfg.foo + [10, 20]
    assert lst == [1, 2, "xx", 10, 20]


def test_set_with_invalid_key() -> None:
    cfg = OmegaConf.create([1, 2, 3])
    with pytest.raises(UnsupportedKeyType):
        cfg["foo"] = 4  # type: ignore
