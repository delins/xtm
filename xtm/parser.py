class Record():
    """Abstract base class for the three record types that are the rows in XDebug's CSV trace files."""
    def __init__(self, split=None, parent=None, rel_level=None):
        self.split = split
        self.parent = parent
        self.children = []
        self.rel_level = rel_level

    def parse(self):
        raise NotImplementedError('should be overwritten in subclasses!')

    def add_child(self, child):
        self.children.append(child)

    def tell_parent(self):
        self.parent.add_child(self)

    def visit(self, visitor):
        recurse = visitor.arrived_at(self)
        if recurse:
            visitor.down()
            for child in self.children:
                child.visit(visitor)
            visitor.up()


class RootRecord(Record):
    """Helper class that acts as root of the tree and doesn't represent any real row in the CSV file."""
    def __init__(self, level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = None
        self.level = level

    def parse(self):
        pass

    def visit(self, visitor):
        visitor.down()
        for child in self.children:
            child.visit(visitor)
        visitor.up()


class EntryRecord(Record):
    """Record that represents a function call."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._headers = [
            'level',
            'call_id',
            'time_index',
            'memory_usage',
            'function_name',
            'user_defined',
            'include_filename',
            'filename',
            'line_number',
            'n_params',
            'params',
        ]
        self.level = None
        self.call_id = None
        self.time_index = None
        self.memory_usage = None
        self.function_name = None
        self.user_defined = None
        self.include_filename = None
        self.filename = None
        self.line_number = None
        self.n_params = None
        self.params = None

    def parse(self):
        self.level = int(self.split[0])
        self.call_id = int(self.split[1])
        self.time_index = float(self.split[3])
        self.memory_usage = int(self.split[4])
        self.function_name = self.split[5]
        self.user_defined = bool(self.split[6])
        self.include_filename = self.split[7]
        self.filename = self.split[8]
        self.line_number = int(self.split[9])
        self.n_params = int(self.split[10])
        self.params = self.split[11 : ]


class ExitRecord(Record):
    """Record that represents a function's exit."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._headers = [
            'level',
            'call_id',
            'time_index',
            'memory_usage'
        ]
        self.level = None
        self.call_id = None
        self.time_index = None
        self.memory_usage = None

    def parse(self):
        self.level = int(self.split[0])
        self.call_id = int(self.split[1])
        self.time_index = float(self.split[3])
        self.memory_usage = int(self.split[4])


class ReturnRecord(Record):
    """Record that represents a function's return value."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._headers = [
            'level',
            'call_id',
            'return_value'
        ]
        self.level = None
        self.call_id = None
        self.return_value = None
        self.return_value = None

    def parse(self):
        self.level = int(self.split[0])
        self.call_id = int(self.split[1])
        self.return_value = (self.split[5])


class TraceParser():
    """Parses XDebug's CSV trace file and turns it into a call tree."""
    entry_map = {
        '0': EntryRecord,
        '1': ExitRecord,
        'R': ReturnRecord
    }

    def __init__(self, filename=None):
        if not filename:
            raise ValueError('filename cannot be empty')
        self.filename = filename
        self.version = None
        self.file_format = None
        self.trace_start = None
        self.trace_end = None


    def parse(self):
        with open(self.filename, 'r') as f:
            line = f.readline().rstrip('\n')
            self.version = line.split(':')[1].strip()
            line = f.readline().rstrip('\n')
            self.file_format = line.split(':')[1].strip()
            line = f.readline().rstrip('\n')
            self.trace_start = line.split('[')[1].rstrip(']')

            # Read the first line, which is bogus but tells us what level the RootRecord should be given
            line = f.readline().rstrip('\n')
            split = line.split('\t')
            level = int(split[0])
            self.root_record = RootRecord(level-1, rel_level=0)
            prev = self.root_record

            for line in f.readlines():
                line = line.rstrip('\n')
                split = line.split('\t')
                if split[0].isdigit():
                    level = int(split[0])
                    if level == prev.level:
                        parent = prev.parent
                    elif level == prev.level + 1:
                        parent = prev
                    else:
                        parent = prev.parent.parent
                    cls = TraceParser.entry_map[split[2]]
                    record = cls(split=split, parent=parent, rel_level=level-self.root_record.level - 1)
                    record.parse()
                    record.tell_parent()
                    prev = record
                else:
                    if split[0].startswith('TRACE END'):
                        self.trace_end = split[0].split('[')[1].rstrip(']')

    def format_meta(self):
        return 'filename: {}\nversion: {}\nfile_format: {}\ntrace_start: {}\ntrace_end: {}'.format(
            self.filename,
            self.version,
            self.file_format,
            self.trace_start,
            self.trace_end
        )
