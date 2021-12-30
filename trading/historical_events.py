from enum import Enum
from pydantic import Field, root_validator, BaseModel
from typing import Optional, List
from trading import coingecko as cg

import time


def coin_info(sym_id):
    return cg.CoinGeckoInfo(sym_id)

class HistoryEvent:
    def __init__(self, date=None):
        self._date = time.time()
        self._fee = None

    def compute_fee(self):
        return 0.0

    @property
    def fees_and_overhead(self):
        if self._fee is None:
            self._fee = self.compute_fee()
        return self._fee


class SingleHistoryEvent(HistoryEvent):
    def __init__(self, sym_id, amount, date=None):
        super().__init__(date)
        self._coin = coin_info(sym_id)
        if date:
            self._spot_price = self._coin.historical_price(date)
        else:
            self._spot_price = self._coin.current_price()
        self._amount = amount


class BuyEvent(SingleHistoryEvent):
    def __init__(self, sym_id, amount, amount_spent, date=None):
        super().__init__(sym_id, amount, date=date)
        self._amount_spent = amount_spent

    def compute_fee(self):
        return self._amount_spent - self._amount * self._spot_price

class SellEvent(SingleHistoryEvent):
    def __init__(self, sym_id, amount, amount_received, date=None):
        super().__init__(sym_id, amount, date=date)
        self._amount_received = amount_received

    def compute_fee(self):
        return self._amount * self._spot_price - self._amount_received

class SwapEvent(HistoryEvent):
    def __init__(self, from_id, to_id, amount_converted, amount_received, date=None):
        super().__init__(date)
        self._from_amount = amount_converted
        self._from = coin_info(from_id)
        self._from_spot = self._from.get_spot(date)
        self._to = coin_info(to_id)
        self._to_spot = self._to.get_spot(date)
        self._to_amount = amount_received
        self._to_spot = self._to.get_spot(date)



    def cempute_fee(self):
        from_value = self._from_amount * self._from_spot
        received = self._to_amount * self._to_spot
        return from_value - received




class PortfolioCoin(BaseModel):
    coin: Coin
    history: Optional[List[HistoryEvent]]
    current_amount: float

    def current_value(self):
        return self.current_amount * self.coin.current_price()



    def amount_spent(self):
        pass


class Portfolio:
    portfolio: List[PortfolioCoin]
