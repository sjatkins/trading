from enum import Enum
from app.schemas.base import BaseModel
from pydantic import Field
from typing import Optional
from trading import coingecko as cg

def coin_info(sym_id):
    return cg.CoinGeckoInfo(sym_id)

class Coin(BaseModel):
    sym_id: str

    @property
    def info(self):
        if not hasattr(self, _info):
            self._info = coin_info(self.sym_id)
        return self._info

    def current_price(self):
        return self.info.current_price()

class HistoryEvent(BaseModel):
    date: str

class BuyEvent(HistoryEvent):
    coin: Coin
    price_paid: float
    amount: float
    fee: float

class SellEvent(HistoryEvent):
    coin: Coin
    sell_price: float
    amount: float
    fee: float

class SwapEvent(HistoryEvent):
    from_coin: Coin
    to_coin: Coin

class PortfolioCoin(BaseModel):
    coin: Coin
    history: Optional[List[HistoryEvent]]
    current_amount: float

    def current_value(self):
        return current_amount * self.coin.current_price()



    def amount_spent(self):
        pass


class Portfolio:
    portfolio: List[PortfolioCoin]
