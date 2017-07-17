import unittest

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

if __name__ == '__main__':
    unittest.main()
