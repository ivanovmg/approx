
import equator
import unittest


class BasicTestCase(unittest.TestCase):
    """ Basic test cases """

    def test_basic(self):
        """ check True is True """
        self.assertTrue(True)

    def test_version(self):
        """ check equator exposes a version attribute """
        self.assertTrue(hasattr(equator, "__version__"))
        self.assertIsInstance(equator.__version__, str)


if __name__ == "__main__":
    unittest.main()
