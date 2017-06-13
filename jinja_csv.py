import os
import sys

import jinja2

from csv_model import CSVDictModel


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
            'sumrowrange': sumrowrange,
            'sumcolumns': sumcolumns,
            'sortedby': sortedby,
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


def sumrowrange(row, start=None, end=None, accumulator=0):
    return sum(row.iterator_at(start, end), accumulator)


def sumcolumns(rows, columns, accumulator=0):
    return sum((row[column] for column in columns for row in rows), accumulator)


def sortedby(rows, sortkeys):
    def keyfunc(row):
        if isinstance(sortkeys, int) or isinstance(sortkeys, str):
            return row[sortkeys]
        return tuple(row[key] for key in sortkeys)
    return sorted(rows, key=keyfunc)


def render_template_from_csv(csvfile, templatefile, template_path=None, options=None, **kwargs):
    model = CSVDictModel.from_file(csvfile)
    view = CSVJinjaView(template_path=template_path, options=options)
    return view.render_jinja_template(templatefile, model, **kwargs)


def render_template_per_row(csvfile, templatefile, filemapper, template_path=None, options=None, rowkey=0, **kwargs):
    model = CSVDictModel.from_file(csvfile)
    view = CSVJinjaView(template_path=template_path, options=options)
    for output in view.render_template_for_rows(templatefile, model, rowkey, **kwargs):
        with open(filemapper(output[0]), 'w') as fp:
            fp.write(output[1])


def main():
    csvfile = sys.argv[1]
    templatefile = sys.argv[2]
    #output_path = sys.argv[3]
    output = render_template_from_csv(csvfile, templatefile)
    print(output, end='')
    #render_template_per_row(csvfile, templatefile, lambda name:os.path.join(output_path, '_'.join(name.lower().split()) + '.out'))


if __name__ == '__main__':
    main()
