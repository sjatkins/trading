from trading import coingecko as cg
import json, time

class PortfolioPosition:
    def __init__(self, sym_id, history=None):
        self._coin_info = cg.CoinGeckoInfo(sym_id)
        self._history = history or []
        self._amount = 0.0
        self._avg_price = 0.0
        self._percentage = 0.0

    @property
    def symbol(self):
        return self._coin_info.symbol

    def __repr__(self):
        return repr(dict(
            symbol=self._coin_info.symbol,
            **self.standard_info()))

    def standard_info(self):
        return dict(
            amount=self._amount,
            avg_price=self._avg_price,
            change = self.percent_change(),
            percents = self.percentages()
        )

    def to_json(self):
        return dict(
            sym_id = self._coin_info.symbol,
            history = self._history,
        )

    @classmethod
    def from_json(cls, data):
        position = cls(**data)
        position.adjust()
        return position
    
    @property
    def percentage(self):
        return self._percentage

    def percentages(self):
        return self._coin_info.percentage_change()

    def current_value(self):
        return self._amount * self._coin_info.current_price()

    def current_price(self):
        return self._coin_info.current_price()

    def spent_value(self):
        return self._amount * self._avg_price

    def percent_change(self):
        return 100.0 * (self.current_value() / self.spent_value() - 1)

    def adjust(self):
        self._amount = sum([h['amount'] for h in self._history])
        buys = [h['price'] for h in self._history if h['amount'] > 0]
        self._avg_price = sum(buys) / len(buys)
        
    def buy(self, price, quantity):
        if not price:
            price = self._coin_info.current_price()
        self._history.append(dict(when=time.time(), amount=quantity, price=price))
        self.adjust()
        return price * quantity * -1

    def sell(self, quantity, price=0.0):
        if not price:
            price = self._coin_info.current_price()
        self._history.append(dict(when=time.time(), amount=-1 * quantity, price=price))
        self.adjust()
        return price * quantity

    def change_price(self, quantity, price=0.0):
        if not price:
            price = self._coin_info.current_price()
        return quantity * price


class Portfolio:
    def __init__(self, name, starting_cash=0.0, positions=None):
        self._name = name
        self._positions = positions or {}
        self._cash = starting_cash

    def to_json(self):
        return dict(
            name=self._name,
            positions = {p.symbol:p.to_json() for p in self._positions.values()},
            starting_cash = self._cash
        )

    @classmethod
    def from_json(cls, data):
        data['positions'] = {k: PortfolioPosition.from_json(v) for k,v in data['positions'].items()}
        return cls(**data)
            

    def add_cash(self, amount):
        cash += amount

    def positions(self):
        return {k:v.standard_info() for k,v in self._positions.items()}
    
    def get_position(self, sym_id):
        return self._positions.get(sym_id)

    def set_position_percentage(self, sym_id, percentage):
        position = self._positions.get(sym_id)
        if position:
            position.percentage = percentage

    def free_cash(self):
        return self._cash
    
    def total_value(self):
        return self._cash + sum(p.current_value() for p in self._positions.values())

    def ratio_adjustments(self):
        with_precent = {k:v for k,v in self._positions if v.percentage}
        total_pool = sum(v.current_value for v in self._positions.values())

    def add_position(self, sym_id, amount=0.0, price=0.0, dollar_amount=None, balance_percentage=None):
        
        position = self.get_position(sym_id, add_if_missing=True)
        if position:
            if balance_percentage:
                position_percentage = percentage
                if not(amount or dollar_amount):
                    dollar_amount = min(self._cash, self.total_value() * balance_percentage / 100.0)
            if dollar_amount:
                amount = dollar_amount / position.current_price()                
            if amount:
                if amount > 0:
                    if position.change_price(amount, price) > self._cash:
                        raise Exception('Not enough funds')
                    self._cash += position.buy(price, amount)
                else:
                    self._cash += position.sell(amount, price)

                    
    def sell_position(self, sym_id, amount=0.0, price=0.0, dollar_amount=None):
        position = self._positions.get(sym_id)
        if position:
            cash = self.add_position(sym_id, amount, price, dollar_amount)
            self._cash += cash
        

    def get_position(self, sym_id, add_if_missing=False):
        if sym_id not in self._positions:
            if add_if_missing:
                self._positions[sym_id] = PortfolioPosition(sym_id)
        return self._positions.get(sym_id)
