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


    def profit_loss(self):
        pass

    def extract_coin(self, txn):
        pass

    def by_type(self, txns=None):
        txns = txns or self._raw_data
        res = defaultdict(list)
        for txn in txns:
            res[self.extract_type(txn)].append(txn)
        return dict(res)

    def by_pair(self, txns=None):
        txns = txns or self._raw_data
        res = defaultdict(list)
        for txn in self._raw_data:
            res[self.extract_coin(txn)].append(txn)
        return dict(res)

    def by_pair_type(self):
        return {k: self.by_type(v) for k,v in self.by_pair().items()}

    def by_type_pair(self):
        return {k: self.by_pair(v) for k,v in self.by_type().items()}

