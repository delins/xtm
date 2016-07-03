from ..parser import EntryRecord, ExitRecord, ReturnRecord
from .abstract_visitor import AbstractVisitor


class RecordFormatter():
    def __init__(self, single_indent='    ', relative_depth=True):
        self._single_indent = single_indent
        self._relative_depth = relative_depth

    def format(self, record, depth=0):
        return '{}{} - '.format(
            self._single_indent * record.rel_level,
            str(record.rel_level) if self._relative_depth else str(record.level),
        ) + self.specialised_format(record)


class EntryRecordFormatter(RecordFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def specialised_format(self, record):
        return '{}: {} {} ({})'.format(
            'E',
            record.call_id,
            record.function_name,
            record.params
        )


class ExitRecordFormatter(RecordFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def specialised_format(self, record):
        return '{}: {}'.format(
            'X',
            record.call_id
        )


class ReturnRecordFormatter(RecordFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def specialised_format(self, record):
        return '{}: {}'.format(
            'R',
            record.return_value
        )


class TreePrintingVisitor(AbstractVisitor):
    def __init__(self, single_indent='    ', relative_depth=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._formatters = {
            EntryRecord: EntryRecordFormatter(single_indent=single_indent, relative_depth=relative_depth),
            ExitRecord: ExitRecordFormatter(single_indent=single_indent, relative_depth=relative_depth),
            ReturnRecord: ReturnRecordFormatter(single_indent=single_indent, relative_depth=relative_depth)
        }

    def get_formatter(self, record):
        return self._formatters[type(record)]

