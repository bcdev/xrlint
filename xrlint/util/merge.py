from typing import Any, Callable


def merge_values(
    value1: Any,
    value2: Any,
    merge_items: Callable[[Any, Any], Any] | None = None,
) -> Any:
    if isinstance(value1, (list, tuple)) and isinstance(value2, (list, tuple)):
        return merge_arrays(value1, value2, merge_items=merge_items)
    if isinstance(value1, dict) and isinstance(value2, dict):
        return merge_dicts(value1, value2, merge_items=merge_items)
    return value2 if value2 is not None else value1


def merge_dicts(
    dct1: dict[str, Any] | None,
    dct2: dict[str, Any] | None,
    merge_items: Callable[[Any, Any], Any] | None = None,
) -> dict[str, Any] | None:
    if dct1 is None:
        return dct2
    if dct2 is None:
        return dct1
    result = {}
    for k1, v1 in dct1.items():
        if k1 in dct2:
            v2 = dct2[k1]
            result[k1] = merge_items(v1, v2) if merge_items is not None else v2
        else:
            result[k1] = v1
    for k2, v2 in dct2.items():
        if k2 not in dct1:
            result[k2] = v2
    return result


def merge_arrays(
    arr1: list | tuple | None,
    arr2: list | tuple | None,
    merge_items: Callable[[Any, Any], Any] | None = None,
) -> list | tuple | None:
    if arr1 is None:
        return arr2
    if arr2 is None:
        return arr1
    n1 = len(arr1)
    n2 = len(arr2)
    result = list(arr1)
    for i, v1 in enumerate(arr1):
        if i < n2:
            v2 = arr2[i]
            result[i] = merge_items(v1, v2) if merge_items is not None else v2
    if n1 < n2:
        result.extend(arr2[n1:])
    return result


def merge_set_lists(set1: list | None, set2: list | None) -> list | None:
    if set1 is None:
        return set2
    if set2 is None:
        return set1
    result = []
    for v in set1 + set2:
        if v not in result:
            result.append(v)
    return result
