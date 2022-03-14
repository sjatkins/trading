from trading import coingecko as cg
from trading import historical_events as he
import json, time, os
import trading

data_path = os.path.join(trading.__path__[0], 'data')
portfolios_path = os.path.join(data_path, 'portfolios')

class CashReserve:
    All_Reserves = {} # CashReserves by currency type

    @classmethod
    def add_to_reserves(cls, amount, currency):
        if currency in cls.All_Reserves:
            cls.All_Reserves[currency].add_amount(amount)
        else:
            cls.All_Reserves[currency] = cls(amount, currency=currency)

    def __init__(self, amount=0, currency='USD'):
        self._amount = amount
        self._currency = currency

    def add_amount(self, amount):
        self._amount += amount

    def convert_to_currency(self, amount, to_currency):
        pass


class PortfolioPosition:
    def __init__(self, sym_id, history=None):
        self._coin_info = cg.CoinGeckoInfo(sym_id)
        self._history = history or []
        self._amount = 0.0
        self._avg_price = 0.0

    def add_event(self, event):
        self._history.append(event)
        if isinstance(event, he.SellEvent):
            self._amount -= event._amount
        elif isinstance(event, he.BuyEvent):
            self._amount += event._amount
        elif isinstance(event, he.SwapEvent):
            amount = -event._from_amount if event._from._id == self._coin_info._id else event._to_amount
            self._amount += amount

    def total_fees(self):
        return sum(h._fee for h in self._history)

    def swap_total(self):
        """amount + sport + overhead"""
        events = [h for h in self._history if isinstance(h, he.SwapEvent) and h._to._id == self._coin_info._id]
        return sum(h._from_amount * h._from_spot for h in events)

    def buy_total(self):
        return sum(h._amount_spent for h in self._history if isinstance(h, he.BuyEvent))

    def total_spent(self):
        return self.buy_total() + self.swap_total()

    def sell_total(self) -> float:
        pass

    def exchange_sell_total(self) -> float:
        pass

    def total_recieved(self):
        return self.sell_total() + self.exchange_sell_total()

    def profit_loss(self):
        return self.total_recieved() - self.total_spent()

    def sell_all(self):
        return self.sell(self._amount, amount_recieved=0)

    def sell_percentage(self, percentage):
        amt = self._amount * percentage / 100.0
        return self.sell(quantity=amt)

    def adjust_to(self, amount=0.0, dollar_amount=0.0):
        if dollar_amount:
            amount = dollar_amount / self._coin_info.current_price()
        change = amount - self._amount
        if change:
            if change > 0:
                return self.buy(quantity=change)
            else:
                return self.sell(quantity=change)
        return 0.0
    
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
        """
        Should be sum of spent value which has nothing to do with amount left
        :return:
        """
        return self._amount * self._avg_price

    def percent_change(self):
        return 100.0 * (self.current_value() / self.spent_value() - 1)

    def received_dividend(self, amount, date=None):
        pass

    def bought(self, amount_spent, quantity, date=None):
        event = he.BuyEvent(self._coin_info._id, amount=quantity, amount_spent=amount_spent, date=date)
        self.add_event(event)

    def sold(self, amount_received, quantity=None, date=None):
        if quantity is None:
            quantity = self._amount
        event = he.SellEvent(self._coin_info._id, quantity, amount_received, date)
        self.add_event(event)


class Portfolio:
    def __init__(self, positions=None):
        self._positions = positions or {}

    def get_position(self, sym_id):
        cid = cg.CoinGeckoInfo.coin_id(sym_id)
        if not cid in self._positions:
            self._positions[cid] = PortfolioPosition(cid)
        return self._positions[cid]

    def bought(self, sym_id, amount_spent, amount=None, date=None):
        position: PortfolioPosition = self.get_position(sym_id)
        position.bought(amount, amount_spent, date)

    def sold(self, sym_id, amount, amount_received, date=None):
        position: PortfolioPosition = self.get_position(sym_id)
        position.sold(amount, amount_received, date)

    def exchange(self, from_id, amount_coverted, to_id, amount_received):
        pass

    def total_value(self):
        pass

    def total_spent(self):
        pass



    
class StandardPosition(PortfolioPosition):
    pass

class ScheduledAddedAmount:
    """
    The idea here is that for some positions there is a planned schedule of adding more, usually via fiat,
    to the position.  Some possible considerations are
    a) efficiency/cost of mechanism for fiat to final or interim currency
    b) efficiency/cost of conversion to final currency
    Those mechanism can perhaps be handle by a mix of the normal buy sell exchange which include noting
    fees.
    As different target coins/tokens have possible different intermediate steps from fiat to target subclassing
    is one possibility or simlpy having the actual PortfolioPosition provide a from fiat set of methods and run that
    through the portfolio.  Leaving only the schedule and amount as uniquely to be taken cane of here.

    Since these tools do not initiate trades and rengotiation such sub parts the only real use for this currencly
    is as an accounting mechanism and something to hang suck join actions off of.  It could be used in future value
    calculations under different fiat input scenarios.
    """
    def __init__(self, coin, how_often_days, dollar_amount):
        self._coin = coin
        self._how_often=how_often_days
        self._dollar_amount = dollar_amount # total of account in

    def coin_amount(self):
        pass

one_day = 24*60*60


class StakedPosition(PortfolioPosition):
    def __init__(self, primary_coin, reward_coin, daily_rate, scheduled_add=None, history=None, compounding=True, overhead_cost=None):
        self._reward_coin = reward_coin
        self._compounding = compounding
        self._daily_rate = daily_rate
        super().__init__(primary_coin, history=history)
        self._scheduled = scheduled_add

    def total_invested(self, until_when=None):
        now = time.time()
        until_when = until_when or now
        investments = sum([h['amount'] for h in self._history if h['type'] == 'invested' and h['when'] < until_when])
        return investments

    def total_coins(self, until_when=):

    def total_value(self, until_when=None):
        until_when = until_when or time.time()






class Portfolio:
    def __init__(self, name, starting_cash=0.0, positions=None):
        self._name = name
        self._positions = positions or {}
        self._cash = starting_cash
        self._profit = 0.0

    def to_json(self):
        return dict(
            name=self._name,
            positions = {p.symbol:p.to_json() for p in self._positions.values()},
            starting_cash = self._cash
        )

    def save(self):
        data = self.to_json()
        path = os.path.join(portfolios_path, '%s.json' % self._name)
        with open(path, 'w') as f:
            json.dump(data, f)
    
    @classmethod
    def from_json(cls, data):
        data['positions'] = {k: PortfolioPosition.from_json(v) for k,v in data['positions'].items()}
        return cls(**data)
            

    def add_cash(self, amount):
        self._cash += amount

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

    def remove_position(self, sym_id):
        pos = self._positions.pop(sym_id, None)
        if pos:
            self._cash += pos.sell_all()
        
    def split_evenly(self, remove_others=False, *symbols):
        if symbols:
            if remove_others:
                to_remove = set(self._positions.keys()) - set(symbols)
                for sym in to_remove:
                    self.remove_position(sym)
            to_add = set(symbols) - set(self._positions.keys())
            for sym in to_add:
                self.get_position(sym, True)

        amount = self.total_value() - self._profit
        per_position = amount / len(self._positions)

        # TODO do any remaining sells before buys to ensure funds

        for pos in self._positions.values():
            self._cash += pos.adjust_to(dollar_amount=per_position)

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

def saved_portfolios():
    saved = {}
    possibles = [f for f in os.listdir(portfolios_path) if f.endswith('.json')]
    for p in possibles:
        with open(os.path.join(portfolios_path, p)) as f:
            data = json.load(f)
            obj = Portfolio.from_json(data)
            saved[data['name']] = obj
    return saved

class ExchangeTopPortfolio(Portfolio):
    def __init__(self, name, exchange, stable_target='usdt', reserved_positions=None, initial_cash=0.0, num_top=5, positions=None):
        self._num = num_top
        self._exchange = exchange
        self._stable_target = stable_target
        self._reserved_positions=reserved_positions or []
        super().__init__(name, starting_cash=initial_cash, positions=positions)
        if initial_cash:
            # put it in stable_target
            pass
    def adjust(self):
        adjustable_positions = [p for p in self._positions if p.name not in self._reserved_positions]


                  


