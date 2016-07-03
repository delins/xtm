class AbstractVisitor():
    def __init__(self, filter_config=None):
        self.depth = 0
        self.records = 0
        if not filter_config:
            raise ValueError('filter_config cannot be left out.')
        self.pre_filters = filter_config.pre_filters
        for filter in self.pre_filters:
            filter.add_visitor(self)
        self.post_filters = filter_config.post_filters
        for filter in self.post_filters:
            filter.add_visitor(self)
        self.in_filters = filter_config.in_filters
        for filter in self.in_filters:
            filter.add_visitor(self)


    def arrived_at(self, record):
        result = []
        if not all([filter.filter(record) for filter in self.pre_filters]):
            return False
        else:
            if all([filter.filter(record) for filter in self.in_filters]):
                formatter = self.get_formatter(record)
                print(formatter.format(record=record, depth=self.depth))
                self.records += 1
            return all([filter.filter(record) for filter in self.post_filters])

    def get_formatter(self):
        raise NotImplementedError()

    def up(self):
        self.depth -= 1

    def down(self):
        self.depth += 1