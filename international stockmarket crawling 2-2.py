from yahooquery import Ticker

data = Ticker('AAPL')
data.asset_profile
data.summary_detail
data.history()

data_y = data.all_financial_data(frequency= 'a')

import numpy as np

data_y.reset_index(inplace = True)
data_y = data_y.loc[:, ~data_y.columns.isin(['periodType', 'currencyCode'])]
data_y = data_y.melt(id_vars = ['symbol', 'asOfDate'])
data_y = data_y.replace([np.nan], None)
data_y['freq'] = 'y'
data_y.columns = ['ticker', 'date', 'account', 'value', 'freq']



data_q = data.all_financial_data(frequency= 'q')
data_q.reset_index(inplace = True)
data_q = data_q.loc[:, ~data_q.columns.isin(['periodType', 'currencyCode'])]
data_q = data_q.melt(id_vars = ['symbol', 'asOfDate'])
data_q = data_q.replace([np.nan], None)
data_q['freq'] = 'q'
data_q.columns = ['ticker', 'date', 'account', 'value', 'freq']


#frequency= 부분에서 a이면 년간, q이면 분기임



# 패키지 불러오기
from sqlalchemy import create_engine
import pymysql
import pandas as pd
from yahooquery import Ticker
import time
from tqdm import tqdm
import numpy as np

# DB 연결
engine = create_engine('mysql+pymysql://user:password@127.0.0.1:3306/stock_db')
con = pymysql.connect(user='root',
                      passwd='5787',
                      host='127.0.0.1',
                      db='stock_db',
                      charset='utf8')

mycursor = con.cursor()

# 티커리스트 불러오기
ticker_list = pd.read_sql("""
select * from global_ticker
where date = (select max(date) from global_ticker)
and country = 'United States';
""", con=engine)

# DB 저장 쿼리
query_fs = """
    insert into global_fs (ticker, date, account, value, freq)
    values (%s,%s,%s,%s,%s) as new
    on duplicate key update
    value = new.value;
"""

# 오류 발생시 저장할 리스트 생성
error_list = []

# 전종목 주가 다운로드 및 저장
for i in tqdm(range(0, len(ticker_list))):

    # 티커 선택
    ticker = ticker_list['Symbol'][i]

    # 오류 발생 시 이를 무시하고 다음 루프로 진행
    try:
        
        # 정보 다운로드
        data = Ticker(ticker)

        # 연간 재무제표
        data_y = data.all_financial_data(frequency = 'a')
        data_y.reset_index(inplace = True)
        data_y = data_y.loc[:, ~data_y.columns.isin(['periodType', 'currencyCode'])]
        data_y = data_y.melt(id_vars = ['symbol', 'asOfDate'])
        data_y = data_y.replace([np.nan], None)
        data_y['freq'] = 'y'
        data_y.columns = ['ticker', 'date', 'account', 'value', 'freq']

        # 분기 재무제표
        data_q = data.all_financial_data(frequency= 'q')
        data_q.reset_index(inplace = True)
        data_q = data_q.loc[:, ~data_q.columns.isin(['periodType', 'currencyCode'])]
        data_q = data_q.melt(id_vars = ['symbol', 'asOfDate'])
        data_q = data_q.replace([np.nan], None)
        data_q['freq'] = 'q'
        data_q.columns = ['ticker', 'date', 'account', 'value', 'freq']
        
        
        # 데이터 합치기
        data_fs = pd.concat([data_y, data_q], axis=0)
        
        # 재무제표 데이터를 DB에 저장
        args = data_fs.values.tolist()
        mycursor.executemany(query_fs, args)
        con.commit()

    except:

        # 오류 발생시 error_list에 티커 저장하고 넘어가기
        print(ticker)
        error_list.append(ticker)

    # 타임슬립 적용
    time.sleep(2)

# DB 연결 종료
engine.dispose()
con.close()



























