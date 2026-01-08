import talib
import yfinance as yf

stock_data = yf.download('^GSPC')
stock_data = stock_data.tail(500)

stock_data['SMA_20'] = talib.SMA(stock_data['Close'], 20)
stock_data['SMA_60'] = talib.SMA(stock_data['Close'], 60)

stock_data[['Close', 'SMA_20', 'SMA_60']].plot()

#지수 이동평균
stock_data['EMA_60'] = talib.EMA(stock_data['Close'], 60)  # 60일 지수 이동평균
stock_data[['Close', 'SMA_60', 'EMA_60']].plot(figsize=(10, 6))

#RSI
stock_data['RSI_14'] = talib.RSI(stock_data['Close'], 14)
stock_data['RSI_14'].fillna(0, inplace=True)

import matplotlib.pyplot as plt
from matplotlib import gridspec
fig = plt.subplots(figsize=(10, 60), sharex=True)
gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])

# 주가 나타내기
ax1 = plt.subplot(gs[0])
ax1 = stock_data['Close'].plot()
ax1.set_xlabel('')
ax1.axes.xaxis.set_ticks([])

# RSI 나타내기
ax2 = plt.subplot(gs[1])
ax2 = stock_data['RSI_14'].plot(color='black', ylim=[0, 100])
ax2.axhline(y=70, color='r', linestyle='-')
ax2.axhline(y=30, color='r', linestyle='-')
ax2.set_xlabel
plt.subplots_adjust(wspace=0, hspace=0)



#볼린저밴드 계산하기
import pandas as pd

upper_2sd, mid_2sd, lower_2sd = talib.BBANDS(stock_data['Close'],
                                             nbdevup=2,
                                             nbdevdn=2,
                                             timeperiod=20)

bb = pd.concat([upper_2sd, mid_2sd, lower_2sd, stock_data['Close']], axis=1)
bb.columns = ['Upper Band', 'Mid Band', 'Lower Band', 'Close']
bb.plot(figsize=(10, 6),
        color={
            'Upper Band': 'red',
            'Lower Band': 'blue',
            'Mid Band': 'green',
            'Close': 'black'
        })


