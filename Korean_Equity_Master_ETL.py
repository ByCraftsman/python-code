"""
Adjusted prices are essential for backtesting to ensure continuity.
Raw prices can cause significant distortions in returns during corporate events 
like stock splits or mergers, leading to inaccurate performance analysis.

퀀트 투자나 벡테스트에서는 수정주가가 필요하다. 일반적인 주가는 액면분할이나 액면병합
 등의 사건이 있을 시, 수익률에 엄청난 왜곡이 생길 수 있기 때문이다.


Naver Finance is used because its charts are based on adjusted prices.

네이버 증권의 차트는 수정주가를 기준으로 되어 있기 때문에, 네이버 증권을 사용하였다.
GET 방식이라서 URL를 조작하여서 쉽게 원하는 시계열만큼의 데이터를 얻을 수 있었다.
"""



#전종목의 티커별 시계열 정보를 크롤링하여 MYSQL에 적제하도록 함.
from sqlalchemy import create_engine
import pandas as pd
"""
kor_ticker는 'Building an ETL Data Pipeline for Korean Listed Stocks'코드에서 정제한 테이블이다.

최신 기준일에 해당하는 데이터만 불러올 것이기 때문에, 서브 쿼리에 select max로
가장 최근일 데이터를 불러주었다. and 조건으로 그중에서 보통주만 가져옴.

우선주는 거래량이 적고 의결권이 없어 분석 모델에서 제외하는 것이 일반적임.
"""

engine = create_engine('mysql+pymysql://ID:PASSWORD@127.0.0.1:3306/stock_db')
query = """
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker) 
	and 종목구분 = '보통주';
"""
ticker_list = pd.read_sql(query, con=engine)
engine.dispose()




# 단일 종목의 주가 시계열 데이터를 불러와서 정제.
from dateutil.relativedelta import relativedelta #달력 기준으로 정확한 시계열이 필요할 때 사용함.
from datetime import date # relativedelta는 date/datetime 객체에 더해지므로 기준 date 객체 생성을 위해 필요.
import requests as rq
from io import BytesIO #URL로 받은 bytes 데이터를 CSV 파일처럼 Pandas에서 읽기 위해 사용함.

#이런식으로 불러온 SQL 데이터를 사용하면 time alignment issue가 발생할 수 있으나,
#이 코드의 주안점은 데이터 정제이므로 고려하지 아니함.
i = 0  # 예시 분석용으로 첫 번째 종목만 선택함.
ticker = ticker_list['종목코드'][i] 

fr = (date.today() + relativedelta(years=-5)).strftime("%Y%m%d") #strftime -> 문자열 형태로 변환
to = (date.today()).strftime("%Y%m%d")

# 일봉 차트눌러서 개발자도구로 해당하는 URL을 입력.
url = f'''https://m.stock.naver.com/front-api/external/chart/domestic/info?symbol={ticker}&requestType=1
&startTime={fr}&endTime={to}&timeframe=day'''

data = rq.get(url).content
data_price = pd.read_csv(BytesIO(data))
data_price.head()


# 데이터 클렌징
price = data_price.iloc[:, 0:6] #: -> 모든행, 0:6 -> 0~5열까지 (iloc은 마지막 부분 미포함.).
price.columns = ['날짜', '시가', '고가', '저가', '종가', '거래량']
price = price.dropna()
price['날짜'] = price['날짜'].str.extract('(\d+)') #정규식으로 숫자만 추출 (때문에 Dtype이 object로 변경됨.).
price['날짜'] = pd.to_datetime(price['날짜']) #시계열 연산 및 정렬이 가능한 datetime 타입으로 변환.
price['종목코드'] = ticker




# 전 코드를 기반으로 하여, 모든 종목의 주가 데이터를 MySQL에 적재하도록 한다.
"""
why pymysql?

위쪽 코드에서는 데이터 조회(SELECT)만 수행하므로, SQLAlchemy 엔진만 있으면
 내부적으로 DB-API 드라이버(pymysql)가 자동 처리된다. 

반면, 여기서는 대량의 주가 데이터를 UPSERT 방식으로 저장해야 하며,
executemany, commit, 트랜잭션 제어가 필요하다. 따라서 저수준 DB 제어가 가능한
 pymysql을 직접 사용하여 cursor 기반으로 데이터를 적재한다.

why tqdm?

tqdm을 사용해 진행률과 예상 소요 시간을 실시간으로 확인할 수 있음.
#즉, tqdm은 장시간 작업에서 "가시성(observability)”을 확보하기 위한 도구임.
"""
import pymysql
import time
from tqdm import tqdm

# DB 연결
engine = create_engine('mysql+pymysql://ID:PASSWORD@127.0.0.1:3306/stock_db')
con = pymysql.connect(user='',
                      passwd='',
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

# 크롤링한 주가를 DB에 저장하기 위해서 미리 쿼리 작성. upsert 방식임
query = """
    insert into kor_price (날짜, 시가, 고가, 저가, 종가, 거래량, 종목코드)
    values (%s,%s,%s,%s,%s,%s,%s) as new
    on duplicate key update
    시가 = new.시가, 고가 = new.고가, 저가 = new.저가,
    종가 = new.종가, 거래량 = new.거래량;
"""

# 오류 발생시 저장할 리스트 생성
error_list = []


# 전종목 주가를 DB에 저장하기. (단일 코드에서 for loop문으로 바꾼 것 뿐임.)
for i in tqdm(range(0, len(ticker_list))): 
    # range(start, end)는 end를 포함하지 않으므로 ticker_list의 인덱스와 정확히 대응됨.

    # 티커 선택
    ticker = ticker_list['종목코드'][i]

    # 시작일과 종료일
    fr = (date.today() + relativedelta(years=-5)).strftime("%Y%m%d")
    to = (date.today()).strftime("%Y%m%d")

    #위쪽 코드는 어차피 오류가 날 일이 없는 부분이라, 여기부터 try하면됨.
    try:

        # url 생성
        url = f'''https://m.stock.naver.com/front-api/external/chart/domestic/info?symbol={ticker}&requestType=1
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
    time.sleep(1)

# DB 연결 종료
engine.dispose()
con.close()




#----------------------------------------------------------------------------------------------------------------




#여기서 부터는 전종목 제무제표 정보를 크롤링하여서 SQL에 적제하도록 한다.
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://ID:PASSWORD@127.0.0.1:3306/stock_db')
query = """
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker) 
	and 종목구분 = '보통주';
"""
ticker_list = pd.read_sql(query, con=engine)
engine.dispose()

i = 0
ticker = ticker_list['종목코드'][i]

"""
네이버 증권으로도 재무제표 정보를 받을 수는 있으나, 동적 페이지로 구성되어 있어서 셀레니움 (크롤링이 오래 걸림) 이 필요하다.
그렇기 때문에 fnguide 사이트를 이용하여 재무제표 정보를 가져온다.

네이버 증권은 재무제표 구조가 자주 바뀌는 반면, FN Guide는 항목과 시계열 구조가 안정적이라 
자동화 파이프라인 구축에 유리하다. 네이버를 사용하면 유지보수할 때 번거로울 수 밖에 없다.
"""

url = f'http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{ticker}'

#displayed_only는 기본적으로 True이기 때문에 false 설정을 안하면 + 항목에 안에 들어있는 상세내역을 가져오지 않는다.
data = pd.read_html(url, displayed_only=False)




"""
테이블 정제 전에 다시 정리하자면,
loc은 라벨 기반 인덱싱이라 컬럼명이나 인덱스명을 사용하고,
iloc은 정수 위치 기반 인덱싱이라 컬럼이나 행의 순서를 사용함.
그렇기 때문에 loc이 코드 가독성과 유지보수 측면에서 유리함.
"""

#연간 재무제표 중, 포괄손익계산서에 필요없는 열이 존재하므로 제거하도록 함.
print(data[0].columns.tolist(), 
      data[2].columns.tolist(),
      data[4].columns.tolist()
     )

#~의 의미는 not의 의미를 가짐. 이러한 로직을 이용하여 제거할 수 있음
data[0].iloc[:, ~data[0].columns.str.contains('전년동기')]

#데이터 프레임을 concat 해주도록 함.
data_fs_y = pd.concat(
    [data[0].iloc[:, ~data[0].columns.str.contains('전년동기')], 
     data[2], 
     data[4]]
    )

#열 이름 변경
data_fs_y = data_fs_y.rename(columns={data_fs_y.columns[0]: "계정"})




#연간 재무제표에서 연말에는 연 데이터 대신 분기 데이터가 들어가므로, 제거해줘야 함.
import requests as rq
from bs4 import BeautifulSoup
import re

#html를 불러옴
page_data = rq.get(url)

#BeatifulSoup 객체로 변환함
page_data_html = BeautifulSoup(page_data.content, 'html.parser')

fiscal_data = page_data_html.select('div.corp_group1 > h2')

fiscal_data_text = fiscal_data[1].text

#숫자만 추출
fiscal_data_text = re.findall('[0-9]+', fiscal_data_text)

#모든 행, 열이름이 '계정' | (or의 의미) 뒷자리 2개가 결산월과 일치하는 부분 선택.
data_fs_y = data_fs_y.loc[:, (data_fs_y.columns == '계정') |
                          (data_fs_y.columns.str[-2:].isin(fiscal_data_text))]



#분기 데이터
data_fs_q = pd.concat(
    [data[1].iloc[:, ~data[1].columns.str.contains('전년동기')],
     data[3],
     data[5]]
    )

data_fs_q = data_fs_q.rename(columns={data_fs_q.columns[0]: "계정"})



def clean_fs(df, ticker, frequency):

    #'계정' 컬럼을 제외한 나머지 모든 컬럼이 NaN인 행을 제거하는 전처리 코드임.
    df = df[~df.loc[:, ~df.columns.isin(['계정'])].isna().all(axis=1)]
    #중복되는 계정 명을 제거하는데, 중복되는 것 중 첫번째 값은 남김.
    df = df.drop_duplicates(['계정'], keep='first')
    #멜트를 이용하여 긴행 형태로 만듦.
    df = pd.melt(df, id_vars='계정', var_name='기준일', value_name='값')
    #nan값 제거
    df = df[~pd.isnull(df['값'])]
    #필요없는 문자열 제거
    df['계정'] = df['계정'].replace({'계산에 참여한 계정 펼치기': ''}, regex=True)
    #데이트타임 형태로 바꾸면서 핸들링하기 편한 월말 형태로 변환
    df['기준일'] = pd.to_datetime(df['기준일'],
                               format='%Y/%m') + pd.tseries.offsets.MonthEnd()
    df['종목코드'] = ticker
    df['공시구분'] = frequency

    return df



#함수 실행
data_fs_y_clean = clean_fs(data_fs_y, ticker, 'y')
data_fs_q_clean = clean_fs(data_fs_q, ticker, 'q')

#연 데이터 + 분기 데이터 concat
data_fs_bind = pd.concat([data_fs_y_clean, data_fs_q_clean])




#MY SQL에 데이터 적제하기
import pymysql
from tqdm import tqdm
import time

# DB 연결
engine = create_engine('mysql+pymysql://ID:PASSWORD@127.0.0.1:3306/stock_db')
con = pymysql.connect(user='',
                      passwd='',
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
    insert into kor_fs (계정, 기준일, 값, 종목코드, 공시구분)
    values (%s,%s,%s,%s,%s) as new
    on duplicate key update
    값=new.값
"""

# 오류 발생시 저장할 리스트 생성
error_list = []

# for loop문으로 모든 종목을 SQL에 적제.
for i in tqdm(range(0, len(ticker_list))):

    ticker = ticker_list['종목코드'][i]

    try:
        url = f'http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{ticker}'

        # 데이터 받아오기
        data = pd.read_html(url, displayed_only=False)

        # 연간 데이터
        data_fs_y = pd.concat([
            data[0].iloc[:, ~data[0].columns.str.contains('전년동기')],
            data[2],
            data[4]
        ])
        
        data_fs_y = data_fs_y.rename(columns={data_fs_y.columns[0]: "계정"})
        
        # 결산년 찾기
        page_data = rq.get(url)
        page_data_html = BeautifulSoup(page_data.content, 'html.parser')
        fiscal_data = page_data_html.select('div.corp_group1 > h2')
        fiscal_data_text = fiscal_data[1].text
        fiscal_data_text = re.findall('[0-9]+', fiscal_data_text)

        # 결산년에 해당하는 계정만 남기기
        data_fs_y = data_fs_y.loc[:, (data_fs_y.columns == '계정') | (
            data_fs_y.columns.str[-2:].isin(fiscal_data_text))]

        #사전에 만든 함수 실행
        data_fs_y_clean = clean_fs(data_fs_y, ticker, 'y')

        # 분기 데이터
        data_fs_q = pd.concat([
            data[1].iloc[:, ~data[1].columns.str.contains('전년동기')], 
            data[3],
            data[5]
        ])
        
        data_fs_q = data_fs_q.rename(columns={data_fs_q.columns[0]: "계정"})

        #사전에 만든 함수 실행
        data_fs_q_clean = clean_fs(data_fs_q, ticker, 'q')

        # 두개 합치기
        data_fs_bind = pd.concat([data_fs_y_clean, data_fs_q_clean])

        # 재무제표 데이터를 DB에 저장
        args = data_fs_bind.values.tolist()
        mycursor.executemany(query, args)
        con.commit()

    except:

        # 오류 발생시 해당 종목명을 저장하고 다음 루프로 이동
        print(ticker)
        error_list.append(ticker)

    # 타임슬립 적용
    time.sleep(1)

# DB 연결 종료
engine.dispose()
con.close()

















