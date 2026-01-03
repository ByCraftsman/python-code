"""This project builds an ETL data pipeline for Korean listed stocks.
    국내 상장주식 데이터를 수집·정제·적재하는 ETL 파이프라인입니다."""

#데이터 정합성(Data Consistency) 이란 동일한 대상에 대해 서로 다른 데이터가 모순되지 않고, 
#논리적으로 일치하는 상태를 의미한다. 이러한 정합성의 유지는 굉장히 중요하다.

#파이프라인(Pipeline)이란 데이터가 “정해진 단계들을 순서대로” 거쳐 자동으로 처리되는 흐름을 말함.
import requests as rq
from bs4 import BeautifulSoup
import re
from io import BytesIO
import pandas as pd




#네이버 증권의 증시 자금 동향 날짜 불러오기
#Business date used as the snapshot date for the entire dataset
#This date represents the data extraction 기준일.
url = 'https://finance.naver.com/sise/sise_deposit.naver'
data = rq.get(url)
data_html = BeautifulSoup(data.content) #네이버는 HTML 형식이라서 이 패키지가 필요함

parse_day = data_html.select_one(
    'div.subtop_sise_graph2 > ul.subtop_chart_note > li > span.tah').text

print(parse_day) 

#정규식으로 데이터 클렌징
biz_day = re.findall('[0-9]+', parse_day) #숫자만
biz_day = ''.join(biz_day) #조인

print(biz_day) #이런 날짜 데이터는 매일 자동으로 업데이트 듸므로, 필요한 곳에 사용하면 됨.




# This code previously worked as an automated KRX data extractor.
# However, as of 2025-12-27, KRX requires authenticated login to download files,
# which prevents programmatic access via HTTP requests.
# As a result, KRX data is obtained via manual download.

#주식 관련 데이터를 구하기 위해서 가장 먼저 해야하는 일은 어떤 종목이 상장되어 있는가에 대한 정보를 구하는 것이다.
#우리나라의 경우에는 한국거래소에서 제공하는 업종분류 현황과 개별종목 지표 데이터를 이용하면 간단하게 구할 수 있다.
#하지만 매번 해당 파일을 다운로드하고 이를 불러오는 작업은 상당히 비효율적이기 때문에, 
#크롤링을 이용한다면 해당 데이터를 파이썬에서 바로 불러올 수 있다.
#이 코드는 한국거래소 정책 변경으로 제대로 기능하지 못함. 
#한국거래소는 2025-12-27부로 로그인을 해야만 데이터를 받을 수 있게 바꿧다.
gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
gen_otp_stk = {
    'mktId': 'STK',
    'trdDd': biz_day,
    'money': '1',
    'csvxls_isNo': 'false',
    'name': 'fileDown',
    'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'
}
#봇으로 인식되지 않으려면 Referer가 필요함. url을 다 입력해도 되고 적당히 경로를 입력해도 된다.
headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'} 

otp_stk = rq.post(gen_otp_url, gen_otp_stk, headers=headers).text
print(otp_stk)


down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'

#이 코드를 실행해보면, permission이 없다고 할것이다. (예전까지는 됐었는데 이제는 안됨.)
#차선책으로 Selenium으로 자동화를 해보려고 하였으나 개발자도구의 접근까지 막혀 있기 때문에,
#현재로서는 이게 자동화가 가능한지 모르겠음. 
down_sector_stk = rq.post(down_url, {'code': otp_stk}, headers=headers)
down_sector_stk.content
sector_stk = pd.read_csv(BytesIO(down_sector_stk.content), encoding='EUC-KR')
sector_stk.head()




#그래서 그냥 판다스로 불러와서 데이터 처리를 하도록 함.
krx_kospi = pd.read_excel(r"C:\Users\minec\OneDrive\바탕 화면\파이썬 엑셀파일\코스피_업종분류현황.xlsx", sheet_name='Sheet1')
krx_kosdaq = pd.read_excel(r"C:\Users\minec\OneDrive\바탕 화면\파이썬 엑셀파일\코스닥_업종분류현황.xlsx", sheet_name='Sheet1')

krx_aggregation = pd.concat([krx_kospi, krx_kosdaq]).reset_index(drop = True)

#종목명에 간혹 공백이 존재하므로, 미리 클렌징 처리하도록함.
krx_aggregation['종목명'] = krx_aggregation['종목명'].str.strip() #str.strip은 공백이 있을 경우 제거해줌.
#기준일 열 추가
krx_aggregation['기준일'] = biz_day 


#PER,PBR,배당수익률(개별종목)
krx_ind = pd.read_excel(r"C:\Users\minec\OneDrive\바탕 화면\파이썬 엑셀파일\PER,PBR,배당수익률(개별종목).xlsx", sheet_name='Sheet1')
krx_ind['종목명'] = krx_ind['종목명'].str.strip()
krx_ind['기준일'] = biz_day 

#Stock names are normalized by removing parenthetical annotations. (락)
#krx_ind는 종목명에 (락)이 붙어 있어서 종목명의 일치가 안되므로 지워줘야함. (최근에 생긴듯.)
#현업에서의 정석은 Raw data는 재현성과 감사 가능성을 위해 보존하고, 모든 정제 과정은 코드로 처리함. 
krx_ind['종목명'] = (
    krx_ind['종목명']
    .str.replace(r'\(.*?\)', '', regex=True) 
    .str.strip() 
)  #replace로 치환해서 없애주고, 공백까지 제거하였음.


#이제 다운로드 받은 데이터를 정리하도록 함. (디버깅 먼저)
#set으로 집합을 만듦. symmetric_difference로 하나의 집합에만 존재하는 부분을 찾음. 
#symmetric_difference가 크다는 건 ‘데이터 우주(universe)가 다르다’는 증거임. (락)을 지우기 전에 3387이 나옴.
len(set(krx_aggregation['종목명']).symmetric_difference(set(krx_ind['종목명'])))
krx_aggregation['종목명'].dtype
krx_ind['종목명'].dtype


#krx_aggregation과 krx_ind을 합침.
kor_ticker = pd.merge(
    krx_aggregation,
    krx_ind,
    on='종목코드',     
    how='outer'
)

base_cols = set(krx_aggregation.columns).intersection(krx_ind.columns)
base_cols.discard('종목코드')

for col in base_cols:
    cols = [f"{col}_x", f"{col}_y"]
    #axis=1로 열기준으로, bfill이기 때문에 오른쪽 값을 왼쪽에 삽입하였음.
    kor_ticker[col] = kor_ticker[cols].bfill(axis=1).iloc[:, 0] 
    #원래 있던 _x, _y의 중복 칼럼들 제거.
    kor_ticker.drop(columns=cols, inplace=True)



#Classifying equity types. 주식들의 종목을 전부 구분해보도록 함.
import numpy as np
#스펙 (SPAC) 추출
kor_ticker['종목명'].str.contains('스팩|제[0-9]+호')
kor_ticker[kor_ticker['종목명'].str.contains('스팩|제[0-9]+호')]['종목명']

#우선주 (Preferred Shares) 추출 (국내 종묵은 종목코드 끝이 0이 아니면 우선주임.)
kor_ticker['종목코드'].str[-1:] !='0' #-1:은 맨뒤의 글자를 의미.
kor_ticker[kor_ticker['종목코드'].str[-1:] !='0']['종목명']

#리츠 (REITs) 종목은 종목명이 '리츠'로 끝남.
kor_ticker[kor_ticker['종목명'].str.endswith('리츠')]


diff = list(set(krx_aggregation['종목명']).symmetric_difference(set(krx_ind['종목명'])))
print(diff)

kor_ticker['종목구분'] = np.where(kor_ticker['종목명'].str.contains('스팩|제[0-9]+호'), '스팩',
                              np.where(kor_ticker['종목코드'].str[-1:] != '0', '우선주',
                                       np.where(kor_ticker['종목명'].str.endswith('리츠'), '리츠',
                                                np.where(kor_ticker['종목명'].isin(diff),  '기타', 
                                                #하나의 테이블에만 있는 종목은 기타로 처리
                                                '보통주')))) #그 외는 전부 보통주로 처리




#최종적인 클렌징 처리 (Data Cleaning)
kor_ticker = kor_ticker.reset_index(drop=True)
kor_ticker.columns = kor_ticker.columns.str.replace(' ', '') #선행 EPS, PER 등의 동백을 지우도록 함
kor_ticker = kor_ticker[['종목코드', '종목명', '시장구분', '종가',
                         '시가총액', '기준일', 'EPS', '선행EPS', 'BPS', '주당배당금', '종목구분']] #필요한 열만 남김.
kor_ticker['기준일'] = pd.to_datetime(kor_ticker['기준일'])

#리스트를 보면 문자열 -가 있음. 이게 있으면 SQL에서 처리못하고 오류남.
print(kor_ticker['선행EPS'].tolist())  # 리스트로 확인

#이 3개의 열이 문제이므로, None으로 대체하도록 함.
num_cols = ['EPS', '선행EPS', 'BPS']

for col in num_cols:
    kor_ticker[col] = pd.to_numeric(
        kor_ticker[col].replace('-', None),
        errors='coerce'    # 변환 실패 시 NaN으로 강제 변환하라는 뜻.
    )
    
kor_ticker = kor_ticker.where(pd.notnull(kor_ticker), None)


print(kor_ticker['선행EPS'].tolist())  # 리스트로 확인
print(kor_ticker.isnull().sum())  # NaN / None 개수 확인

#최종적으로 SQL로 보낼 수 있게 None으로 바꿈.
kor_ticker = kor_ticker.replace({np.nan: None})




#정제한 DataFrame을 SQL에 전송하기. 
import pymysql
con = pymysql.connect(user='',
                      passwd='',
                      host='127.0.0.1',
                      db='stock_db',
                      charset='utf8')

mycursor = con.cursor()
#upsert를 구현하는 query의 작성.
query = r"""
    insert into kor_ticker (종목코드,종목명,시장구분,종가,시가총액,기준일,EPS,선행EPS,BPS,주당배당금,종목구분)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) as new
    on duplicate key update
    종목명=new.종목명,시장구분=new.시장구분,종가=new.종가,시가총액=new.시가총액,EPS=new.EPS,선행EPS=new.선행EPS,
    BPS=new.BPS,주당배당금=new.주당배당금,종목구분 = new.종목구분;
""" #primary key인 종목코드와, 기준일은 제외해야함.

args = kor_ticker.values.tolist() #values를 리스트 형태로 바꿔야 함.
mycursor.executemany(query, args) #전송
con.commit()
mycursor.close()
con.close()
#----------------------------------------------------------------------------------------------------------------




#https://www.wiseindex.com 에서 에너지 섹터의 WICS 데이터를 가져옴.
#JSON의 경우에는 Request URL에 데이터가 바로 나타남. JSON 형식은 HTML과 달리 문법이 단순하고
#데이터의 용량이 작아서 빠른 속도로 데이터를 교환할 수 있다. 크클링에 용이한 형태이다.
fnguide_index_url = f'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={biz_day}&sec_cd=G10'
fng_data = rq.get(fnguide_index_url).json() #requests가 이미 JSON 파싱까지 처리해줘서 json 패키지는 필요 없다.

#섹터 구성종목인 list와 섹터 코드인 sector가 중요함. 
fng_data.keys()
fng_data['list']
fng_data['sector'] #섹터 코드를 확인하자.

#분석을 위해서 데이터프레임으로 가져옴.
fng_data_pd = pd.json_normalize(fng_data['list'])


#G10만 말고, 모든 섹터들을 크롤링해보도록 하자.
from tqdm import tqdm
import time
sector_code = ['G25', 'G35', 'G50', 'G40', 'G10', 'G20', 'G55', 'G30', 'G15', 'G45']

fng_data_sector = []

for i in tqdm(sector_code):
    url = f'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={biz_day}&sec_cd={i}' 
    #G10대신 i라는 변수를 입력하는 것만 다름.
    fng_data2 = rq.get(url).json()
    fng_data_pd2 = pd.json_normalize(fng_data2['list'])
    fng_data_sector.append(fng_data_pd2)
    time.sleep(2)

#클렌징 처리 (Data Cleaning)
kor_sector = pd.concat(fng_data_sector, axis = 0)
kor_sector = kor_sector[['IDX_CD', 'CMP_CD', 'CMP_KOR', 'SEC_NM_KOR']]
kor_sector['기준일'] = biz_day
kor_sector['기준일'] = pd.to_datetime(kor_sector['기준일'])


#SQL 연결
con = pymysql.connect(user='',
                      passwd='',
                      host='127.0.0.1',
                      db='stock_db',
                      charset='utf8')

mycursor = con.cursor()
query = r"""
    insert into kor_sector (IDX_CD, CMP_CD, CMP_KOR, SEC_NM_KOR, 기준일)
    values (%s,%s,%s,%s,%s) as new
    on duplicate key update
    IDX_CD = new.IDX_CD, CMP_KOR = new.CMP_KOR, SEC_NM_KOR = new.SEC_NM_KOR
"""

args = kor_sector.values.tolist()
mycursor.executemany(query, args)
con.commit()
con.close()





"""
##Readme 에 쓸 내용은 여기다가 임시로 적어둠.
## Project Overview
This project builds an ETL data pipeline for Korean listed stocks.

## Data Sources
- Naver Finance (HTML scraping)
- Korea Exchange (KRX) – manual download due to authenticated access requirements
- WiseIndex (JSON API)

## Pipeline Structure
1. Extract
2. Transform
3. Load (MySQL with UPSERT)

## Key Features
- Data cleansing and normalization
- Handling missing and malformed numeric values
- Stock type classification
- Sector composition data integration

## Tech Stack
- Python
- pandas, numpy
- requests, BeautifulSoup
- MySQL
"""
















