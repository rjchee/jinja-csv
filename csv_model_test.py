import unittest

from csv_model import CSVRow

class TestCSVRow(unittest.TestCase):

    def setUp(self):
        self.data = ['Hello', 'World', 1, '', '99']
        self.row = CSVRow(self.data)
    
    def test_keys(self):
        self.assertEqual(list(self.row.keys()), list(range(len(self.data))))

    def test_items(self):
        self.assertEqual(list(self.row.items()), list(enumerate(self.data)))

    def test_values(self):
        self.assertEqual(list(self.row.values()), self.data)

    def test_modify(self):
        """CSVRow should be read-only after construction

        This test checks that errors are raised upon modification to the underlying.
        """
        
        modify_funcs = [
            (lambda r: r.__delitem__(0), 'del'),
            (lambda r: r.__setitem__(0, 100), 'set'),
            (lambda r: r.clear(), 'clear'),
            (lambda r: r.pop(1), 'pop'),
            (lambda r: r.popitem(), 'popitem'),
            (lambda r: r.setdefault(100, 'test'), 'setdefault'),
            (lambda r: r.update(list((a, a) for a in range(100))), 'update')
        ]

        for f, name in modify_funcs:
            err_msg = '{} should raise a NotImplementedError'.format(name)
            with self.assertRaises(NotImplementedError, msg=err_msg):
                f(self.row)


if __name__ == '__main__':
    unittest.main()
