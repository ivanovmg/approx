
import math
import unittest

from collections import (
    OrderedDict,
    UserString,
)
from decimal import Decimal

from hypothesis import (
    given,
    settings,
    strategies as st,
)
from parameterized import param, parameterized

from approx import approx


class TestString(unittest.TestCase):
    @parameterized.expand([
        ('', '', True),
        (' ', ' ', True),
        ('string', 'string', True),
        ('string', 'other_string', False),
        ('string', UserString('string'), True),
        (UserString('string'), UserString('other_string'), False),
    ])
    def test_handle_strings(self, item1, item2, expected):
        result = approx(item1, item2)
        self.assertEqual(result, expected)


class TestRealNum(unittest.TestCase):
    def compare_numbers(self, item1, item2, rel_tol, abs_tol):
        """Helper method for comparing numbers."""
        result = approx(
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

    def test_equal_items(self):
        item1 = 3.14
        item2 = 3.14
        result = approx(item1, item2, abs_tol=0, rel_tol=0)
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

    @given(
        item1=st.decimals(allow_nan=False),
        item2=st.decimals(allow_nan=False),
        rel_tol=st.floats(min_value=0, max_value=1),
        abs_tol=st.floats(min_value=0, max_value=10),
    )
    @settings(max_examples=10)
    def test_almost_equal_decimals_no_nans(
        self, item1, item2, rel_tol, abs_tol,
    ):
        self.compare_numbers(item1, item2, rel_tol, abs_tol)

    @parameterized.expand([
        param(item1=Decimal('NaN'), item2=Decimal('NaN'), expected=False),
        param(
            item1=Decimal('Infinity'),
            item2=Decimal('Infinity'),
            expected=True,
        ),
        param(
            item1=Decimal('Infinity'),
            item2=Decimal('-Infinity'),
            expected=False,
        ),
        param(
            item1=Decimal('-Infinity'),
            item2=Decimal('+Infinity'),
            expected=False,
        ),
    ])
    def test_almost_decimals_nans(self, item1, item2, expected):
        result = approx(item1, item2)
        self.assertEqual(result, expected)

    # currently cannot handle signalling NaNs
    @parameterized.expand([
        param(item1=Decimal('sNaN'), item2=Decimal('sNaN')),
        param(item1=Decimal('sNaN'), item2=Decimal('NaN')),
    ])
    @unittest.expectedFailure
    def test_decimals_signalling_nans(self, item1, item2):
        result = approx(item1, item2)
        expected = False
        self.assertEqual(result, expected)


class TestMapping(unittest.TestCase):
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
        result = approx(
            item1,
            item2,
            rel_tol=rel_tol,
            abs_tol=0,
        )
        self.assertEqual(result, expected)


class TestSequence(unittest.TestCase):
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
        result = approx(
            item1,
            item2,
            rel_tol=rel_tol,
            abs_tol=0,
        )
        self.assertEqual(result, expected)


class TestComposite(unittest.TestCase):
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

        result = approx(
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
        (3.14, 'text'),
        (object(), 'text'),
        ('string', Decimal(6.28)),
        ('string', True),
        ('string', False),
        ('string', None),
    ])
    def test_uncomparable_objects_raises(self, item1, item2):
        with self.assertRaises(TypeError, msg='Cannot compare'):
            approx(item1, item2)


if __name__ == '__main__':
    unittest.main()
