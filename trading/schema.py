from enum import Enum
from pydantic import Field, root_validator, BaseModel
from typing import Optional, List
from trading import coingecko as cg
import time


def coin_info(sym_id):
    return cg.CoinGeckoInfo(sym_id)

class Coin(BaseModel):
    sym_id: str

    @property
    def info(self):
        if not hasattr(self, '_info'):
            self._info = coin_info(self.sym_id)
        return self._info

    def current_price(self):
        return self.info.current_price()

class HistoryEvent(BaseModel):
    date: str = Field(default_factory=time.time)

    def fees_and_overhead(self):
        return 0.00

class SingleHistoryEvent(BaseModel):
    sym_id: str
    coin: Coin
    spot_price: float
    amount: float

    @root_validator
    def validate(self, values):
        if not values['coin']:
            values['coin'] = Coin.sym_id
        values['spot_price'] = values['coin'].current_price()

    def fees_and_overhead(self):
        return 0.00

class BuyEvent(SingleHistoryEvent):
    amount_spent: float  # dollar_value

    def fees_and_overhead(self):
        return self.amount_spent - self.amount * self.spot_price

class SellEvent(SingleHistoryEvent):
    amount_received: float

    def fees_and_overhead(self):
        return self.amount_received - self.amount * self.spot_price

class SwapEvent(HistoryEvent):
    from_coin: Coin
    from_spot: float
    to_coin: Coin
    to_spot: float
    from_amount: float
    to_amount: float
    fees: float = 0.00


    @root_validator()
    def validate(self, values):
        values['from_spot'] = self.from_coin.current_price()
        values['to_spot'] = values['to_coin'].current_price()
        from_value = values['from_spot'] * self.from_amount
        to_value = self.to_amount * values['to_spot']
        from_value = values['from_spot'] * self.from_amoun
        values['fees'] = from_value - to_value
        return values

    def fees_and_overhead(self):
        return self.fees




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
