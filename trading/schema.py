from enum import Enum
from pydantic import Field, root_validator, BaseModel
from typing import Optional, List
from trading import coingecko as cg

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
    date: str
    sym_id: str
    spot_price: float
    amount: float

    def fees_and_overhead(self):
        return 0.00

class BuyEvent(HistoryEvent):
    coin: Coin
    amount_spent: float  # dollar_value

    def fees_and_overhead(self):
        return self.amount_spent - self.amount * self.spot_price

class SellEvent(HistoryEvent):
    coin: Coin
    amount_received: float

    def fees_and_overhead(self):
        return self.amount_received - self.amount * self.spot_price

class SwapEvent(BaseModel):
    from_id: str
    from_coin: Coin
    from_amount: float
    from_spot: float
    to_id: str
    to_coin: Coin
    to_spot: float
    to_amount: float
    fees: float = 0.00


    @root_validator()
    def validate(self, values):
        values['from_coin'] = coin_info(self.from_id)
        values['from_spot'] = values['from_coin'].current_price()
        values['to_coin'] = coin_info(self.to_id)
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
