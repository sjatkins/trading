from trading import coingecko as cg
from trading import portfolio
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

def cash_accumulation(base, rate, add=0, take_up_to=0, minus_basis=0, percent_aside=0, times=12):
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
    time_period = 365 * 3
    count = int(time_period / unit_days )
    for i in range(count):
        earned = base * unit_rate
        taking = 0
        if take_up_to:
            taking = take_up_to if (earned > 2 * take_up_to) else earned/2
        elif percent_aside:
            taking = earned * percent_aside/100.0
        
        base += earned + add - taking
        table.add_row([i+1, '{:14,.2f}'.format(earned), '{:14,.2f}'.format(base), '{:14,.2f}'.format(taking)])

    print(table)
