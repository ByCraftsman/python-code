import pandas as pd
import yfinance as yf
import pymysql
from sqlalchemy import create_engine

tickers = [
    'SPY',  # 미국 주식
    'IEV',  # 유럽 주식 
    'EWJ',  # 일본 주식
    'EEM',  # 이머징 주식
    'TLT',  # 미국 장기채
    'IEF',  # 미국 중기채
    'IYR',  # 미국 리츠
    'RWX',  # 글로벌 리츠
    'GLD',  # 금
    'DBC'  # 상품
]

all_data = {}
for ticker in tickers:
    all_data[ticker] = yf.download(ticker, start='1993-01-22')

prices = pd.DataFrame(
    {tic: data['Adj Close']
     for tic, data in all_data.items()})

prices = prices.fillna(method = 'ffill')

engine = create_engine('mysql+pymysql://root:5787@127.0.0.1:3306/stock_db')
prices.to_sql(name='sample_etf', con=engine, index=True, if_exists='replace')
engine.dispose()

rets = prices.pct_change(1).dropna()

import matplotlib.pyplot as plt
import seaborn as sns

sns.heatmap(rets.corr().round(2), annot = True, annot_kws = {"size" : 16}, cmap = 'coolwarm')


import riskfolio as rp

# 포트폴리오 객체 생성
port = rp.Portfolio(returns=rets)

# 입력값 계산
method_mu = 'hist'  # 역사적 데이터를 바탕으로 기대 수익률 추정
method_cov = 'hist'  # 역사적 데이터를 바탕으로 분산-공분산 행렬 추정

# 객체에 수익률 및 분산-공분산 입력
port.assets_stats(method_mu=method_mu, method_cov=method_cov)

model = 'Classic'  # 모델 입력. Classic(역사적 데이터), BL(블랙-리터만), FM(팩터 모형)
rm = 'MV'  # 위험 측정 방법. MV는 표준편차를 의미
obj = 'Sharpe'  # 목적함수. MinRisk(최소분산), MaxRet(최대수익률), Utility(효용) or Sharpe(샤프지수)
hist = True  # 역사적 데이터 사용
rf = 0  # 무위험 수익률
l = 0  # 위험 회피 계수, obj가 'Utility' 일 때만 사용

# 최적화
w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)

round(w, 4)



points = 50  # 효율적 투자선을 구성하는 샘플 갯수
frontier = port.efficient_frontier(model=model,
                                   rm=rm,
                                   points=points,
                                   rf=rf,
                                   hist=hist)


label = 'Max Risk Adjusted Return Portfolio' 
mu = port.mu  # 기대 수익률
cov = port.cov  # 분산-공분산 행렬
returns = port.returns  # 자산 별 수익률

ax = rp.plot_frontier(w_frontier=frontier,
                      mu=mu,
                      cov=cov,
                      returns=returns,
                      rm=rm,
                      rf=rf,
                      alpha=0.05,
                      cmap='viridis',
                      w=w,
                      label=label,
                      marker='*',
                      s=16,
                      c='r',
                      height=6,
                      width=10,
                      ax=None)





import riskfolio as rp

port = rp.Portfolio(returns=rets)
method_mu = 'hist'
method_cov = 'hist'
port.assets_stats(method_mu=method_mu, method_cov=method_cov)

model = 'Classic'
rm = 'MV'
obj = 'MinRisk'  # 목적함수. MinRisk(최소분산), MaxRet(최대수익률), Utility(효용) or Sharpe(샤프지수)
hist = True
rf = 0
l = 0

w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)

round(w.T, 4)

ax = rp.plot_bar(w=w, title='Portfolio',  kind='h', ax=None)


#제약조건
asset_classes = {
    'Asset':
    ['SPY', 'IEV', 'EWJ', 'EEM', 'TLT', 'IEF', 'IYR', 'RWX', 'GLD', 'DBC'],
    'Class': [
        'stock', 'stock', 'stock', 'stock', 'bond', 'bond', 'alternative',
        'alternative', 'alternative', 'alternative'
    ]
}

asset_classes = pd.DataFrame(asset_classes)

constraints = {'Disabled': [False, False],
               'Type': ['All Assets', 'All Assets'],
               'Set': ['', ''],
               'Position': ['', ''],
               'Sign': ['>=', '<='],
               'Weight': [0.05, 0.2],
               'Type Relative': ['', ''],
               'Relative Set': ['', ''],
               'Relative': ['', ''],
               'Factor': ['', '']}

constraints = pd.DataFrame(constraints)


A, B = rp.assets_constraints(constraints, asset_classes)

port.ainequality = A
port.binequality = B

w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)

w.T

rp.plot_bar(w)
ax = rp.plot_bar(w=w, title='Portfolio',  kind='h', ax=None)




constraints = {
    'Disabled': [
        False, False, False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False
    ],
    'Type': [
        'Assets', 'Assets', 'Assets', 'Assets', 'Assets', 'Assets', 'Assets',
        'Assets', 'Assets', 'Assets', 'Assets', 'Assets', 'Assets', 'Assets',
        'Assets', 'Assets', 'Assets', 'Assets', 'Assets', 'Assets'
    ],
    'Set': [
        'Asset', 'Asset', 'Asset', 'Asset', 'Asset', 'Asset', 'Asset', 'Asset',
        'Asset', 'Asset', 'Asset', 'Asset', 'Asset', 'Asset', 'Asset', 'Asset',
        'Asset', 'Asset', 'Asset', 'Asset'
    ],
    'Position': [
        'SPY', 'IEV', 'EWJ', 'EEM', 'TLT', 'IEF', 'IYR', 'RWX', 'GLD', 'DBC',
        'SPY', 'IEV', 'EWJ', 'EEM', 'TLT', 'IEF', 'IYR', 'RWX', 'GLD', 'DBC'
    ],
    'Sign': [
        '>=', '>=', '>=', '>=', '>=', '>=', '>=', '>=', '>=', '>=', '<=', '<=',
        '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<='
    ],
    'Weight': [
        0.10, 0.10, 0.05, 0.05, 0.10, 0.10, 0.05, 0.05, 0.03, 0.03, 0.25, 0.25,
        0.20, 0.20, 0.20, 0.20, 0.10, 0.10, 0.08, 0.08
    ],
    'Type Relative': [
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
        '', ''
    ],
    'Relative Set': [
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
        '', ''
    ],
    'Relative': [
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
        '', ''
    ],
    'Factor': [
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
        '', ''
    ]
}

constraints = pd.DataFrame(constraints)


A, B = rp.assets_constraints(constraints, asset_classes)

port.ainequality = A
port.binequality = B

w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)

round(w, 4)


constraints = {
    'Disabled': [False, False, False, False, False, False, False, False],
    'Type': [
        'All Assets', 'All Assets', 'Classes', 'Classes', 'Classes', 'Classes',
        'Classes', 'Classes'
    ],
    'Set': ['', '', 'Class', 'Class', 'Class', 'Class', 'Class', 'Class'],
    'Position':
    ['', '', 'stock', 'bond', 'alternative', 'stock', 'bond', 'alternative'],
    'Sign': ['>=', '<=', '>=', '>=', '>=', '<=', '<=', '<='],
    'Weight': [0.03, 0.20, 0.40, 0.30, 0.10, 0.70, 0.50, 0.20],
    'Type Relative': ['', '', '', '', '', '', '', ''],
    'Relative Set': ['', '', '', '', '', '', '', ''],
    'Relative': ['', '', '', '', '', '', '', ''],
    'Factor': ['', '', '', '', '', '', '', '']
}

constraints = pd.DataFrame(constraints)

A, B = rp.assets_constraints(constraints, asset_classes)

port.ainequality = A
port.binequality = B

w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)

round(w, 4)



import riskfolio as rp

port = rp.Portfolio(returns=rets)
method_mu = 'hist'
method_cov = 'hist'
port.assets_stats(method_mu=method_mu, method_cov=method_cov)

model = 'Classic'
rm = 'MV'
hist = True
rf = 0
b = None  # 위험기여도 제약조건

w_rp = port.rp_optimization(model=model, rm=rm, rf=rf, b=b, hist=hist)

round(w_rp, 4)


ax = rp.plot_risk_con(w_rp,
                      cov=port.cov,
                      returns=port.returns,
                      rm=rm,
                      rf=0,
                      alpha=0.01,
                      color="tab:blue",
                      height=6,
                      width=10,
                      ax=None)


# 위험예산 포트폴리오
b = [0.15, 0.15, 0.15, 0.15, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05]
w_rp = port.rp_optimization(model=model, rm=rm, rf=rf, b=b, hist=hist)

round(w_rp, 4)


ax = rp.plot_risk_con(w_rp,
                      cov=port.cov,
                      returns=port.returns,
                      rm=rm,
                      rf=0,
                      alpha=0.01,
                      color="tab:blue",
                      height=6,
                      width=10,
                      ax=None)




















