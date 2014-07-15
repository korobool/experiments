import restproxy
import unittest

class TestRESTProxy(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_equal(self):
        self.assertEqual(1,1)

    def test_except(self):
        with self.assertRaises(ValueError):
            pass

if __name__ == '__main__':
    unittest.main()

