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
import time




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
# 2. 메타데이터 기반으로 시계열 정보를 가져옴
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
    df_f = pd.DataFrame.from_records(fundamentals_daily)

    if not df_f.empty:
        df_f['ticker'] = ticker
        df_f['date'] = pd.to_datetime(df_f['date'])
        df_f.sort_values('date', inplace=True)

except Exception as e:
    print(f"fundamentals_daily 오류: {e}")
    df_f = pd.DataFrame()



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
        df_fs['ticker'] = ticker

    # 숫자 변환
    for col in df_fs.columns:
        try:
            df_fs[col] = pd.to_numeric(df_fs[col])
        except:
            pass

except Exception as e:
    print(f"재무제표 오류: {e}")
    df_fs = pd.DataFrame()




# 6. 결과 확인
print("\n[Prices]")
print(prices.head())

print("\n[Fundamentals Daily]")
print(df_f.head())

print("\n[Financial Statements]")
print(df_fs.head())


"""
Dow 30 ETL Pipeline

Purpose:
    Collect and store historical price and fundamental data for the
    30 constituents of the Dow Jones Industrial Average (DJIA).

Clarification:
    This pipeline is designed for data engineering and analysis purposes.
    It does NOT attempt to reproduce the DJIA index value.

Index weighting methodologies (for reference):
    Price-weighted
     - Index level determined by sum of stock prices / divisor
     - Example: Dow Jones Industrial Average

Market capitalization-weighted
     - Weights based on total market value of each company
     - Example: S&P 500

Equal-weighted
     - Each constituent assigned identical weight
     - Used in alternative index strategies
"""



#위의 단일종목에 대한 로직을 다우 30종목에 적용하도록 함.
#tiingo에서 무료로 받을 수 있는 게 다우지수라서 다우지수를 기준으로한 ETL 코드를 짜도록 하자.
DOW30 = [
    "AAPL","MSFT","JPM","V","PG","GS","HD","CVX","MRK","UNH",
    "KO","DIS","MCD","NKE","AMGN","TRV","AXP","CRM","HON","IBM",
    "INTC","WMT","BA","CAT","CSCO","JNJ","MMM","VZ","WBA","DOW"
]


all_prices = []
all_fundamentals = []
all_statements = []


for i, ticker in enumerate(DOW30, start=1):
    print(f"[{i}/{len(DOW30)}] 처리 중: {ticker}")

    # 4-1. Metadata
    metadata = client.get_ticker_metadata(ticker)
    start_date = metadata.get("startDate")
    end_date = metadata.get("endDate") or date.today().isoformat()

    # 4-2. 가격 데이터
    try:
        prices = client.get_dataframe(
            ticker,
            startDate=start_date,
            endDate=end_date,
            frequency="daily"
        )

        if not prices.empty:
            prices = prices[['adjClose', 'adjVolume']]
            prices['ticker'] = ticker
            prices.reset_index(inplace=True)
            prices.rename(columns={'date': 'tradeDate'}, inplace=True)
            all_prices.append(prices)

    except Exception as e:
        print(f"가격 오류: {ticker} → {e}")

    # 4-3. Daily Fundamentals
    try:
        fundamentals_daily = client.get_fundamentals_daily(ticker)
        df_f = pd.DataFrame.from_records(fundamentals_daily)

        if not df_f.empty:
            df_f['ticker'] = ticker
            df_f['date'] = pd.to_datetime(df_f['date'])
            df_f.sort_values('date', inplace=True)
            all_fundamentals.append(df_f)

    except Exception as e:
        print(f"fundamentals 오류: {ticker} → {e}")

    # 4-4. 재무제표
    try:
        fundamentals_stmnts = client.get_fundamentals_statements(
            ticker,
            startDate='2017-01-01',
            asReported=True,
            fmt='csv'
        )

        df_fs = pd.read_csv(StringIO(fundamentals_stmnts))

        if not df_fs.empty:
            df_fs['ticker'] = ticker
            all_statements.append(df_fs)

    except Exception as e:
        print(f"재무제표 오류: {ticker} → {e}")

    time.sleep(3)  

# 5. 병합
prices_df = pd.concat(all_prices, ignore_index=True)
fundamentals_df = pd.concat(all_fundamentals, ignore_index=True)
statements_df = pd.concat(all_statements, ignore_index=True)

print("완료")
print("prices:", prices_df.shape)
print("fundamentals:", fundamentals_df.shape)
print("statements:", statements_df.shape)




#SQL 적재부분까지 완료한 후에 리팩토링하면 될듯










