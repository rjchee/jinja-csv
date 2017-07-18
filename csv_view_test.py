from datetime import datetime
import unittest

from dateutil import parser
from jinja2 import FunctionLoader

from csv_view import *

class TestViewFilters(unittest.TestCase):

    def setUp(self):
        self.view = CSVJinjaView(env_options={'loader': FunctionLoader(lambda x:x)})

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

    def test_date_from_timestamp(self):
        data = ['1000', '0', '1', '1931516412']
        for test_data in data:
            template = '{{ ' + str(test_data) + ' | int | date }}'
            expected = str(datetime.fromtimestamp(int(test_data)))
            self.assertEqual(expected, self.view.render_jinja_template(template, None))

    def test_dateformat(self):
        date = '2017-07-18'
        formats = ['%d/%m/%y', '%Y-%d-%m', '%y']
        expected = ['18/07/17', '2017-18-07', '17']
        self.assertEqual(len(formats), len(expected),
                         msg='# of test cases should match # of expected outcomes')
        for fmt, val in zip(formats, expected):
            template = '{{ ' + repr(date) + ' | date | dateformat(' + repr(fmt) + ') }}'
            self.assertEqual(val, self.view.render_jinja_template(template, None))


if __name__ == '__main__':
    unittest.main()
