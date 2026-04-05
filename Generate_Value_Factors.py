import os
import numpy as np
import pandas as pd
import pymysql
from dotenv import load_dotenv
from sqlalchemy import create_engine

"""
연간 재무제표 기준으로 지표를 산출할 경우, 다음 연간 보고서가 공시되기 전까지 정보가 갱신되지 않는 한계가 있다.

이를 보완하기 위해 분기 재무제표를 사용하며, 최근 4개 분기 실적을 합산하는 TTM(Trailing Twelve Months) 방식을 적용하였다.

기본적인 가치 지표의 산출을 목표로 하기 때문에, 부수적으로 발생하는 문제점은 고려하지 않도록 한다.

[Limitations]

1. 재무제표 발표일(공시일)을 고려하지 않고 기준일 기준으로 계산하였다.
2. 시가총액 기준일과 재무제표 기준일 간 불일치가 발생할 수 있다.
3. 자본(Stock 계정)은 4개 분기 단순 평균으로 근사하였다.
"""

# 환경변수 로드
dotenv_path = r"C:\Users\minec\OneDrive\바탕 화면\python-code\.env"
load_dotenv(dotenv_path)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")




# DB 연결 및 데이터 불러오기
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

ticker_list = pd.read_sql("""
select *
from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker)
  and 종목구분 = '보통주';
""", con=engine)

sample_fs = pd.read_sql("""
select *
from kor_fs
where 공시구분 = 'q'
  and 종목코드 = '005930'
  and 계정 in ('당기순이익', '자본', '영업활동으로인한현금흐름', '매출액');
""", con=engine)

kor_fs = pd.read_sql("""
select *
from kor_fs
where 공시구분 = 'q'
  and 계정 in ('당기순이익', '자본', '영업활동으로인한현금흐름', '매출액');
""", con=engine)

engine.dispose()




# 가치지표 산출 함수
def make_value_indicators(fs_df, ticker_df):
    fs_df = fs_df.sort_values(['종목코드', '계정', '기준일']).copy()

    # groupby().rolling() 결과를 직접 대입하는 방식보다
    # transform()이 원본 길이/인덱스를 유지하므로 더 안전하다. (ttm 구할때는 이 방법이 더 우수함.)
    fs_df['ttm'] = fs_df.groupby(['종목코드', '계정'])['값'].transform(
        lambda x: x.rolling(window=4, min_periods=4).sum())

    # Flow 계정은 최근 4개 분기 합계 사용. Stock 계정(자본)은 평균값으로 근사
    fs_df['ttm'] = np.where(
        fs_df['계정'] == '자본',
        fs_df['ttm'] / 4,
        fs_df['ttm'])

    # 각 종목-계정별 가장 최근 값만 사용
    fs_df = fs_df.groupby(['계정', '종목코드']).tail(1)

    value_df = fs_df[['계정', '종목코드', 'ttm']].merge(
        ticker_df[['종목코드', '시가총액', '기준일']],
        on='종목코드')

    # 시가총액 단위를 1억 원 기준으로 맞춤
    value_df['시가총액'] = value_df['시가총액'] / 100000000

    # 가치지표 계산
    value_df['값'] = value_df['시가총액'] / value_df['ttm']
    value_df['값'] = value_df['값'].round(4)

    value_df['지표'] = np.where(value_df['계정'] == '매출액', 'PSR',
                         np.where(value_df['계정'] == '영업활동으로인한현금흐름', 'PCR',
                         np.where(value_df['계정'] == '자본', 'PBR',
                         np.where(value_df['계정'] == '당기순이익', 'PER', None))))

    value_df = value_df.rename(columns={'값': '값'})
    value_df = value_df[['종목코드', '기준일', '지표', '값']]
    value_df = value_df.replace([np.inf, -np.inf, np.nan], None)

    return value_df




# 배당수익률 함수
def make_dividend_yield(ticker_df):
    dy_df = ticker_df.copy()
    dy_df['값'] = dy_df['주당배당금'] / dy_df['종가']
    dy_df['값'] = dy_df['값'].round(4)
    dy_df['지표'] = 'DY'

    dy_df = dy_df[['종목코드', '기준일', '지표', '값']]
    dy_df = dy_df.replace([np.inf, -np.inf, np.nan], None)
    dy_df = dy_df[dy_df['값'] != 0]

    return dy_df




# 단일 종목 테스트
sample_value = make_value_indicators(fs_df=sample_fs, ticker_df=ticker_list[ticker_list['종목코드'] == '005930'].copy())

sample_dy = make_dividend_yield(ticker_list[ticker_list['종목코드'] == '005930'].copy())




# 전 종목 가치지표 계산
kor_value = make_value_indicators(fs_df=kor_fs, ticker_df=ticker_list)

dy_list = make_dividend_yield(ticker_list)




# SQL 적재
query = """
insert into kor_value (종목코드, 기준일, 지표, 값)
values (%s, %s, %s, %s) as new
on duplicate key update
값 = new.값
"""

con = pymysql.connect(
    user=DB_USER,
    passwd=DB_PASSWORD,
    host=DB_HOST,
    db=DB_NAME,
    charset='utf8'
)

try:
    mycursor = con.cursor()

    args_fs = kor_value.values.tolist()
    mycursor.executemany(query, args_fs)

    args_dy = dy_list.values.tolist()
    mycursor.executemany(query, args_dy)

    con.commit()

except Exception:
    con.rollback()  # 중간 실패 시 전체 취소
    raise

finally:
    con.close()





