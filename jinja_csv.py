import os
import sys

from csv_model import CSVDictModel


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
