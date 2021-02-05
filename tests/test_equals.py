
import math
import unittest
from collections import (
    UserString,
    OrderedDict,
)
from decimal import Decimal

from hypothesis import (
    given,
    settings,
    strategies as st,
)
from parameterized import parameterized, param

from approx import equals


class TestStringHandler(unittest.TestCase):
    @parameterized.expand([
        ('', '', True),
        (' ', ' ', True),
        ('string', 'string', True),
        ('string', 'other_string', False),
        ('string', UserString('string'), True),
        (UserString('string'), UserString('other_string'), False),
    ])
    def test_handle_strings(self, item1, item2, expected):
        result = equals.StringHandler().handle(item1, item2)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ('string', 0.123),
        ([3, 4, 5], [1, 2, 3]),
        ({3, 4, 5}, {1, 2, 3}),
        ({1: 3, 4: 5}, {1: 2, 3: 2}),
        (3.14, 'text'),
        (object(), 'text'),
        ('string', Decimal(6.28)),
        ('string', True),
        ('string', False),
        ('string', None),
    ])
    def test_cannot_handle_other_than_strings(self, item1, item2):
        result = equals.StringHandler().handle(item1, item2)
        self.assertEqual(result, None)

    def test_ignore_all_kwargs(self):
        item1 = 'string'
        item2 = 'string'
        result = equals.StringHandler().handle(item1, item2, kwarg='any_kwarg')
        self.assertTrue(result)


class TestRealNumHandler(unittest.TestCase):
    def test_equal_items(self):
        item1 = 3.14
        item2 = 3.14
        kwargs = {
            'abs_tol': 0,
            'rel_tol': 0,
        }
        result = equals.RealNumHandler().check_equal(item1, item2, **kwargs)
        self.assertTrue(result)

    @given(
        item1=st.floats(),
        item2=st.floats(),
        rel_tol=st.floats(min_value=0, max_value=1),
        abs_tol=st.floats(min_value=0, max_value=10),
    )
    @settings(max_examples=500)
    def test_almost_equal_floats(self, item1, item2, rel_tol, abs_tol):
        self.compare_numbers(item1, item2, rel_tol, abs_tol)

    @given(
        item1=st.decimals(allow_nan=False),
        item2=st.decimals(allow_nan=False),
        rel_tol=st.floats(min_value=0, max_value=1),
        abs_tol=st.floats(min_value=0, max_value=10),
    )
    @settings(max_examples=500)
    def test_almost_equal_decimals(self, item1, item2, rel_tol, abs_tol):
        self.compare_numbers(item1, item2, rel_tol, abs_tol)

    # currently cannot handle decimal nans
    @unittest.expectedFailure
    @given(
        item1=st.decimals(allow_nan=True),
        item2=st.decimals(allow_nan=True),
        rel_tol=st.floats(min_value=0, max_value=1),
        abs_tol=st.floats(min_value=0, max_value=10),
    )
    @settings(max_examples=10)
    def test_almost_equal_decimals_with_nans(
        self, item1, item2, rel_tol, abs_tol,
    ):
        self.compare_numbers(item1, item2, rel_tol, abs_tol)

    def compare_numbers(self, item1, item2, rel_tol, abs_tol):
        handler = equals.RealNumHandler()
        result = handler.handle(
            item1,
            item2,
            rel_tol=rel_tol,
            abs_tol=abs_tol,
        )
        expected = math.isclose(
            item1,
            item2,
            rel_tol=rel_tol,
            abs_tol=abs_tol,
        )
        self.assertEqual(result, expected)

    @parameterized.expand([
        ('string', 0.123),
        ([3, 4, 5], [1, 2, 3]),
        (3.14, 'text'),
        (object(), 'text'),
        ('string', Decimal(6.28)),
        ('string', True),
        ('string', False),
        ('string', None),
    ])
    def test_cannot_handle_other_than_numbers(self, item1, item2):
        handler = equals.RealNumHandler()
        result = handler.handle(item1, item2)
        self.assertEqual(result, None)


class TestMappingHandler(unittest.TestCase):
    @parameterized.expand([
        param(
            item1={1: [1, 2]},
            item2={1: [1.0001, 2]},
            rel_tol=1e-3,
            expected=True,
        ),
        param(
            item1={1: [[1], 2]},
            item2={1: [[1.0001], 2]},
            rel_tol=1e-3,
            expected=True,
        ),
        param(
            item1={1: [{1}, {2, 'str'}]},
            item2={1.0001: [{1}, {2, 'str'}]},
            rel_tol=1e-3,
            expected=True,
        ),
        param(
            item1={1: [{1: [1, 2]}, {2, 'str'}]},
            item2={1: [{1.0001: [1, 2.0001]}, {2, 'str'}]},
            rel_tol=1e-3,
            expected=True,
        ),
        param(
            item1={1: [{1: [1, 2]}, {2, 'str'}]},
            item2={1: [{1.0001: [1, 2.0001]}, {2, 'str'}]},
            rel_tol=1e-5,
            expected=False,
        ),
        param(
            item1={1.01: [{1: [1, 2]}, {2, 'str'}]},
            item2={1: [{1: [1, 2]}, {2, 'str'}]},
            rel_tol=1e-5,
            expected=False,
        ),
        param(
            item1={1.01: [{1: [1, 2]}, {2, 'str'}]},
            item2=OrderedDict({1: [{1: [1, 2]}, {2, 'str'}]}),
            rel_tol=1e-5,
            expected=False,
        ),
    ])
    def test_compare_dicts(self, item1, item2, rel_tol, expected):
        handler = equals.MappingHandler()
        result = handler.handle(
            item1,
            item2,
            rel_tol=rel_tol,
            abs_tol=0,
        )
        self.assertEqual(result, expected)

    @parameterized.expand([
        ('string', 0.123),
        ([3, 4, 5], [1, 2, 3]),
        ({3, 4, 5}, {1, 2, 3}),
        (3.14, 'text'),
        (object(), 'text'),
        ('string', Decimal(6.28)),
        ('string', True),
        ('string', False),
        ('string', None),
    ])
    def test_cannot_handle_other_than_dicts(self, item1, item2):
        handler = equals.MappingHandler()
        result = handler.handle(item1, item2)
        self.assertEqual(result, None)


class TestSequenceHandler(unittest.TestCase):
    @parameterized.expand([
        param(
            item1=[1, 2, 3],
            item2=[1.0009, 2.001, 3.001],
            rel_tol=1e-3,
            expected=True,
        ),
        param(
            item1=[1, 2, 3],
            item2=[1.0009, 2.001, 3.001],
            rel_tol=1e-5,
            expected=False,
        ),
        param(
            item1=[1, 2],
            item2=[1.0009, 2.001, 3.001],
            rel_tol=1e-3,
            expected=False,
        ),
        param(
            item1=[1, {2: 1}],
            item2=[1.0009, {2.0001: 1.0001}],
            rel_tol=1e-3,
            expected=True,
        ),
        param(
            item1=[1, [2, [3, [4, 5]]]],
            item2=[1, [2, [3, [4.002, 5.003]]]],
            rel_tol=1e-3,
            expected=True,
        ),
    ])
    def test_compare_sequences(self, item1, item2, rel_tol, expected):
        handler = equals.SequenceHandler()
        result = handler.handle(
            item1,
            item2,
            rel_tol=rel_tol,
            abs_tol=0,
        )
        self.assertEqual(result, expected)

    @parameterized.expand([
        ('string', 'another_string'),
    ])
    def test_cannot_handle_other_than_sequences(self, item1, item2):
        handler = equals.SequenceHandler()
        result = handler.handle(item1, item2)
        self.assertEqual(result, None)


class TestCompositeHandler(unittest.TestCase):
    class CompositeObject:
        def __init__(self, num, string, seq):
            self.num = num
            self.string = string
            self.seq = seq

    @parameterized.expand([
        (1e-3, True),
        (1e-5, False),
    ])
    def test_custom_objects_almost_equal(self, rel_tol, expected):
        item1 = self.CompositeObject(
            3.14159,
            'string',
            [1.0, {1: 'string'}],
        )

        item2 = self.CompositeObject(
            3.14160,
            'string',
            [1.0001, {1.0001: 'string'}],
        )

        handler = equals.CompositeHandler()
        result = handler.handle(
            item1,
            item2,
            rel_tol=rel_tol,
            abs_tol=0,
        )
        self.assertEqual(result, expected)


class TestApprox(unittest.TestCase):
    @parameterized.expand([
        ('pi', 3.1415),
        ('pi', ['p', 'i']),
        (object(), object()),
        (list(), dict()),
        (set(), dict()),
        ([1, 2], {1: '2'}),
    ])
    def test_uncomparable_objects_raises(self, item1, item2):
        with self.assertRaises(TypeError, msg='Cannot compare'):
            equals.approx(item1, item2)


if __name__ == '__main__':
    unittest.main()
