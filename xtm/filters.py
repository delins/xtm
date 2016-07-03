import json

from .parser import EntryRecord, ExitRecord, ReturnRecord


class Filter():
    """Base Filter class. Takes a ."""
    def __init__(self):
        self.visitor = None

    def add_visitor(self, visitor):
        """Used set the visitor that's using this filter. Useful to be able to tap into the 'parent' visitor's attributes."""
        self.visitor = visitor

    def filter(self, record):
        """Filters Records. Takes a Record and returns True if the Record matches the filter."""
        return True


class MaxDepthFilter(Filter):
    """Returns True if the current record's depth is no deeper than the max_depth."""
    def __init__(self, max_depth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_depth = max_depth

    def filter(self, record):
        return self.visitor.depth <= self.max_depth


class MaxRecordsFilter(Filter):
    """Returns True if number of printed records doesn't exceed max_records."""
    def __init__(self, max_records, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_records = max_records

    def filter(self, record):
        return self.visitor.records <= self.max_records


class ExitFilter(Filter):
    """Returns True if the current record is of type ExitRecord.

    Inverses the result if inverse=True is given to the constructor."""
    def __init__(self, inverse=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inverse = inverse

    def filter(self, record):
        result = type(record) == ExitRecord
        if self.inverse:
            result = not result
        return result


class ReturnFilter(Filter):
    """Returns True if the current record is of type ReturnRecord.

    Inverses the result if inverse=True is given to the constructor."""
    def __init__(self, inverse=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inverse = inverse

    def filter(self, record):
        result = type(record) == ReturnRecord
        if self.inverse:
            result = not result
        return result


class FunctionNameFilter(Filter):
    """Returns True if the Record describes a function whose name is in function_names.

    ExitRecords and ReturnRecords are matched to their EntryRecord counterpart. If an EntryRecord is found to match,
    The related Records are filtered in the same way.

    Note that under some circumstances the EntryRecord may have been filtered away by another function so that it never
    goes through this filter and in result the corresponding Exit and Return Records are not known about. In this case
    these corresponding Records are left alone.

    Inverses the result if inverse=True is given to the constructor."""
    def __init__(self, function_names=None, inverse=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.function_names = function_names or set()
        self.inverse = inverse
        self.call_id_set = set()

    def filter(self, record):
        if type(record) == EntryRecord:
            result = record.function_name in self.function_names
            if result:
                self.call_id_set.add(record.call_id)
        else:
            result = record.call_id in self.call_id_set
        if self.inverse:
            result = not result
        return result


class FilenameFilter(Filter):
    """Returns True if the Record is defined in a file whose name starts with startswith.

    ExitRecords and ReturnRecords are matched to their EntryRecord counterpart. If an EntryRecord is found to match,
    The related Records are filtered in the same way.

    Note that under some circumstances the EntryRecord may have been filtered away by another function so that it never
    goes through this filter and in result the corresponding Exit and Return Records are not known about. In this case
    these corresponding Records are left alone.

    Inverses the result if inverse=True is given to the constructor."""
    def __init__(self, startswith=None, inverse=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._startswith = startswith or ''
        self._inverse = inverse
        self._call_id_set = set()

    def filter(self, record):
        if type(record) == EntryRecord:
            result = record.filename.startswith(self._startswith)
            if result:
                self._call_id_set.add(record.call_id)
        else:
            result = record.call_id in self._call_id_set
        if self._inverse:
            result = not result
        return result


class FilterConfig():
    _class_map = {
        'MaxDepthFilter': MaxDepthFilter,
        'MaxRecordsFilter': MaxRecordsFilter,
        'ExitFilter': ExitFilter,
        'ReturnFilter': ReturnFilter,
        'FunctionNameFilter': FunctionNameFilter,
        'FilenameFilter': FilenameFilter
    }
    def __init__(self, filter_definitions=None):
        self._pre_filters = []
        self._in_filters = []
        self._post_filters= []

        if filter_definitions:
            self._filter_definitions = json.loads(filter_definitions)

            for filter in self._filter_definitions['pre_filters']:
                filter = self.construct_filter(filter)
                if filter:
                    self._pre_filters.append(filter)

            for filter in self._filter_definitions['in_filters']:
                filter = self.construct_filter(filter)
                if filter:
                    self._in_filters.append(filter)

            for filter in self._filter_definitions['post_filters']:
                filter = self.construct_filter(filter)
                if filter:
                    self._post_filters.append(filter)

    def construct_filter(self, filter):
        cls = FilterConfig._class_map.get(filter['class'])
        if cls:
            parameters = filter['parameters']
            return cls(**parameters)

    def format(self):
        return 'Pre filters:\n{}\nIn filters:\n{}\nPost filters:\n{}'.format(
            '\n'.join(['\t' + filter.__class__.__name__ for filter in self._pre_filters]),
            '\n'.join(['\t' + filter.__class__.__name__ for filter in self._in_filters]),
            '\n'.join(['\t' + filter.__class__.__name__ for filter in self._post_filters])
        )

    @property
    def pre_filters(self):
        return self._pre_filters

    @property
    def in_filters(self):
        return self._in_filters

    @property
    def post_filters(self):
        return self._post_filters
