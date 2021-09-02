import pandas_datareader.data as pdr
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
from pyti.bollinger_bands import upper_bollinger_band as bb_up
from pyti.bollinger_bands import lower_bollinger_band as bb_low

brand_list = ['^GSPC','QQQ','aapl','msft','amzn','tsla','fb','goog','nvda','pypl','intc','cmcsa',
'nflx','adbe','csco','pep','avgo','txn']

def RCI(values, period=9):
    result = [None] * (period - 1)
    for end in range(period-1, len(values)):
        start = end - period + 1
        target = values[start:end+1]
        target_sorted = sorted(target, reverse=True)
        i = 0
        d = 0
        while i < period:
            time_rank = period - i
            price_rank = target_sorted.index(target[i]) + 1
            d = d + ((time_rank - price_rank)*(time_rank - price_rank))
            i += 1
        rci = 6*d / (period * (period*period - 1))
        rci = (1-rci)*100
        result.append(rci)
    return result


def calc_macd(df, es, el, sg):
    macd = pd.DataFrame()
    macd['ema_s'] = df['Close'].ewm(span=es).mean()
    macd['ema_l'] = df['Close'].ewm(span=el).mean()
    macd['macd'] = macd['ema_s'] - macd['ema_l']
    macd['signal'] = macd['macd'].ewm(span=sg).mean()
    macd['diff'] = macd['macd'] - macd['signal']
    def f_plus(x): return x if x > 0 else 0
    def f_minus(x): return x if x < 0 else 0
    macd['diff+'] = macd['diff'].map(f_plus)
    macd['diff-'] = macd['diff'].map(f_minus)
    return macd


end = datetime.date.today()
start = end - datetime.timedelta(days=180)

for brand_list_num in brand_list:
    print(brand_list_num)
    df = pdr.DataReader(brand_list_num, 'yahoo', start, end)
    df = df.drop(['Adj Close'], axis=1)
    
    # calc Bollinger bands
    data = df['Close'].values.tolist()
    period = 20
    df['bb_up'] = bb_up(data, period)
    df['bb_low'] = bb_low(data, period)
    # calc RCI
    close_list = df['Close'].values.tolist()
    rci_short = RCI(close_list)
    df['RCI'] = rci_short
    # calc MACD
    macd = calc_macd(df, 12, 26, 9)
    # print(df)
    # print(macd)

    apd = [
        mpf.make_addplot(df[['bb_up', 'bb_low']]),
        mpf.make_addplot(df[['RCI']], ylabel='RCI', panel='lower'),
        mpf.make_addplot((macd['diff+']), ylabel='MACD',type='bar', color='r', panel=2),
        mpf.make_addplot((macd['diff-']), type='bar', color='b', panel=2),
        ]
    mpf.plot(df, addplot=apd, type='candle', mav=(5, 25), title=brand_list_num,
         datetime_format='%Y/%m/%d', panel_ratios=(1, 1), figratio=(2.0, 1), figscale=2.0,savefig=brand_list_num)
