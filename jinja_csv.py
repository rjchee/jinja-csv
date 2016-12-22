import csv
import os
import sys

import jinja2


class CSVModel:
    def __init__(self, filename, named_columns=True):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile) if named_columns else csv.reader(csvfile)
            self.rows = list(row for row in reader)
            if named_columns:
                self.fieldnames = reader.fieldnames
                idx_map = {field : idx for idx, field in enumerate(self.fieldnames)}
                for i in range(len(self.rows)):
                    row = {}
                    for field, value in self.rows[i].items():
                        row[field] = value
                        row[idx_map[field]] = value
                    self.rows[i] = row


    def __iter__(self):
        return iter(self.rows)


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


    def render_jinja_template(self, template_name, model, base_template='all_rows.template', **kwargs):
        return self.env.get_template(base_template).render(
                rows=model,
                row_template=template_name,
                **kwargs)


    def render_template_for_rows(self, template_name, model, rowkey=0, **kwargs):
        template = self.env.get_template(template_name)
        return list((row[rowkey], template.render(row=row, fieldnames=model.fieldnames, **kwargs)) for row in model)


def render_template_from_csv(csvfile, templatefile, template_path=None, options=None):
    model = CSVModel(csvfile)
    view = CSVJinjaView(template_path=template_path, options=options)
    return view.render_jinja_template(templatefile, model)


def render_template_per_row(csvfile, templatefile, filemapper, template_path=None, options=None):
    model = CSVModel(csvfile)
    view = CSVJinjaView(template_path=template_path, options=options)
    for output in view.render_template_for_rows(templatefile, model):
        with open(filemapper(output[0]), 'w') as fp:
            fp.write(output[1])


def main():
    csvfile = sys.argv[1]
    templatefile = sys.argv[2]
    output_path = sys.argv[3]
    output = render_template_from_csv(csvfile, templatefile)
    print(output, end='')
    render_template_per_row(csvfile, templatefile, lambda name:os.path.join(output_path, '_'.join(name.lower().split()) + '.out'))


if __name__ == '__main__':
    main()
