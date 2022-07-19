from itertools import zip_longest


def assert_deep_equals(a, b):
    assert type(a) is type(b)

    if isinstance(a, dict):
        ks = set(a.keys()).union(set(b.keys()))

        for k in ks:
            try:
                a_new = a[k]
                b_new = b[k]
                assert_deep_equals(a_new, b_new)
            except KeyError:
                raise AssertionError

        return

    if isinstance(a, list):
        for a_new, b_new in zip_longest(a, b):
            assert_deep_equals(a_new, b_new)

        return

    assert a == b
