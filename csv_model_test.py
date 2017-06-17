import unittest

from csv_model import CSVRow
from csv_model import CSVDictRow
from csv_model import CSVModel

class TestCSVRow(unittest.TestCase):

    def setUp(self):
        self.data = ['Hello', 3.5, 1, '', '99']
        self.row = CSVRow(self.data)
    
    def test_iter(self):
        self.assertEqual(list(self.row), self.data)

    def test_contains(self):
        for val in self.data:
            self.assertIn(val, self.row)

    def test_len(self):
        self.assertEqual(len(self.row), len(self.data))

    def test_get(self):
        for i, val in enumerate(self.data):
            self.assertEqual(self.row[i], val)

    def test_get_slice(self):
        self.assertEqual(self.row[:3], ['Hello', 3.5, 1])
        self.assertEqual(self.row[3:], ['', '99'])
        self.assertEqual(self.row[1:3], [3.5, 1])
        self.assertEqual(self.row[::2], ['Hello', 1, '99'])
        self.assertEqual(self.row[1:5:2], [3.5, ''])

    def test_eq(self):
        self.assertEqual(self.row, self.data)

    def test_cast(self):
        self.assertEqual(self.row.cast([set, str, str, bool, int]),
                                       [set(['H', 'e', 'l', 'o']), '3.5', '1', False, 99])
        self.assertEqual(self.row.cast([bool]*len(self.data)), list(map(bool, self.data)))


class TestCSVDictRow(TestCSVRow):

    def setUp(self):
        self.data = ['Hello', 3.5, 1, '', '99']
        self.fields = ['Text', 'Score', 'Count', 'Comments', 'Rank']
        self.row = CSVDictRow(self.fields, self.data)

    def test_get(self):
        super().test_get()
        for field, val in zip(self.fields, self.data):
            self.assertEqual(self.row[field], val)

    def test_get_slice(self):
        super().test_get_slice()
        self.assertEqual(self.row[slice('Comments')], ['Hello', 3.5, 1])
        self.assertEqual(self.row[slice('Comments', None)], ['', '99'])
        self.assertEqual(self.row[slice('Score', 'Comments')], [3.5, 1])
        self.assertEqual(self.row[slice('Text', 'Count')], ['Hello', 3.5])
        self.assertEqual(self.row[slice('Score', 5, 2)], [3.5, ''])


class TestCSVModel(unittest.TestCase):

    def setUp(self):
        self.data = [
            ['Hello', '3.5', '1', '', '99', 'True'],
            ['Bye', '9', '0', 'eh', '9.5', 'false'],
            ['s', '3.14', '55', 's', 'false', 'yes'],
            ['eee', '4', '88', 'f', 'yes', 'NO']
        ]

    def test_autocast(self):
        expected_results = [
            ['Hello', 3.5, 1, '', '99', True],
            ['Bye', 9.0, 0, 'eh', '9.5', False],
            ['s', 3.14, 55, 's', 'false', True],
            ['eee', 4.0, 88, 'f', 'yes', False]
        ]
        model = CSVModel(self.data)
        for expected_row, row in zip(expected_results, model):
            for expected_item, item in zip(expected_row, row):
                self.assertEqual(expected_item, item)
                self.assertEqual(type(expected_item), type(item))

if __name__ == '__main__':
    unittest.main()
