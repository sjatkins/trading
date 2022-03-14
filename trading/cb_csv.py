import csv
from trading.csv_trades import CSVTrades

class CoinbaseFromCSV(CSVTrades):
    def __init__(self, csv_file, earliest_day=None):
        super().__init__(csv_file, earliest_day=earliest_day)

    def extract_day(self, txn):
        return txn['Timestamp'].split('T')[0]

    def extract_type(self, txn):
        return txn['Transaction Type']
