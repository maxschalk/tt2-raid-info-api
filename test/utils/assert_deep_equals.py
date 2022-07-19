from itertools import zip_longest


def assert_deep_equals(first, second):
    assert type(first) is type(second)

    if isinstance(first, dict):
        keys = set(first.keys()).union(set(second.keys()))

        for k in keys:
            try:
                a_new = first[k]
                b_new = second[k]
                assert_deep_equals(a_new, b_new)
            except KeyError as exc:
                raise AssertionError from exc

        return

    if isinstance(first, list):
        for a_new, b_new in zip_longest(first, second):
            assert_deep_equals(a_new, b_new)

        return

    assert first == second
