import csv

class CSVRow(object):
    def __init__(self, row):
        self.data = list(row)

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, val):
        return val in self.data

    def __eq__(self, other):
        return hasattr(other, '__iter__') and self.data == list(other)

    def __len__(self):
        return len(self.data)

    def _getindex(self, i):
        return len(self) if i is None else i

    def __getitem__(self, idx):
        if isinstance(idx, (int, slice)):
            try:
                return self.data[idx]
            except IndexError as e:
                raise IndexError('CSVRow index out of range')
        raise TypeError('CSVRow can only be indexed with integers or slices, not {}'.format(type(idx).__name__))

    def cast(self, filters):
        if not filters:
            return self
        return CSVRow(self._cast_row(filters))

    def _cast_row(self, filters):
        if len(filters) != len(self):
            raise ValueError('number of filters does not match number of CSV columns; {} != {}'.format(len(filters), len(self)))
        return [f(v) for f, v in zip(filters, self)]


class CSVDictRow(CSVRow):
    def __init__(self, fieldnames, row):
        if len(fieldnames) != len(row):
            raise ValueError("number of fields should match number of columns")
        super().__init__(row)
        self._idx_map = {}
        for idx, field in enumerate(fieldnames):
            self._idx_map[field] = idx
        self.fieldnames = fieldnames

    def _getindex(self, i):
        if i is None:
            return len(self)
        if isinstance(i, int):
            return i
        return self._idx_map.get(i, len(self))

    def __getitem__(self, idx):
        if isinstance(idx, str):
            idx = self._getindex(idx)
        if isinstance(idx, int):
            if idx < 0 or idx >= len(self):
                raise IndexError('CSVDictRow index out of range')
            return self.data[idx]
        if not isinstance(idx, slice):
            msg = ('CSVDictRow can only be indexed with integers, fieldnames, '
                   'or slices, not {}').format(type(idx).__name__)
            raise TypeError(msg)
        if idx.step is not None and not isinstance(idx.step, int):
            raise TypeError('slice indices must be integers or None or have an __index__ method')
        start = 0 if idx.start is None else self._getindex(idx.start)
        stop = self._getindex(idx.stop)
        return self.data[start:stop:idx.step]

    def cast(self, filters):
        if not filters:
            return self
        return CSVDictRow(self.fieldnames, self._cast_row(filters))


def cast_to_bool(s=None):
    if s is None:
        return False
    if isinstance(s, str):
        if s.lower() in ['true', 'yes']:
            return True
        elif s.lower() in ['false', 'no']:
            return False
    else:
        return bool(s)
    raise ValueError()


class CSVModel:
    def __init__(self, rows, types=None):
        max_len = max(map(len, rows))
        if types is None:
            casts = [int, float, cast_to_bool]
            types = [str]*max_len
            for i in range(max_len):
                # try to find the most specific cast
                for cast in casts:
                    try:
                        list(map(cast, (row[i] for row in rows if i < len(row))))
                    except ValueError:
                        continue
                    types[i] = cast
                    break
        elif len(types) != max_len:
            raise ValueError(('number of given types ({}) should match '
                              'number of columns ({})!').format(len(types), max_len))

        self.rows = []
        for row in rows:
            new_row = [t(row[i]) if i < len(row) else t() for i, t in enumerate(types)]
            self.rows.append(self._init_row(new_row))
        self.num_cols = max_len
        self.num_rows = len(rows)
        self.types = types

    def _init_row(self, row):
        return CSVRow(row)

    def cast(self, filters):
        new_rows = []
        for row in self.rows:
            new_rows.append(row.cast(filters))
        return self.__init__(new_rows, types=list(filters))

    def cast_range(self, filters, start=None, end=None):
        if not self.rows:
            return
        filterlen = len(filters)
        csvrow = self.rows[0]
        rangelen = len(csvrow[start:end])
        if rangelen != filterlen:
            raise ValueError('Number of filters ({}) should match number of columns ({})!'.format(filterlen, rangelen))
        new_filters = list(types)
        new_filters[csvrow._getindex(start):csvrow._getindex(end)] = filters
        return self.cast(new_filters)

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return self.num_rows

    def __reversed__(self):
        return reversed(self.rows)

    @classmethod
    def from_file(cls, filename):
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            return cls(list(reader))


class CSVDictModel(CSVModel):
    def __init__(self, fieldnames, rows, types=None):
        self.fieldnames = fieldnames
        super().__init__(rows, types)

    def _init_row(self, row):
        return CSVDictRow(self.fieldnames, row)

    def cast(self, filters):
        new_rows = []
        for row in self.rows:
            new_rows.append(row.cast(filters))
        return self.__init__(self.fieldnames, new_rows, types=list(filters))

    @classmethod
    def from_file(cls, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            rows = []
            for row in reader:
                rows.append(list(row[field] for field in reader.fieldnames))
            return cls(reader.fieldnames, rows)


