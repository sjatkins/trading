class CoinInfo:
    """
    General Coin information class with ability to cache per coin information.  There will be subclasses for various API sources of crypto coin information.
    """
    _known = {}
    _available_coins = []
    _availble_by_symbol = {}
    _available_by_id = {}
    _coins = []
    _info_by_id = {}
    _info_by_symbol = {}
    _aliases = dict(
        bchsv='bsv'
    )

    @classmethod
    def available_coins(cls):
        if not cls._available_coins:
            cls._available_coins = cls.get_available_coins()
            cls._available_by_id = {c['id']:c for c in cls._available_coins}
            cls._available_by_symbol = {c['symbol'].lower():c for c in cls._available_coins}
        return cls._available_coins

    @classmethod
    def coin_id(cls, sym_or_id):
        if not cls._available_coins:
            cls.available_coins()
        info = cls._available_by_id.get(sym_or_id) or cls._available_by_symbol.get(sym_or_id)
        return info['id']
        
            
    @classmethod
    def get_coins_list(cls):
        return []
    
    @classmethod
    def coins(cls):
        if not cls._coins:
            cls._coins = cls.get_coins_list()
        return cls._coins

    @classmethod
    def get_raw_detail(cls, an_id):
        return cls.info_by_id.get(an_id)

    @classmethod
    def add_coin(cls, sym_or_id):
        the_id = cls.coin_id(sym_or_id)
        if the_id:
            raw = cls.get_raw_detail(the_id)
            cls._coins.append(raw)
            cls._info_by_id[the_id] = raw
            cls._info_by_symbol[the_id] = raw
            return raw
            
            
        
    @classmethod
    def info_by_id(cls, an_id):
        if not cls._info_by_id:
            cls._info_by_id = {c['id']:c for c in cls.coins()}
        return cls._info_by_id.get(an_id) or cls.add_coin(an_id)
    
    @classmethod
    def info_by_symbol(cls, sym):
        if not cls._info_by_symbol:
            cls._info_by_symbol = {c['symbol'].lower():c for c in cls.coins()}
        return cls._info_by_symbol.get(sym) or cls.add_coin(sym)
    

    @classmethod
    def for_coin(cls, sym_id):
        sym_id = cls._aliases.get(sym_id, sym_id)
        res = cls._known.get(sym_id)
        if not res:
            res = cls(sym_id)
            cls._known[sym_id] = res
        return res

    def __init__(self, sym_id):
        self._info = self.info_by_symbol(sym_id) or self.info_by_id(sym_id)
        assert(self._info)
        self._raw_detail, self._detail = self._info, self.clean_coin_data(self._info)

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

    
    
    
