from trading.csv_trades import CSVTrades

class KucoinFromCSV(CSVTrades):
    def __init__(self, csv_file):
        super().__init__(csv_file)

    def extract_day(self, txn):
        return txn['time'].split(' ')[0]

    def extract_type(self, txn):
        return txn['type']


