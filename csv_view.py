import jinja2

from csv_model import cast_to_bool
from csv_model import cast_to_date


class CSVJinjaView:
    def __init__(self, env=None, template_path=None, options=None):
        if env is None:
            if options is None:
                options = {}
            if 'trim_blocks' not in options:
                options['trim_blocks'] = True
            if 'lstrip_blocks' not in options:
                options['lstrip_blocks'] = True
            if 'loader' not in options:
                options['loader'] = jinja2.FileSystemLoader([os.getcwd() if template_path is None else template_path, os.path.realpath(__file__)])
            env = jinja2.Environment(**options)
        self.env = env
        self._register_filters()

    def _register_filters(self):
        filters = {
            'cast': self.cast,
            'castrange': self.cast_range,
            'rowrange': row_range,
            'columnrange': column_range,
            # 'getcolumns': columns, TODO: add API for this method
            'sortedby': sortedby,
            'bool': cast_to_bool,
            'date': cast_to_date,
        }
        self.env.filters.update(filters)

    def render_jinja_template(self, template_name, model, **kwargs):
        return self.env.get_template(template_name).render(
                    rows=model, **kwargs)

    def render_template_for_rows(self, template_name, model, rowkey, **kwargs):
        template = self.env.get_template(template_name)
        return list((row[rowkey], template.render(row=row, fieldnames=model.fieldnames, **kwargs)) for row in model)

    def cast(self, rows, filters):
        return rows.cast(list(self.env.filters[f] for f in filters))

    def cast_range(self, rows, filters, start=None, end=None):
        return rows.cast_range(list(self.env.filters[f] for f in filters), start, end)


def row_range(rows, start=None, end=None):
    return rows.row_slice(start, end)

def column_range(rows, start=None, end=None):
    return rows.col_slice(start, end)

def columns(rows, column_list=None):
    if column_list is None:
        return rows.cols()
    return # TODO: complete

def sortedby(rows, sortkeys):
    def keyfunc(row):
        if isinstance(sortkeys, int) or isinstance(sortkeys, str):
            return row[sortkeys]
        return tuple(row[key] for key in sortkeys)
    return sorted(rows, key=keyfunc)
