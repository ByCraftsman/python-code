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


api_key = keyring.get_password('tiingo', 'bycraftsman')
print("Saved key:", api_key)


config = {}
config['session'] = True
config['api_key'] = api_key
client = TiingoClient(config)


tickers = client.list_stock_tickers()
tickers_df = pd.DataFrame.from_records(tickers)

tickers_df.head()

tickers_df.groupby(['exchange', 'priceCurrency'])['ticker'].count()



ticker_metadata = client.get_ticker_metadata("AAPL")
print(ticker_metadata)


historical_prices = client.get_dataframe("AAPL",
                                         startDate='2017-08-01',
                                         frequency='daily')

historical_prices.head()



fundamentals_daily = client.get_fundamentals_daily('AAPL')
fundamentals_daily_df = pd.DataFrame.from_records(fundamentals_daily)

fundamentals_daily_df.head()





fundamentals_stmnts = client.get_fundamentals_statements(
    'AAPL', startDate='2019-01-01', asReported=True, fmt='csv')

df_fs = pd.DataFrame([x.split(',') for x in fundamentals_stmnts.split('\n')])
df_fs.columns = df_fs.iloc[0]
df_fs = df_fs[1:]
df_fs.set_index('date', drop=True, inplace=True)
df_fs = df_fs[df_fs.index != '']

df_fs.head()




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





