from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://user:password@127.0.0.1:3306/stock_db')
price = pd.read_sql('select * from sample_etf;', con=engine)
price = price.set_index(['Date'])
engine.dispose()


import talib

data = price[['SPY']].dropna()
sma = data.apply(lambda x: talib.SMA(x, 200))

data > sma


import bt

bt_sma = bt.Strategy('Timing', [
    bt.algos.SelectWhere(data > sma),
    bt.algos.WeighEqually(),
    bt.algos.Rebalance()
])

bt_sma_backtest = bt.Backtest(bt_sma, data)

#매수 후 보유
def buy_and_hold(data, name):

    # 벤치마크 전략 생성
    bt_strategy = bt.Strategy(name, [        
        bt.algos.SelectAll(),
        bt.algos.WeighEqually(),
        bt.algos.RunOnce(),
        bt.algos.Rebalance()
    ])
    # Return the backtest
    return bt.Backtest(bt_strategy, data)


# 벤치마크 전략 백테스트
stock = buy_and_hold(data[['SPY']], name='stock')

# 두개 백테스트 동시에 실행
bt_sma_result = bt.run(bt_sma_backtest, stock)

import matplotlib
matplotlib.use('Qt5Agg') # 혹은 'Qt4Agg', 'TkAgg', 'WxAgg' 등

bt_sma_result.prices.iloc[201:, ].rebase().plot()

#낙폭 계산
bt_sma_result.prices.iloc[201:, ].rebase().to_drawdown_series().plot()


stat = bt_sma_result.stats




#파라미터 최적화
def timing(price, n):

    sma = price.apply(lambda x: talib.SMA(x, n))
    stragety = bt.Strategy(n, [
        bt.algos.SelectWhere(price > sma),        
        bt.algos.WeighEqually(),
        bt.algos.Rebalance()
    ])

    backtest = bt.Backtest(stragety, price)

    return (backtest)

n_20 = timing(data, 20)
n_60 = timing(data, 60)
n_100 = timing(data, 100)
n_150 = timing(data, 150)
n_200 = timing(data, 200)
n_250 = timing(data, 250)

result = bt.run(n_20, n_60, n_100, n_150, n_200, n_250)

result.prices[250:].rebase().plot()


#롱숏 전략
data = price[['SPY']]
SMA_200 = data.apply(lambda x: talib.SMA(x, 200))
SMA_60 = data.apply(lambda x: talib.SMA(x, 60))

signal = SMA_200.copy()
signal[SMA_60 >= SMA_200] = 1
signal[SMA_60 < SMA_200] = -1
signal[signal.isnull()] = 0

bind = pd.concat([data, SMA_200, SMA_60, signal], axis=1)
bind.columns = ['SPY', 'SMA 200', 'SMA 60', 'signal']
bind.loc['2018':].plot(figsize=(10, 6), secondary_y=['signal'])


strategy = bt.Strategy(
    'SMA_crossover',
    [bt.algos.SelectAll(),
     bt.algos.WeighTarget(signal),
     bt.algos.Rebalance()])

backtest = bt.Backtest(strategy, data)
result = bt.run(backtest)

result.plot()
result.display_monthly_returns()


pd.concat([bind, result.prices],
          axis=1).loc['2020'].plot(figsize=(10, 6),
                                            secondary_y=['signal'],
                                            alpha=0.8)

                                   
                                   
                                   
#평균회귀전략                                   
data = price[['SPY']]
spy_rsi = data.apply(lambda x: talib.RSI(x, 14))

signal = spy_rsi.copy()
signal[spy_rsi > 70] = -1
signal[spy_rsi < 30] = 1
signal[(spy_rsi <= 70) & (spy_rsi >= 30)] = 0
signal[signal.isnull()] = 0
                                   
                     
strategy = bt.Strategy('RSI_MeanReversion',
                       [bt.algos.WeighTarget(signal),
                        bt.algos.Rebalance()])
backtest = bt.Backtest(strategy, data)
result = bt.run(backtest)

result.plot()
result.stats



upper_2sd, mid_2sd, lower_2sd = talib.BBANDS(data['SPY'],
                                             nbdevup=2,
                                             nbdevdn=2,
                                             timeperiod=20)

bb = pd.concat([upper_2sd, mid_2sd, lower_2sd, data['SPY']], axis=1)
bb.columns = ['Upper Band', 'Mid Band', 'Lower Band', 'SPY']

import numpy as np

signal = data.copy()
signal['SPY'] = np.nan

signal[bb['SPY'] > bb['Upper Band']] = -1
signal[bb['SPY'] < bb['Lower Band']] = 1
signal[signal.isnull()] = 0

strategy = bt.Strategy('BB',
                       [bt.algos.WeighTarget(signal),
                        bt.algos.Rebalance()])

backtest = bt.Backtest(strategy, data)
result = bt.run(backtest)

result.plot()













