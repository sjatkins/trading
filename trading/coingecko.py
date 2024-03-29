import pycoingecko
from sja_utils import dicts as du
from trading import coin_info
from collections import defaultdict
from datetime import datetime

gecko = pycoingecko.CoinGeckoAPI()


def as_iso_day(a_date):
    if isinstance(a_date, datetime):
        return a_date.isoformat()[:10]
    if isinstance(a_date, float):  # epoch
        return datetime.utcfromtimestamp(a_date).isoformat()[:10]
    if '-' in a_date:
        parts = a_date.split('-')
        if len(parts[0]) == 4:
            return a_date
        else:
            return '-'.join(reversed(parts))


class CoinGeckoInfo(coin_info.CoinInfo):

    @classmethod
    def get_available_coins(cls):
        return gecko.get_coins_list()

    @classmethod
    def get_raw_detail(cls, an_id):
        return gecko.get_coin_by_id(an_id)
    
    @classmethod
    def get_coins_list(cls):
        """gets full details on all known coins"""
        return gecko.get_coins()

        
    def __init__(self, sym_id):
        super().__init__(sym_id)

    def get_spot(self, date=None, currency='usd'):
        return self.historical_price(date, currency=currency) if date else self.current_price(currency)

    def current_price(self, currency='usd'):
        self.refresh()
        return self.raw_current_price().get(currency)

    def get_detail(self):
        raw = self.get_raw_detail(self._info['id'])
        detail = self.clean_coin_data(raw)
        return raw, detail

    def historical_price(self, a_date, currency='usd'):
        yyyy_mm_dd = as_iso_day(a_date)
        parts = yyyy_mm_dd.split('-')
        cg_format = '-'.join(reversed(parts))
        h = gecko.get_coin_history_by_id(self._id, cg_format)
        hm = h['market_data']
        return hm['current_price'].get(currency)

    @classmethod
    def clean_coin_data(cls, raw):
        res = dict(raw)
        res.pop('localization')
        if res.get('decscription'):
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
        return self._detail['market_data']

    def percentage_change(self):
        mar = self.market_data()
        percents = {k:v for k,v in mar.items() if k.startswith('price_change_percentage') and not k.endswith('in_currency')}
        return {k.split('_')[-1]:v for k,v in percents.items()}

    def on_exchanges(self):
        return []


class Exchange(du.DictObject):
    _exchange_info =  {}
    _known = {}
    
    @classmethod
    def exchange_info(cls):
        if not cls._exchange_info:
            cls._exchange_info = {e['id']:e for e in gecko.get_exchanges_list()}
        return cls._exchange_info

    @classmethod
    def for_(cls, exchange_id):
        exchange = cls._known.get(exchange_id)
        if not exchange:
            exchange = cls(exchange_id)
            cls._known[exchange_id] = exchange
        return exchange

    def __init__(self, exchange_id):
        super().__init__(**self.exchange_info()[exchange_id])
        self._coin_pairs = {}
        self._coin_info = {}

    def coin_pairs(self):
        if not self._coin_pairs:
            data = gecko.get_exchanges_by_id(self.id)
            tickers = data['tickers']
            pairs = defaultdict(list)
            for pair in tickers:
                pairs[pair['base'].lower()].append(pair['target'].lower())
            self._coin_pairs = pairs
        return self._coin_pairs

    def coin_info(self):
        if not self._coin_info:
            self._coin_info = {k: CoinGeckoInfo.for_coin(k) for k in self.coin_pairs()}
            self._coin_info = {k:v for k,v in self._coin_info.items() if v}
        return self._coin_info

    def refresh_coin_info(self):
        self._coin_info.clear()
        
    def change_in_period(self, period, recompute_info=True):
        if recompute_info:
            self.refresh_coin_info()
        return {k: v.percentage_change()[period] for k,v in self.coin_info().items()}
        
    def change_24h(self):
        return {k: v.percentage_change()['24h'] for k,v in self.coin_info().items()}

    def change_1h(self):
        return {k: v.percentage_change()['1h'] for k,v in self.coin_info().items()}

    def change_7d(self):
        return {k: v.percentage_change()['7d'] for k,v in self.coin_info().items()}
    
    def change_30d(self):
        return {k: v.percentage_change()['30d'] for k,v in self.coin_info().items()}

    def sorted_period(self, period, recompute=True):
        data = {k:v for k,v in self.change_in_period(period, recompute).items() if v}
        return sorted(data.items(), key=lambda x:x[1])[::-1]
        
    def sorted_pairs(self, fn, recompute=True):
        
        return sorted(fn().items(), key=lambda x:x[1])[::-1]
    
    def sorted_1h(self):
        return self.sorted_pairs(self.change_1h)

    def sorted_24h(self):
        return self.sorted_pairs(self.change_24h)

    def sorted_7d(self):
        return self.sorted_pairs(self.change_7d)
        
    def sorted_30d(self):
        return self.sorted_pairs(self.change_30d)
            

    
if __name__ == '__main__':
    eth = CoinGeckoInfo('eth')
    print(eth)
