#이 프로젝트는 자동화를 목표로 짜보자.

"""
import keyring # 내부적으로 Windows Vault에 저장하여 암호화해주는 패키지 

#보안을 위하여 딱 한번만 실행하고 코드를 지우도록 하자.
keyring.set_password(
    "System",
    "User Name",
    "Your API Key"
)

# 저장 확인
api_key = keyring.get_password("System", "User Name")
print("Saved key:", api_key)
"""

import keyring
from tiingo import TiingoClient
import pandas as pd
from datetime import date
from io import StringIO




# 1. Tiingo Client 설정
api_key = keyring.get_password('tiingo', 'bycraftsman')
print("Saved key:", api_key)
config = {
    'session': True,
    'api_key': api_key
}

client = TiingoClient(config)




#메타데이터 기준으로 시계열 주가 데이터 추출
#애플 주식을 기준으로 일단 1번 짜보고 후에 전종목으로 확장해서 SQL에 적재하는 방식으로 가는 게 나을듯.
# 2. 메타데이터 조회
ticker = "AAPL"

metadata = client.get_ticker_metadata(ticker)
print(metadata)

start_date = metadata.get("startDate")
end_date = metadata.get("endDate")

# endDate가 None이면 오늘 날짜로 설정
if end_date is None:
    end_date = date.today().isoformat()

print(f"{ticker} 기간: {start_date} ~ {end_date}")




# 3. 시계열 가격 데이터
try:
    prices = client.get_dataframe(
        ticker,
        startDate=start_date,
        endDate=end_date,
        frequency="daily"
    )

    # 필요한 컬럼만 선택
    prices = prices[['adjClose', 'adjVolume']]

    # ticker 컬럼 추가 (SQL 적재 대비)
    prices['ticker'] = ticker

    # 인덱스 → 컬럼 변환
    prices.reset_index(inplace=True)
    prices.rename(columns={'date': 'tradeDate'}, inplace=True)

except Exception as e:
    print(f"가격 데이터 오류: {e}")
    prices = pd.DataFrame()




# 4. Daily Fundamentals
try:
    fundamentals_daily = client.get_fundamentals_daily(ticker)
    fundamentals_df = pd.DataFrame.from_records(fundamentals_daily)

    if not fundamentals_df.empty:
        fundamentals_df['ticker'] = ticker
        fundamentals_df['date'] = pd.to_datetime(fundamentals_df['date'])

except Exception as e:
    print(f"fundamentals_daily 오류: {e}")
    fundamentals_df = pd.DataFrame()




# 5. 재무제표
try:
    fundamentals_stmnts = client.get_fundamentals_statements(
        ticker,
        startDate='2017-01-01',
        asReported=True,
        fmt='csv'
    )

    df_fs = pd.read_csv(StringIO(fundamentals_stmnts))

    if not df_fs.empty:
        df_fs['date'] = pd.to_datetime(df_fs['date'])
        df_fs.set_index('date', inplace=True)
        df_fs = df_fs.apply(lambda col: pd.to_numeric(col, errors='coerce'))
        df_fs['ticker'] = ticker

except Exception as e:
    print(f"재무제표 오류: {e}")
    df_fs = pd.DataFrame()




# 6. 결과 확인
print("\n[Prices]")
print(prices.head())

print("\n[Fundamentals Daily]")
print(fundamentals_df.head())

print("\n[Financial Statements]")
print(df_fs.head())

















-------------------------------------------------------------------------------------------------
싹다 갈아엎어야 함. investing.com은 크롤링 차단 심하고 HTML 구조 자주 변경되서
예전에 짠 코드가 작동하지 않음. 안정적으로 재무제표 및 시계열 데이터를 구할 수 있는 곳으로 변경하고
아래 코드는 지우도록 함.







from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from datetime import datetime
import math
import pandas as pd
import numpy as np
from tqdm import tqdm
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
nationcode = '5'
url = f'''https://investing.com/stock-screener/?sp=country::
{nationcode}|sector::a|industry::a|equityType::ORD%3Ceq_market_cap;1'''
driver.get(url)

html = BeautifulSoup(driver.page_source, 'lxml')
html.find(class_='js-search-input inputDropDown')['value']

html_table = html.select('table.genTbl.openTbl.resultsStockScreenerTbl.elpTbl')

print(html_table[0])







WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
    (By.XPATH, '//*[@id="resultsTable"]/tbody')))

end_num = driver.find_element(By.CLASS_NAME, value='js-total-results').text
end_num = math.ceil(int(end_num) / 50)


all_data_df = []

for i in tqdm(range(1, end_num + 1)):

    url = f'''https://investing.com/stock-screener/?sp=country::
        {nationcode}|sector::a|industry::a|equityType::ORD%3Ceq_market_cap;{i}'''
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="resultsTable"]/tbody')))
    except:
        time.sleep(1)
        driver.refresh()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="resultsTable"]/tbody')))

    html = BeautifulSoup(driver.page_source, 'lxml')

    html_table = html.select(
        'table.genTbl.openTbl.resultsStockScreenerTbl.elpTbl')
    df_table = pd.read_html(html_table[0].prettify())
    df_table_select = df_table[0][['Name', 'Symbol',
                                   'Exchange',  'Sector', 'Market Cap']]

    all_data_df.append(df_table_select)

    time.sleep(2)

all_data_df_bind = pd.concat(all_data_df, axis=0)

data_country = html.find(class_='js-search-input inputDropDown')['value']
all_data_df_bind['country'] = data_country
all_data_df_bind['date'] = datetime.today().strftime('%Y-%m-%d')
all_data_df_bind = all_data_df_bind[~all_data_df_bind['Name'].isnull()]
all_data_df_bind = all_data_df_bind[all_data_df_bind['Exchange'].isin(
    ['NASDAQ', 'NYSE', 'NYSE Amex'])]
all_data_df_bind = all_data_df_bind.drop_duplicates(['Symbol'])
all_data_df_bind.reset_index(inplace=True, drop=True)
all_data_df_bind = all_data_df_bind.replace({np.nan: None})

driver.quit()



import pymysql

con = pymysql.connect(user='',
                      passwd='',
                      host='',
                      db='',
                      charset='utf8')

mycursor = con.cursor()
query = """
    insert into global_ticker (Name, Symbol, Exchange, Sector, `Market Cap`, country, date)
    values (%s,%s,%s,%s,%s,%s,%s) as new
    on duplicate key update
    name=new.name,Exchange=new.Exchange,Sector=new.Sector,
    `Market Cap`=new.`Market Cap`; 
"""

args = all_data_df_bind.values.tolist()

mycursor.executemany(query, args)
con.commit()

con.close()





