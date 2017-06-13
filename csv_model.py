import csv

class CSVRow(dict):
    def __init__(self, row):
        super().__init__(enumerate(row))

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def setdefault(self, key, value):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def pop(self, k, d=None):
        raise NotImplementedError()

    def popitem(self):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def update(self, arg, **kwargs):
        raise NotImplementedError()

    def iterator_at(self, start, end=None):
        if start is None:
            start = 0
        if end is None:
            end = len(self)
        return iter(self[idx] for idx in range(start, end))

    def __iter__(self):
        return self.iterator_at(0)

    def keys(self):
        return list(range(len(self)))

    def items(self):
        return list((key, self[key]) for key in self.keys())

    def values(self):
        return list(iter(self))

    def cast(self, filters):
        if not filters:
            return self
        return CSVRow(self.cast_row(filters))

    def cast_row(self, filters):
        if not filters:
            return self.values()
        new_row = []
        if callable(filters[0]):
            if len(filters) != len(self):
                raise ValueError('number of filters does not match number of CSV columns; {} != {}'.format(len(filters), len(self)))
            for v, f in zip(self.values(), filters):
                new_row.append(f(v))
            return new_row
        else:
            filters = dict(filters)
        for k, v in self.items():
            new_row.append(filters[k](v) if k in filters else v)
        return new_row


class CSVDictRow(CSVRow):
    def __init__(self, fieldnames, row):
        if len(fieldnames) != len(row):
            raise ValueError("number of fields should match number of columns")
        self._count = len(fieldnames)
        self._idx_map = {}
        for idx, field in enumerate(fieldnames):
            self._idx_map[field] = idx
            super(CSVRow, self).__setitem__(field, row[field])
            super(CSVRow, self).__setitem__(idx, row[field])
        self.fieldnames = fieldnames

    def __len__(self):
        return self._count

    def iterator_at(self, start, end=None):
        if start is None:
            start = 0
        elif isinstance(start, str):
            start = self._idx_map[start]
        if end is None:
            end = len(self)
        elif isinstance(end, str):
            end = self._idx_map[end]
        return iter(self[field] for field in self.fieldnames[start:end])

    def keys(self):
        return list(self.fieldnames)

    def cast(self, filters):
        if not filters:
            return self
        return CSVDictRow(self.fieldnames, {field: val for field, val in zip(self.fieldnames, self.cast_row(filters))})


def cast_to_bool(s):
    if isinstance(s, str):
        if s.lower() in ['true', 'yes']:
            return True
        elif s.lower() in ['false', 'no']:
            return False
    else:
        return bool(s)
    raise ValueError()


def cast_order():
    return [(int, 0), (float, 0.0), (cast_to_bool, False)]

class CSVModel:
    def __init__(self, rows, types=None):
        max_len = max(map(len, rows))
        if types is None:
            casts = cast_order()
            types = [(str, '')]*max_len
            for i in range(max_len):
                # try to find the most specific cast
                for cast, zero in casts:
                    try:
                        list(map(cast, (row[i] for row in rows if i < len(row))))
                    except ValueError:
                        continue
                    types[i] = (cast, zero)
                    break
        self.rows = []
        for row in rows:
            new_row = []
            for i, type_data in enumerate(types):
                cast, zero = type_data
                new_row.append(cast(row[i]) if i < len(row) else zero)
            self.rows.append(CSVRow(new_row))
        self.num_cols = max_len
        self.num_rows = len(rows)
        self.types = types

    def cast(self, filters):
        new_rows = []
        for row in self.rows:
            new_rows.append(row.cast(filters))
        return self(new_rows, types=[(f, '') for f in filters])


    def cast_range(self, filters, start, end):
        if not self.rows:
            return
        filterlen = len(filters)
        rangelen = len(list(self.rows[0].iterator_at(start, end)))+1
        if rangelen != filterlen:
            raise ValueError('Number of filters ({}) should match number of columns ({})!'.format(filterlen, rangelen))
        new_rows = []
        s_i = len(list(self.rows[0].iterator_at(0, start)))
        new_filters = list(t[0] for t in self.types[:s_i])
        new_filters.extend(filters)
        new_filters.extend(t[0] for t in self.types[s_i+rangelen:])
        return self.cast(new_filters)

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __reversed__(self):
        return reversed(self.rows)

    @classmethod
    def from_file(cls, filename):
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            return cls(list(reader))


class CSVDictModel(CSVModel):
    def __init__(self, fieldnames, rows, types=None):
        if types is None:
            casts = cast_order()
            types = [(str, '')]*len(fieldnames)
            for i, field in enumerate(fieldnames):
                # try to find the most specific cast
                for cast, zero in casts:
                    try:
                        list(map(cast, (row.get(field, zero) for row in rows)))
                    except ValueError:
                        continue
                    types[i] = (cast, zero)
                    break
        self.rows = []
        for row in rows:
            new_row = {}
            for field, type_data in zip(fieldnames, types):
                cast, zero = type_data
                new_row[field] = cast(row.get(field, zero))
            self.rows.append(CSVDictRow(fieldnames, new_row))
        self.fieldnames = fieldnames
        self.num_cols = len(fieldnames)
        self.num_rows = len(rows)
        self.types = types

    def cast(self, filters):
        new_rows = []
        for row in self.rows:
            new_rows.append(row.cast(filters))
        return self.__init__(self.fieldnames, new_rows, types=list((f, '') for f in filters))

    @classmethod
    def from_file(cls, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            return cls(reader.fieldnames, list(reader))



