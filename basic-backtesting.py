import bt  #Backtesting.py
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root:5787@127.0.0.1:3306/stock_db')
price = pd.read_sql('select * from sample_etf;', con=engine)
price = price.set_index(['Date'])
engine.dispose()

# 전체 자산 동일비중, 매월 말 리밸런싱
strategy = bt.Strategy("Asset_EW", [
    bt.algos.SelectAll(),
    bt.algos.WeighEqually(),
    bt.algos.RunMonthly(),
    bt.algos.Rebalance()
])

data = price.dropna()

# 백테스트 생성
backtest = bt.Backtest(strategy, data)

# 백테스트 실행
result = bt.run(backtest)

result

result.prices
result.prices.to_returns()

import matplotlib.pyplot as plt


result.plot(figsize=(10, 6), legend=False)
plt.show()



wt = result.get_security_weights()
result.get_security_weights().plot.area()
result.display()



#올웨더 포트폴리오 백테스트(정적 자산배분)
import matplotlib
matplotlib.use('Qt5Agg') 


data = price[['SPY', 'TLT', 'IEF', 'GLD', 'DBC']].dropna()

aw = bt.Strategy('All Weather', [
    bt.algos.SelectAll(),
    bt.algos.WeighSpecified(SPY=0.3, TLT=0.4, IEF=0.15, GLD=0.075, DBC=0.075),
    bt.algos.RunQuarterly(),
    bt.algos.Rebalance()
])
aw_backtest = bt.Backtest(aw, data)
aw_result = bt.run(aw_backtest)

aw_result.plot(figsize=(10, 6), title='All Weather', legend=False)
wt = aw_result.get_security_weights()
aw_result.stats




#동적 자산배분
data = price.dropna()

gdaa = bt.Strategy('GDAA', [
    bt.algos.SelectAll(),
    bt.algos.SelectMomentum(n=5, lookback=pd.DateOffset(years=1)),
    bt.algos.WeighERC(lookback=pd.DateOffset(years=1)),
    bt.algos.RunMonthly(),    
    bt.algos.Rebalance()
])

gdaa_backtest = bt.Backtest(gdaa, data)
gdaa_result = bt.run(gdaa_backtest)

gdaa_result.plot()

gdaa_result.get_security_weights().plot.area()

gdaa_backtest.turnover.plot()

gdaa_backtest_net = bt.Backtest(gdaa,
                                data,
                                name='GDAA_net',
                                commissions=lambda q, p: abs(q) * p * 0.003)

gdaa_result = bt.run(gdaa_backtest, gdaa_backtest_net)
gdaa_result.prices
gdaa_result.plot()
stat = gdaa_result.stats










