from trading import coingecko as cg
import time

class PorfolioPosition:
    def __init__(self, sym_id):
        self._coin_info = cg.CoinGeckoInfo(sym_id)
        self._history = []
        self._amount = 0.0
        self._avg_price = 0.0
        self._total_received = 0.0
        self._percentage = 0.0

    @property
    def percentage(self):
        return self._percentage

    def current_value(self):
        return self._amount * self._coin_info.current_price()

    def spent_value(self):
        return self._amount * self._avg_price

    def percent_change(self):
        return 100.0 * (self._total_received + self.current_value()) / self.spent_value()

    def adjust(self):
        buys = [h for h in self._history if h['']]

    def buy(self, price, quantity):
        self._history.append(dict(when=time.time(), amount=quantity, price=price))
        self.adjust()
        return self

    def sell(self, quantity, price=0.0):
        if not price:
            price = self._coin_info.current_price()
        self._history.append(dict(when=time.time(), amount=-1 * quantity, price=price))
        self.adjust()

class Portfolio:
    def __init__(self, name):
        self._name = name
        self._positions = {}

    def set_position_percentage(self, sym_id, percentage):
        position = self._positions.get(sym_id)
        if position:
            position.percentage = percentage

    def total_value(self):
        return sum(p.current_value() for p in self._positions.values())

    def ratio_adjustments(self):
        with_precent = {k:v for k,v in self._positions if v.percentage}
        total_pool = sum(v.current_value for v in self._positions.values())

    def add_position(self, sym_id, amount=0.0, price=0.0, balance_precentage=None):
        position = self.get_position(sym_id, add_if_missing=bool(amount))
        if position:
            if amount > 0:
                position.buy(price, amount)
            else:
                position.sell(amount, price)

    def get_position(self, sym_id, add_if_missing=False):
        if sym_id not in self._positions:
            if add_if_missing:
                self._positions[sym_id] = PorfolioPosition(sym_id)
        return self._positions.get(sym_id)