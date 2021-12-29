from collections import defaultdict

class IdOrSymbol:
    def __init__(self, as_list=None):
        self.update_list(as_list or [])

    def update_list(self, as_list):
        self._list = as_list
        self._by_id = {i['id']: i for i in as_list}
        self._ids_by_symbol = defaultdict(set)
        for k,v in self._by_id.items():
            self._ids_by_symbol[v['symbol']].add(k)

    @property
    def as_list(self):
        return self._list

    @property
    def by_id(self):
        return self._by_id

    def add_info(self, info):
        the_id = info.get('id')
        symbol = info.get('symbol')
        if the_id and symbol:
            if the_id not in self._by_id:
                self._by_id[the_id] = info
                self._ids_by_symbol[symbol].add(the_id)
        return info

    def get_by_symbol(self, symbol):
        ids = self._ids_by_symbol.get(symbol, set())
        return [self.get_id(i) for i in ids]

    def get_symbol_id(self, symbol):
        return list(self._ids_by_symbol.get(symbol, []))

    def get_id(self, an_id):
        return self.by_id.get(an_id)

    def get_symbol_or_id(self, sym_id):
        at_id = self.get_id(sym_id)
        if at_id:
           return at_id
        else:
            return self. get_by_symbol(sym_id)


class CoinInfo:
    """
    General Coin information class with ability to cache per coin information.  There will be subclasses for various API sources of crypto coin information.
    """
    KnownCoins = {}
    Coins = IdOrSymbol()
    CoinDetail = IdOrSymbol()
    _aliases = dict(
        bchsv='bsv'
    )

    @classmethod
    def get_available_coins(cls):
        """basic coin info list"""
        return []

    @classmethod
    def coins(cls):
        if not cls.Coins.as_list:
            cls.Coins.update_list(cls.get_available_coins())
        return cls.Coins

    @classmethod
    def coin_list(cls):
        return cls.coins().as_list

    @classmethod
    def get_coins_list(cls):
        """Gets list of basic coin info for provider"""
        return []


    @classmethod
    def coin_id(cls, sym_or_id):
        coin = cls.coins().get_id(sym_or_id)
        if coin:
            return sym_or_id
        else:
            ids = cls.coins().get_id(sym_or_id)
            if ids:
                if len(ids) == 1:
                    return ids[0]
                else:
                    infos = cls.coins().get_by_symbol(sym_or_id)
                    raise Exception(f'ambiguous symbol. choose id from: {infos}')

    @classmethod
    def get_raw_detail(cls, an_id):
        return {}

    @classmethod
    def coin_detail(cls, an_id):
        detail = cls.CoinDetail.get_id(an_id)
        if not detail:
            detail = cls.CoinDetail.add_info(cls.get_raw_detail(an_id))
        return detail


    @classmethod
    def for_coin(cls, sym_id):
        the_id = cls.coin_id(sym_id)
        known = cls.KnownCoins.get(the_id)
        if not known:
            known = cls(the_id)
            cls.KnownCoins[the_id] = known
        return known

    def __init__(self, sym_id):
        self._id = self.coin_id(sym_id)
        self._info = self.coin_detail(self._id)
        assert (self._info)
        self._raw_detail, self._detail = self._info, self.clean_coin_data(self._info)

    @property
    def id(self):
        return self._id

    @property
    def symbol(self):
        return self._info['symbol']

    def raw_current_price(self):
        return self._raw_detail['market_data']['current_price']

    def refresh(self):
        self._raw_detail, self._detail = self.get_detail()
        self._detail = self.clean_coin_data(self._raw_detail)

    def get_detail(self):
        return {}, {}

    def percentage_change(self):
        return {}
    
    @classmethod
    def clean_coin_data(self, raw):
        """
        API specific cleanup for interests of this module.
        Fixes to the current currency (default 'usd')
        Fixes to the current language (default 'en')
        """
        return raw
    
    def market_data(self):
        return self._detail['market_data']
    
    def price_changes(self):
        mar = self.market_data()
        pass

    def on_exchanges(self):
        return []

    
    
    
