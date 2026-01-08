import keyring

keyring.set_password('dar_api_key', 'User Name', 'Password')

import requests as rq
from io import BytesIO
import zipfile

api_key = keyring.get_password('dart_api_key', 'juho')
codezip_url = f'''https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=610ea064c91f52e831c9d77e9ddda21d40fba52c'''
codezip_data = rq.get(codezip_url)
codezip_data.headers

codezip_data.headers['Content-Disposition']

codezip_file = zipfile.ZipFile(BytesIO(codezip_data.content))
codezip_file.namelist()


import xmltodict
import json
import pandas as pd

code_data = codezip_file.read('CORPCODE.xml').decode('utf-8')
data_odict = xmltodict.parse(code_data)
data_dict = json.loads(json.dumps(data_odict))
data = data_dict.get('result').get('list')
corp_list = pd.DataFrame(data)



import pymysql
from sqlalchemy import create_engine

corp_list = corp_list[~corp_list.stock_code.isin(
    [None])].reset_index(drop=True)

engine = create_engine('mysql+pymysql://root:5787@127.0.0.1:3306/stock_db')
corp_list.to_sql(name='dart_code', con=engine, index=True, if_exists='append')



# 전체 공시
from datetime import date
from dateutil.relativedelta import relativedelta

bgn_date = (date.today() + relativedelta(days=-7)).strftime("%Y%m%d")
end_date = (date.today()).strftime("%Y%m%d")

notice_url = f'''https://opendart.fss.or.kr/api/list.json?crtfc_key=610ea064c91f52e831c9d77e9ddda21d40fba52c
&bgn_de={bgn_date}&end_de={end_date}&page_no=1&page_count=100'''

notice_data = rq.get(notice_url)
notice_data_df = notice_data.json().get('list')
notice_data_df = pd.DataFrame(notice_data_df)

notice_data_df.tail()



corp_list[corp_list['corp_name'] == '삼성전자']

bgn_date = (date.today() + relativedelta(days=-30)).strftime("%Y%m%d")
end_date = (date.today()).strftime("%Y%m%d")
corp_code = '00126380'

notice_url_ss = f'''https://opendart.fss.or.kr/api/list.json?crtfc_key=610ea064c91f52e831c9d77e9ddda21d40fba52c
&corp_code={corp_code}&bgn_de={bgn_date}&end_de={end_date}&page_no=1&page_count=100'''

notice_data_ss = rq.get(notice_url_ss)
notice_data_ss_df = notice_data_ss.json().get('list')
notice_data_ss_df = pd.DataFrame(notice_data_ss_df)

notice_data_ss_df.tail()


notice_url_exam = notice_data_ss_df.loc[2, 'rcept_no']
notice_dart_url = f'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={notice_url_exam}'

print(notice_dart_url)



# 배당 관련 공시
corp_code = '00126380'
bsns_year = '2021'
reprt_code = '11011'

url_div = f'''https://opendart.fss.or.kr/api/alotMatter.json?crtfc_key=610ea064c91f52e831c9d77e9ddda21d40fba52c
&corp_code={corp_code}&bsns_year={bsns_year}&reprt_code={reprt_code}'''

div_data_ss = rq.get(url_div)
div_data_ss_df = div_data_ss.json().get('list')
div_data_ss_df = pd.DataFrame(div_data_ss_df)

div_data_ss_df.head()


#전 종목 재무제표 받기
url_fs = f'''https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?crtfc_key=610ea064c91f52e831c9d77e9ddda21d40fba52c
&corp_code={corp_code}&bsns_year={bsns_year}&reprt_code={reprt_code}&fs_div=OFS'''

fs_data_ss = rq.get(url_fs)
fs_data_ss_df = fs_data_ss.json().get('list')
fs_data_ss_df = pd.DataFrame(fs_data_ss_df)























