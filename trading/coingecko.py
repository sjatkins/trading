import pycoingecko
from trading import coin_info

gecko = pycoingecko.CoinGeckoAPI()

class CoinGeckoInfo(coin_info.CoinInfo):
    _known = {}
    _coins = []
    _info_by_id = {}
    _info_by_symbol = {}

    @classmethod
    def get_coins_list(cls):
        return gecko.get_coins_list()
            
    def __init__(self, sym_id):
        super().__init__(sym_id)

    def current_price(self):
        self.refresh()
        return self.market_data()['current_price']

    def get_detail(self):
        raw = gecko.get_coin_by_id(self._info['id'])
        detail = self.clean_coin_data(raw)
        return raw, detail

    def clean_coin_data(self, raw):
        res = dict(raw)
        res.pop('localization')
        res['description'] = res['description']['en']
        mar_data = {}
        for k,v in res['market_data'].items():
            if isinstance(v, dict) and  'usd' in v:
                mar_data[k] = v['usd']
            else:
                mar_data[k] = v
        res['market_data'] = mar_data
        return res
        

    def market_data(self):
        return self._details['market_data']

    def on_exchanges(self):
        return []

    
if __name__ == '__main__':
    eth = CoinGeckoInfo('eth')
    print(eth)
