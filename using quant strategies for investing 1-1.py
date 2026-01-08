import yfinance as yf
import pandas as pd

tickers = ['^KS11', '039490.KS']

all_data = {}
for ticker in tickers:
    all_data[ticker] = yf.download(ticker,
                                   start="2016-01-01",
                                   end='2021-12-31')

prices = pd.DataFrame({tic: data['Close'] for tic, data in all_data.items()})
ret = prices.pct_change().dropna()


import statsmodels.api as sm

ret['intercept'] = 1
reg = sm.OLS(ret[['039490.KS']], ret[['^KS11', 'intercept']]).fit()




import pandas_datareader.data as web
from pandas_datareader.famafrench import get_available_datasets

datasets = get_available_datasets()
datasets[1:20]


df_pbr = web.DataReader('Portfolios_Formed_on_BE-ME',
                        'famafrench',
                        start = '1900-01-01')

import matplotlib.pyplot as plt

plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

df_pbr_vw = df_pbr[0].loc[:, ['Lo 20', 'Qnt 2', 'Qnt 3', 'Qnt 4', 'Hi 20']]
df_pbr_cum = (1 + df_pbr_vw / 100).cumprod()

df_pbr_cum.plot(figsize=(10, 6),
                legend = 'reverse',
                title='PBR별 포트폴리오의 누적 수익률')

import numpy as np

df_pbr_cum = np.log(1+df_pbr_vw/100).cumsum()
df_pbr_cum.plot(figsize=(10, 6),
                legend='reverse',
                title='PBR별 포트폴리오의 누적 수익률')







































