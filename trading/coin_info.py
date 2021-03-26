class CoinInfo:
    """
    General Coin information class with ability to cache per coin information.  There will be subclasses for various API sources of crypto coin information.
    """
    _known = {}
    _coins = []
    _info_by_id = {}
    _info_by_symbol = {}

    @classmethod
    def get_coins_list():
        return []
    
    @classmethod
    def coins(cls):
        if not cls._coins:
            cls._coins = cls.get_coins_list()
        return cls._coins
    
    @classmethod
    def info_by_id(cls, an_id):
        if not cls._info_by_id:
            cls._info_by_id = {c['id']:c for c in cls.coins()}
        return cls._info_by_id.get(an_id)
    
    @classmethod
    def info_by_symbol(cls, sym):
        if not cls._info_by_symbol:
            cls._info_by_symbol = {c['symbol']:c for c in cls.coins()}
        return cls._info_by_symbol.get(sym)
    

    @classmethod
    def for_coin(cls, sym_id):
        res = cls._known.get(sym_id)
        if not res:
            res = cls(sym_id)
            cls._known[sym_id] = res
        return res

    def __init__(self, sym_id):
        self._info = self.info_by_symbol(sym_id) or self.info_by_id(sym_id)
        assert(self._info)
        self._raw_detail, self._detail = self.get_detail() 
        self._details = self.clean_coin_data()


    def get_detail(self):
        return {}, {}

    
    
    def refresh():
        """
        Refreshes the subparts of the information likely to go stale on demand.
        """
        pass
    
    def clean_coin_data(self, raw):
        """
        API specific cleanup for interests of this module.
        Fixes to the current currency (default 'usd')
        Fixes to the current language (default 'en')
        """
        return raw
    
    def market_data(self):
        return self._details['market_data']
    
    def price_changes(self):
        mar = self.market_data()
        pass
    
    
