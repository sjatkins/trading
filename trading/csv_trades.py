import csv
from collections import defaultdict


class CSVTrades:
    def __init__(self, csv_file, earliest_day=None):
        with open(csv_file) as f:
            self._raw_data = [x for x in csv.DictReader(f)]
        if earliest_day:
            self._raw_data = [d for d in self._raw_data if self.extract_day(d) >= earliest_day]

    def extract_day(self, txn):
        pass

    def extract_type(self, txn):
        pass

    def by_pair(self):
        pass

    def by_coin(self):
        pass

    def profit_loss(self):
        pass


    def by_type(self):
        res = defaultdict(list)
        for txn in self._raw_data:
            res[self.extract_type(txn)].append(txn)
        return res
