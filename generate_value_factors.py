"""
연간 재무제표 기준으로 지표를 산출할 경우, 다음 연간 보고서가 공시되기 전까지 정보가 갱신되지 않는 한계가 있다.
이를 보완하기 위해 분기 재무제표를 사용하며, 최근 4개 분기 실적을 합산하는 TTM(Trailing Twelve Months) 방식을 적용하였다.

[Limitations]

1. 재무제표 발표일(공시일)을 고려하지 않고 기준일 기준으로 계산하였다.
2. 시가총액 기준일과 재무제표 기준일 간 불일치가 발생할 수 있다.
3. 자본(Stock 계정)은 4개 분기 단순 평균으로 근사하였다.
"""

from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

# .env 파일 경로 지정
dotenv_path = r"C:\Users\minec\OneDrive\바탕 화면\python-code\.env"
load_dotenv(dotenv_path)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")




#단일 종목으로 가치지표를 구한 후, 해당 로직을 이용하여 전 종목의 가치지표를 구하도록 한다.

# DB 연결
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# 티커 리스트
ticker_list = pd.read_sql("""
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker) 
	and 종목구분 = '보통주';
""", con=engine)

# 삼성전자 분기 재무제표
sample_fs = pd.read_sql("""
select * from kor_fs
where 공시구분 = 'q'
and 종목코드 = '005930'
and 계정 in ('당기순이익', '자본', '영업활동으로인한현금흐름', '매출액');
""", con=engine)

engine.dispose() #engine.dispose() → SQLAlchemy 전용

sample_fs = sample_fs.sort_values(['종목코드', '계정', '기준일'])

#1년 단위 성과를, 분기마다 끊임없이 업데이트해서 판단하기 위해서 이렇게 코드를 짠다.
sample_fs['ttm'] = sample_fs.groupby(['종목코드', '계정'],
                   as_index=False)['값'].rolling(window=4, min_periods=4).sum()['값'] 




#Flow 계정은 합계를 하면 끝이지만, Stock 계정은 반드시 평균을 해줘야 한다.
import numpy as np

sample_fs['ttm'] = np.where(sample_fs['계정'] == '자본',
                            sample_fs['ttm'] / 4, sample_fs['ttm']) 
sample_fs = sample_fs.groupby(['계정', '종목코드']).tail(1)

sample_fs_merge = sample_fs[['계정', '종목코드', 'ttm']].merge(
    ticker_list[['종목코드', '시가총액', '기준일']], on='종목코드')

#단위를 맞추기 위하여 시가총액을 1억으로 나눠준다.
sample_fs_merge['시가총액'] = sample_fs_merge['시가총액']/100000000

#가치지표 계산
sample_fs_merge['value'] = sample_fs_merge['시가총액'] / sample_fs_merge['ttm']
sample_fs_merge['지표'] = np.where(sample_fs_merge['계정'] == '매출액', 'PSR',
                          np.where(sample_fs_merge['계정'] == '영업활동으로인한현금흐름', 'PCR',
                          np.where(sample_fs_merge['계정'] == '자본', 'PBR',
                          np.where(sample_fs_merge['계정'] == '당기순이익', 'PER', None))))

#배당수익률 계산
ticker_list_dividend = ticker_list[ticker_list['종목코드'] == '005930'].copy()
ticker_list_dividend['DY'] = ticker_list_dividend['주당배당금'] / ticker_list_dividend['종가']




#전 종목의 가치지표를 구하고 MYSQL에 적재하기. (단일 종목 테스트 로직을 전체 종목에 확장)
import pymysql

# DB 연결
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
con = pymysql.connect(
    user=DB_USER,
    passwd=DB_PASSWORD,
    host=DB_HOST,
    db=DB_NAME,
    charset='utf8')

mycursor = con.cursor()



# 분기 재무제표 불러오기
kor_fs = pd.read_sql("""
select * from kor_fs
where 공시구분 = 'q'
and 계정 in ('당기순이익', '자본', '영업활동으로인한현금흐름', '매출액');
""", con=engine)

# 티커 리스트 불러오기
ticker_list = pd.read_sql("""
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker) 
and 종목구분 = '보통주';
""", con=engine)

engine.dispose()




kor_fs = kor_fs.sort_values(['종목코드', '계정', '기준일'])
kor_fs['ttm'] = kor_fs.groupby(['종목코드', '계정'], 
                as_index=False)['값'].rolling(window=4, min_periods=4).sum()['값']

kor_fs['ttm'] = np.where(kor_fs['계정'] == '자본', kor_fs['ttm'] / 4, kor_fs['ttm'])

kor_fs = kor_fs.groupby(['계정', '종목코드']).tail(1)

kor_fs_merge = kor_fs[['계정', '종목코드','ttm']].merge(
    ticker_list[['종목코드', '시가총액', '기준일']], on='종목코드')
kor_fs_merge['시가총액'] = kor_fs_merge['시가총액'] / 100000000

kor_fs_merge['value'] = kor_fs_merge['시가총액'] / kor_fs_merge['ttm']
kor_fs_merge['value'] = kor_fs_merge['value'].round(4)
kor_fs_merge['지표'] = np.where(kor_fs_merge['계정'] == '매출액', 'PSR',
                       np.where(kor_fs_merge['계정'] == '영업활동으로인한현금흐름', 'PCR',
                       np.where(kor_fs_merge['계정'] == '자본', 'PBR',
                       np.where(kor_fs_merge['계정'] == '당기순이익', 'PER', None))))

#kor_fs_merge.rename(columns={'value': '값'}, inplace=True) #inplace=True는 기존 객체를 직접 수정한다는 의미임. (이 코드도 가능함.)
#하지만 최근 실무에서는 inplace보다는 아래와 같은 재할당 방식이 더 권장된다고 한다. 체이닝 구조에서 더 안전하고 성능상 차이가 없어서다.
kor_fs_merge = kor_fs_merge.rename(columns={'value': '값'}) 
kor_fs_merge = kor_fs_merge[['종목코드', '기준일', '지표', '값']]
kor_fs_merge = kor_fs_merge.replace([np.inf, -np.inf, np.nan], None) #None으로 치환.




#SQL에 적재하기
query = """
    insert into kor_value (종목코드, 기준일, 지표, 값)
    values (%s,%s,%s,%s) as new
    on duplicate key update
    값=new.값
"""

args_fs = kor_fs_merge.values.tolist()
mycursor.executemany(query, args_fs)
con.commit()




ticker_list['값'] = ticker_list['주당배당금'] / ticker_list['종가']
ticker_list['값'] = ticker_list['값'].round(4)
ticker_list['지표'] = 'DY'
dy_list = ticker_list[['종목코드', '기준일', '지표', '값']]
dy_list = dy_list.replace([np.inf, -np.inf, np.nan], None)
dy_list = dy_list[dy_list['값'] != 0] #0인 값은 버림

args_dy = dy_list.values.tolist()
mycursor.executemany(query, args_dy)
con.commit()


con.close() #con.close() → pymysql 전용





