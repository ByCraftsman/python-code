"""
9시에 큰 변동성이 생기는 것을 이용하여 약간의 수익률만을 목표로 빠르게 매매하는 것을 목표로 함.
약 한달 간, 300~1500만원의 시드로 시도해 보았음. 결과적으로는 수익성이 매우 저조하였음.

가격을 펌핑시키는 세력들은 이미 지정가를 걸어두고 급등을 시키기 때문에, 후속으로 매수에 들어가는 이 전략은 불리할 수 밖에 없다는 결론임.
개미들의 매수세가 강력하다면 그에 따라 매매의 성공 확률이 높아지나, 결국은 장세에 영향을 많이 받는다는 뜻이므로 좋지 못함.

그리고 거래금액이 조금만 늘어나도 슬리피지 문제가 있고, 호가창 단위의 제약으로 인하여 정교한 매매가 기술적으로 불가능함.
하지만 이러한 문제점은 업비트나 빗썸이 아니라, 바이낸스 선물같이 거래량이 많은 거래소에서 매매한다면 어느정도 해결은 되리라 생각함.
"""



import time
import requests
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
from datetime import datetime
import pytz


#API 키 (업비트, 빗썸 공용)
ACCESS_KEY = ""
SECRET_KEY = ""
SERVER_URL = "https://api.upbit.com"


# 매수 조건 
TARGET_PERCENT_INCREASE = 0.0106
MONITORING_START_TIME = "08:59:57"
MONITORING_END_TIME = "09:00:25"
BUY_AMOUNT_KRW = 5000000 
KST = pytz.timezone("Asia/Seoul")


#JWT 헤더 생성 (query_hash 포함)
def get_headers(query=None):
    nonce = str(uuid.uuid4())  # UUID 형식의 nonce 생성

    payload = {
        "access_key": ACCESS_KEY,
        "nonce": nonce,
    }

    if query:
        query_string = urlencode(query, doseq=True).encode("utf-8")
        query_hash = hashlib.sha512(query_string).hexdigest()
        payload["query_hash"] = query_hash
        payload["query_hash_alg"] = "SHA512"
        
    # JWT 생성
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # 헤더 확인용 출력
    headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}
    return headers




#매수에서 제외하는 코인 (임의로 설정함.)
EXCLUDED_MARKETS = ["KRW-SBD", "KRW-BORA", "KRW-MED", "KRW-LSK", "KRW-GRS", "KRW-SAFE", "KRW-CARV", "KRW-MOC", "KRW-STRAX", "KRW-GAME2"]


#KRW 마켓 목록 가져오기 (제외 목록 필터링 포함)
def get_markets():
    url = f"{SERVER_URL}/v1/market/all"
    response = requests.get(url, headers=get_headers())
    if response.status_code != 200:
        raise ValueError(f"마켓 리스트 가져오기 실패: {response.json() if response.content else response.status_code}")
    
    # KRW 마켓만 필터링 + 제외 목록 제거
    markets = [market["market"] for market in response.json() if market["market"].startswith("KRW")]
    filtered_markets = [market for market in markets if market not in EXCLUDED_MARKETS]
    return filtered_markets




#선택된 마켓 가격 정보 가져오기
def get_ticker_info(filtered_markets):
    url = f"{SERVER_URL}/v1/ticker"
    params = {"markets": ",".join(filtered_markets)}
    response = requests.get(url, headers=get_headers(), params=params)
    if response.status_code != 200 or not response.json():
        raise ValueError(f"티커 정보 가져오기 실패: {response.json() if response.content else response.status_code}")
    return response.json()



#주문 UUID를 사용하여 실제 체결된 가격 가져오기
def get_actual_buy_price(order_uuid):
    url = f"{SERVER_URL}/v1/order"
    params = {"uuid": order_uuid}

    # 올바른 JWT 헤더 생성 (쿼리 파라미터 포함)
    headers = get_headers(params)

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        order_info = response.json()
        if order_info and "price" in order_info:
            return float(order_info["price"])  # 체결된 가격 반환
        else:
            print("주문 정보에서 가격을 찾을 수 없습니다.")
            return None
    else:
        print(f"주문 정보 조회 실패: {response.status_code}, {response.text}")
        return None




#시장가 매수 주문 (재시도 포함)
def place_market_buy_order(ticker, amount):
    url = f"{SERVER_URL}/v1/orders"
    query = {
        "market": ticker,
        "side": "bid",
        "price": str(amount),
        "ord_type": "price",  # 금액 기준 시장가 매수
    }

    headers = get_headers(query)

    # 최대 2번 재시도
    for attempt in range(1, 3):  
        response = requests.post(url, headers=headers, json=query)
        if response.status_code == 201:  # 매수 성공
            print(f"매수 성공: {ticker}, 금액: {amount} KRW")
            order_uuid = response.json()["uuid"]  # 주문 UUID 가져오기
            return order_uuid  # 주문 UUID 반환
        else:  # 매수 실패 시 재시도
            print(f"매수 실패 (시도 {attempt}/3): {response.status_code}, {response.text}")
            time.sleep(0.125)  # 대기 후 재시도

    # 3번 실패 후 프로그램 종료
    print(f"매수 실패: {ticker}, 모든 재시도 실패. 프로그램 종료.")
    return None




#목표 수익률 설정하기 + 실행 실패시 재시도함. (불발날 때가 종종 있어서)
def place_limit_sell_order_with_profit(ticker, order_uuid, profit_rate=0.004, retry_count=2, retry_delay=0.125):
    for attempt in range(retry_count):  # 재시도 루프
        try:
            # 1. 체결된 평균 매수 가격 가져오기
            buy_price = get_actual_buy_price(order_uuid)
            if not buy_price:
                print(f"체결된 가격을 확인할 수 없습니다. 매도하지 않습니다. (UUID: {order_uuid})")
                return

            # 2. 목표 매도 가격 계산
            target_sell_price = buy_price * (1 + profit_rate)
            print(f"[목표가 계산] 매수 평균가: {buy_price}, 목표 매도 가격: {target_sell_price}")

            # 3. 잔고 조회
            balance_url = f"{SERVER_URL}/v1/accounts"
            balance_response = requests.get(balance_url, headers=get_headers())

            if balance_response.status_code == 200:
                balances = balance_response.json()
                found_balance = False

                # 4. 잔고에서 종목 찾기
                for balance in balances:
                    if balance["currency"] == ticker.replace("KRW-", ""):
                        found_balance = True
                        volume = float(balance["balance"])
                        print(f"[잔고 확인] {ticker}: 잔고 {volume} {ticker.replace('KRW-', '')}")

                        # 5. 목표가를 수량으로 나눈 단위 가격 계산
                        price_per_unit = target_sell_price / volume
                        print(f"[매도 준비] 수량: {volume}, 단위 목표가: {price_per_unit} KRW")

                        # 6. 지정가 매도 주문
                        if place_limit_sell_order(ticker, price_per_unit, volume):
                            print(f"[매도 성공] 종목: {ticker}, 수량: {volume}, 목표가: {price_per_unit} KRW")
                        else:
                            print(f"[지정가 매도 실패] 시장가 매도로 전환: {ticker}")
                            place_market_sell_order(ticker, volume)
                        return  # 매도 성공 시 함수 종료

                if not found_balance:
                    print(f"{ticker}에 해당하는 잔고가 없습니다.")
                    raise Exception("잔고를 찾을 수 없습니다.")  # 잔고가 없으면 예외 발생시켜 재시도로 이동

            else:
                print(f"[잔고 조회 실패] 상태코드: {balance_response.status_code}, 응답: {balance_response.text}")
                raise Exception("잔고 조회 실패")

        except Exception as e:
            print(f"[재시도 {attempt + 1}/{retry_count}] 오류 발생: {e}")
            if attempt < retry_count - 1:
                time.sleep(retry_delay)  # 재시도 전 대기
            else:
                print("[매도 실패] 최대 재시도 횟수를 초과했습니다.")
                return

    print("[매도 실패] 잔고를 찾거나 매도에 실패했습니다.")




#업비트 틱 사이즈에 따라 가격 반올림
def round_price_to_tick_size(price):
    if price >= 2000000:
        return round(price, -3)  # 1,000 단위
    elif price >= 1000000:
        return round(price / 500) * 500  # 500 단위
    elif price >= 500000:
        return round(price / 100) * 100  # 100 단위
    elif price >= 100000:
        return round(price / 50) * 50  # 50 단위
    elif price >= 10000:
        return round(price / 10) * 10  # 10 단위
    elif price >= 1000:
        return round(price)  # 1 단위
    elif price >= 100:
        return round(price)  # 1 단위
    elif price >= 10:
        return round(price, 2)  # 0.01 단위
    elif price >= 1:
        return round(price, 3)  # 0.001 단위
    elif price >= 0.1:
        return round(price, 4)  # 0.0001 단위
    elif price >= 0.01:
        return round(price, 5)  # 0.00001 단위
    elif price >= 0.001:
        return round(price, 6)  # 0.000001 단위
    elif price >= 0.0001:
        return round(price, 7)  # 0.0000001 단위
    else:
        return round(price, 8)  # 0.00000001 단위
    





#틱 사이즈에 맞춤
def calculate_target_price(buy_avg_price, profit_rate=0.004):
    target_price = buy_avg_price * (1 + profit_rate)  # 매수 평균가에 이익률을 곱해 목표가 계산
    rounded_target_price = round_price_to_tick_size(target_price)  # 목표 가격을 틱 사이즈에 맞춰 반올림
    return rounded_target_price



def place_limit_sell_order(ticker, target_price, volume):
    rounded_price = round_price_to_tick_size(target_price)  # 틱 사이즈에 맞게 반올림

    # 지정가 매도 주문 시도
    url = f"{SERVER_URL}/v1/orders"
    query = {
        "market": ticker,
        "side": "ask",
        "volume": str(volume),
        "price": str(rounded_price),
        "ord_type": "limit",  # 지정가 매도
    }

    headers = get_headers(query)
    response = requests.post(url, headers=headers, json=query)

    if response.status_code == 201:
        print(f"매도 주문 성공: {ticker}, 수량: {volume}, 목표가: {rounded_price} KRW")
        return True
    else:
        print(f"매도 주문 실패: {response.status_code}, {response.text}")
        return False




#지정가 매도 실패시 시장가 매도
def place_market_sell_order(ticker, volume):
    url = f"{SERVER_URL}/v1/orders"
    query = {
        "market": ticker,
        "side": "ask",
        "volume": str(volume),
        "ord_type": "market",  # 시장가 매도
    }

    headers = get_headers(query)
    response = requests.post(url, headers=headers, json=query)

    if response.status_code == 201:
        print(f"시장가 매도 성공: {ticker}, 수량: {volume}")
        return True
    else:
        print(f"시장가 매도 실패: {response.status_code}, {response.text}")
        return False






def monitor_and_trade():
    """8:59:57 이후의 모니터링 및 매수/매도 실행"""
    markets = get_markets()
    base_prices = {}
    print(f"모니터링 시작: {MONITORING_START_TIME}")

    selected_markets = []  # 매수한 종목 리스트

    while datetime.now(KST).strftime("%H:%M:%S") < MONITORING_END_TIME:
        try:
            if not base_prices:  # 기준 가격 초기화
                ticker_info = get_ticker_info(markets)
                for ticker in ticker_info:
                    base_prices[ticker["market"]] = ticker["trade_price"]
                print(f"기준 가격 설정 완료: {base_prices}")
                continue

            ticker_info = get_ticker_info(markets)
            for ticker in ticker_info:
                if len(selected_markets) >= 3:  # 매수 코인 수의 제한 
                    print("3개의 종목을 매수하여 모니터링을 종료합니다.")
                    return

                market = ticker["market"]
                current_price = ticker["trade_price"]
                base_price = base_prices.get(market)

                # 제외 종목 필터링
                if market in exclude_markets or not base_price:
                    continue

                # 가격 상승률 계산
                increase_rate = (current_price - base_price) / base_price

                if increase_rate >= TARGET_PERCENT_INCREASE and market not in selected_markets:
                    print(f"{market} 가격 {increase_rate * 100:.2f}% 상승! 매수 대상 선정.")
                    order_uuid = place_market_buy_order(market, BUY_AMOUNT_KRW)  # 매수 주문 후 주문 UUID 반환
                    if not order_uuid:  # 매수 실패 시 프로그램 종료
                        print("매수 실패로 인해 프로그램을 종료합니다.")
                        return  # 프로그램 종료
                    else:
                        print(f"매수 성공! 주문 UUID: {order_uuid}")
                        selected_markets.append(market)  # 매수한 종목 추가
                        # 2% 상승 목표 가격을 기준으로 지정가 매도 주문
                        place_limit_sell_order_with_profit(market, order_uuid)

            time.sleep(0.125)
        except Exception as e:
            print(f"오류 발생: {e}")
            break

    print("모니터링 종료: 매수 조건 충족 종목이 부족합니다.")




if __name__ == "__main__":
    #9시 45초 이후에는 매수하지 않도록 하는 체크 추가
    current_time = datetime.now(KST).strftime("%H:%M:%S")
    PRE_MONITORING_START_TIME = "08:50:00"  # 8시 50분 시작
    PRE_MONITORING_END_TIME = "08:59:50"    # 8시 59분 종료

    if current_time >= MONITORING_END_TIME:
        print("현재 시간이 모니터링 시간을 넘어섭니다. 매수하지 않고 종료합니다.")
    else:
        # 8시 50분 전 대기
        while current_time < PRE_MONITORING_START_TIME:
            time.sleep(0.3)  # 시작 시간 전까지 대기
            current_time = datetime.now(KST).strftime("%H:%M:%S")

        print("8시 50분부터 8시 59분까지 급등 종목 필터링을 시작합니다.")
        pre_monitoring_start = datetime.now(KST).replace(hour=8, minute=50, second=0, microsecond=0)
        pre_monitoring_end = datetime.now(KST).replace(hour=8, minute=59, second=50, microsecond=0)

        # 8:50:00 ~ 8:59:50 급등 종목 필터링
        #급등 종목을 필터링한 이유는 단기적인 상승을 한 코인에서는 위험도가 약간 더 높다고 생각하였기 때문임.
        base_prices = {}
        exclude_markets = EXCLUDED_MARKETS.copy()
        while pre_monitoring_start <= datetime.now(KST) < pre_monitoring_end:
            try:
                print(f"[LOG] 현재 시간: {datetime.now(KST).strftime('%H:%M:%S')}. 급등 종목 필터링 중...")
                ticker_info = get_ticker_info(get_markets())
                for ticker in ticker_info:
                    market = ticker["market"]
                    current_price = ticker["trade_price"]

                    # 기준 가격 초기화
                    if market not in base_prices:
                        base_prices[market] = current_price
                    else:
                        # 사전의 급등 코인 필터링
                        initial_price = base_prices[market]
                        increase_rate = (current_price - initial_price) / initial_price
                        if increase_rate >= 0.017 and market not in exclude_markets:
                            exclude_markets.append(market)
                            print(f"1.7% 이상 급등한 종목 제외: {market} (상승률: {increase_rate * 100:.2f}%)")

                time.sleep(1)
            except Exception as e:
                print(f"[ERROR] 급등 종목 필터링 중 오류 발생: {e}")
                break

        print(f"필터링 완료. 제외 종목: {exclude_markets}")

        # 8:59:57까지 대기 후 모니터링 시작
        while current_time < MONITORING_START_TIME:
            time.sleep(0.3)
            current_time = datetime.now(KST).strftime("%H:%M:%S")

        # 모니터링 시작
        monitor_and_trade()






        







