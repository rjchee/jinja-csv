from datetime import datetime
import unittest

from dateutil import parser
from jinja2 import FunctionLoader

from csv_view import *

class TestViewFilters(unittest.TestCase):

    def setUp(self):
        self.view = CSVJinjaView(options={'loader': FunctionLoader(lambda x:x)})

    def test_bool(self):
        data = ['yes', 'no', 'True', 'y', 'false', 'N', 'TrUE']
        expected = ['True', 'False', 'True', 'True', 'False', 'False', 'True']
        self.assertEqual(len(data), len(expected),
                         msg='# of test cases should match # of expected outcomes')
        for test_data, val in zip(data, expected):
            template = '{{ ' + repr(test_data) + ' | bool }}'
            self.assertEqual(val, self.view.render_jinja_template(template, None))

    def test_date(self):
        today = datetime.now()
        data = ['2017-07-02', '02/29/2008', '10:15:45.31 AM', '05/11/96']
        expected = [datetime(2017, 7, 2), datetime(2008, 2, 29),
                    datetime(today.year, today.month, today.day, 10, 15, 45, 310000),
                    datetime(1996, 5, 11)]
        self.assertEqual(len(data), len(expected),
                         msg='# of test cases should match # of expected outcomes')
        for test_data, val in zip(data, expected):
            template = '{{ ' + repr(test_data) + ' | date }}'
            self.assertEqual(str(val), self.view.render_jinja_template(template, None))


if __name__ == '__main__':
    unittest.main()
