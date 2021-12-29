class UnknownCoin(Exception):
    def __init__(self, sym_id):
        super().__init__('cannont find coin %s' % sym_id)