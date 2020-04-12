import unittest


class TestExample(unittest.TestCase):
    def test_basic_example(self):
        from equator import equals

        item1 = [
            {
                1: [
                    {1: [1, 2]},
                    [1, 2.0001],
                ],
            },
            [3, [4, [5]]],
        ]

        item2 = [
            {
                1: [
                    {1.0001: [1, 2.0001]},
                    [1.0001, 1.9999],
                ],
            },
            [2.9999, [4, [5.002]]],
        ]

        result = equals.approx(item1, item2, rel_tol=1e-2)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
