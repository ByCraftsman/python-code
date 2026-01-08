

"""
Adjusted prices are essential for backtesting to ensure continuity.
Raw prices can cause significant distortions in returns during corporate events 
like stock splits or mergers, leading to inaccurate performance analysis.

퀀트 투자나 벡테스트에서는 수정주가가 필요하다. 일반적인 주가는 액면분할이나 액면병합
 등의 사건이 있을 시, 수익률에 엄청난 왜곡이 생길 수 있기 때문이다."""


# Naver Finance is used because its charts are based on adjusted prices.
#네이버 증권의 차트는 수정주가를 기준으로 되어 있기 때문에, 네이버 증권을 사용하였다.
#GET 방식이라서 URL를 조작하여서 쉽게 원하는 시계열만큼의 데이터를 얻을 수 있었다.

from sqlalchemy import create_engine
import pandas as pd
engine = create_engine('mysql+pymysql://root:5787@127.0.0.1:3306/stock_db')
#최신 기준일에 해당하는 데이터만 불러올 것이기 때문에, select from에서
#서브 쿼리에 select max를 해서 where 구문에 넣어주었다. 그중에서 보통주만 가져옴.
query = """
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker) 
	and 종목구분 = '보통주';
"""
ticker_list = pd.read_sql(query, con=engine)
engine.dispose()

ticker_list.head()


from dateutil.relativedelta import relativedelta
import requests as rq
from io import BytesIO
from datetime import date

i = 0
ticker = ticker_list['종목코드'][i]
fr = (date.today() + relativedelta(years=-5)).strftime("%Y%m%d") #strftime으로 문자열 형태로 변경
to = (date.today()).strftime("%Y%m%d")

url = f'''https://fchart.stock.naver.com/siseJson.nhn?symbol={ticker}&requestType=1
&startTime={fr}&endTime={to}&timeframe=day'''

data = rq.get(url).content
data_price = pd.read_csv(BytesIO(data))

data_price.head()

import re

price = data_price.iloc[:, 0:6]
price.columns = ['날짜', '시가', '고가', '저가', '종가', '거래량']
price = price.dropna()
price['날짜'] = price['날짜'].str.extract('(\d+)')
price['날짜'] = pd.to_datetime(price['날짜'])
price['종목코드'] = ticker

price.head()




# 패키지 불러오기
import pymysql
from sqlalchemy import create_engine
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import requests as rq
import time
from tqdm import tqdm
from io import BytesIO

# DB 연결
engine = create_engine('mysql+pymysql://root:5787@127.0.0.1:3306/stock_db')
con = pymysql.connect(user='root',
                      passwd='5787',
                      host='127.0.0.1',
                      db='stock_db',
                      charset='utf8')
mycursor = con.cursor()

# 티커리스트 불러오기
ticker_list = pd.read_sql("""
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker) 
	and 종목구분 = '보통주';
""", con=engine)

# DB 저장 쿼리
query = """
    insert into kor_price (날짜, 시가, 고가, 저가, 종가, 거래량, 종목코드)
    values (%s,%s,%s,%s,%s,%s,%s) as new
    on duplicate key update
    시가 = new.시가, 고가 = new.고가, 저가 = new.저가,
    종가 = new.종가, 거래량 = new.거래량;
"""

# 오류 발생시 저장할 리스트 생성
error_list = []

# 전종목 주가 다운로드 및 저장
for i in tqdm(range(0, len(ticker_list))):

    # 티커 선택
    ticker = ticker_list['종목코드'][i]

    # 시작일과 종료일
    fr = (date.today() + relativedelta(years=-5)).strftime("%Y%m%d")
    to = (date.today()).strftime("%Y%m%d")

    # 오류 발생 시 이를 무시하고 다음 루프로 진행
    try:

        # url 생성
        url = f'''https://fchart.stock.naver.com/siseJson.nhn?symbol={ticker}&requestType=1
        &startTime={fr}&endTime={to}&timeframe=day'''

        # 데이터 다운로드
        data = rq.get(url).content
        data_price = pd.read_csv(BytesIO(data))

        # 데이터 클렌징
        price = data_price.iloc[:, 0:6]
        price.columns = ['날짜', '시가', '고가', '저가', '종가', '거래량']
        price = price.dropna()
        price['날짜'] = price['날짜'].str.extract('(\d+)')
        price['날짜'] = pd.to_datetime(price['날짜'])
        price['종목코드'] = ticker

        # 주가 데이터를 DB에 저장
        args = price.values.tolist()
        mycursor.executemany(query, args)
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









