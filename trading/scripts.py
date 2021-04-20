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