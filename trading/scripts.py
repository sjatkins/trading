from trading import coingecko as cg
from trading import portfolio
import math

gecko = cg.gecko
get_exchange = cg.Exchange.for_
get_coin = cg.CoinGeckoInfo.for_coin
from prettytable import PrettyTable
def get_kucoin_top(num=10):
    coins = get_exchange('kucoin').sorted_period('24h')[:num]
    print('\n   Top %d Kucoin 24h Price Increase' % num)
    table = PrettyTable()
    table.field_names = ['Symbol', 'Percent', 'USD price', 'ETH price']
    table.align['Symbol'] = 'l'
    table.align['Percent'] = 'r'
    table.align['USD price'] = 'r'
    table.align['ETH price'] = 'r'

    for symbol, percent in coins:
        coin = get_coin(symbol)
        raw_price = coin.raw_current_price()
        usd, eth = raw_price.get('usd'), raw_price.get('eth')
        table.add_row([symbol.upper(), '%3.2f' % percent, '%5.5f' % usd, '%3.10f' % eth])

    print(table)

def cash_accumulation(base, rate, add=0, take_up_to=0, minus_basis=0, percent_aside=0, times=12, how_often=12, years=3, add_frequency=1):
    def to_add(counter):
        if add:
            if add_frequency > 1:
                return 0 if (counter + 1) % add_frequency else add
        return add
        
    data = []
    table = PrettyTable()
    table.field_names = ['Index', 'Earned', 'Base Price', 'Taking']
    table.align['Index'] = 'r'
    table.align['Earned'] = 'r'
    table.align['Base Price'] = 'r'
    table.align['Takisc'] = 'r'

    per_day = rate/100/365
    unit_rate = per_day * 365/times
    unit_days = 365/times
    take_days = 365/how_often
    
    time_period = 365 * years
    count = int(time_period / unit_days )
    next_month = 1
    cumulative_earn = 0
    cumulative_days = 0
    take_until = 0
    taking_rate = percent_aside/100
    taking_left = 0
    for i in range(count):
        cumulative_days += unit_days
        earned = base * unit_rate
        cumulative_earn += earned
        taking = 0
        if taking_rate:
            if cumulative_days  >= take_days:
                taking = cumulative_earn * taking_rate
                cumulative_earn = 0
                cumulative_days = 0
        elif take_up_to:
            if cumulative_days >= take_days:
                taking = min(take_up_to, earned)
                cumulative_earn = 0
                cumulative_days = 0
                if taking < take_up_to:
                    take_until = i + math.ceil(take_up_to/taking) - 1
                    taking_left = take_up_to - taking
        
            elif i and i <= take_until:
                taking = min(earned, taking_left)
                taking_left -= taking
        
        base += earned + to_add(i) - taking
        table.add_row([i+1, '{:14,.2f}'.format(earned), '{:14,.2f}'.format(base), '{:14,.2f}'.format(taking)])

    print(table)

def per_day(apy):
    x = math.log(apy)/365.0
    return exp(x)