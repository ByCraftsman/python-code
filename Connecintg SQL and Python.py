import pymysql

#SQL 데이터 불러오기
con = pymysql.connect(
    user='root',
    passwd='5787',
    host='127.0.0.1',
    db='shop',
    charset='utf8mb4'
)
"""
charset은 파이썬과 MySQL 서버 간에 문자열 데이터를 주고받을 때
어떤 문자셋(인코딩 규칙)을 사용할지를 지정하는 옵션임.


파이썬 내부에서는 문자열이 이미 유니코드(unicode)로 처리되므로, 별도의 설정 없이 UTF-8을 사용함.
하지만 MySQL의 utf8 문자셋은 최대 3바이트까지만 지원하는 불완전한 UTF-8 구현이므로, 
4바이트 유니코드를 완전히 지원하는 utf8mb4를 사용함. 실무에서는 utf8mb4 사용이 사실상 표준임.
"""


#cursor() 메서드를 통해 데이터베이스의 커서 객체를 가져옴.
#커서란 화면에서 현재 사용자의 위치를 나타내며 깜빡거리는 막대기를 커서라고 함.
mycursor = con.cursor()

query = """
    select * from goods;
"""

mycursor.execute(query) #쿼리 실행
data = mycursor.fetchall() #실제로 데이터를 불러옴.

con.close() # 데이터를 불러온 후에 반드시 닫아야 오류가 안생김.
mycursor.close() # cursor도 리소스 관리를 위해 닫는 것이 원칙이라 함.

data #이러한 방식으로 데이터를 불러오면 tuple 형태로 불러오게 된다.
# 때문에 열 이름도 보이지 않고, 데이터 분석에 용이한 데이터프레임 형태도 아니다.




#파이썬으로 데이터 SQL에 삽입하기
con = pymysql.connect(
    user='root',
    passwd='5787',
    host='127.0.0.1',
    db='shop',
    charset='utf8mb4'
)

mycursor = con.cursor()

query2 = """
    insert into goods (goods_id, goods_name, goods_classify, sell_price, buy_price, register_data)
    values ('0009', '스테이플러', '사무용품', '2000', '1500', '2020-12-30');
"""

mycursor.execute(query2)
con.commit() #삽입, 갱신, 삭제 등의 DML(Data Manipulation Language) 문자를 실행하는 경우는 commit을 해줌.
con.close()
mycursor.close()




#pandas를 이용하여 SQL에 연결
import pandas as pd
from sqlalchemy import create_engine #pandas SQL에 연결할 때는 SQLalchemy ORM을 사용함

#사용법 -> create_engine('mysql+pymysql://[사용자명]:[비밀번호]@[호스트:포트]/[사용할 데이터베이스]')
engine = create_engine('mysql+pymysql://root:5787@127.0.0.1:3306/shop')

query3 = """select * from Goods"""
goods = pd.read_sql(query3, con=engine)
engine.dispose()




#데이터 프레임을 SQL에 저장하기
import seaborn as sns

iris = sns.load_dataset('iris')

engine = create_engine('mysql+pymysql://root:5787@127.0.0.1:3306/shop')
#if_exists = 'replace' 는 해당 테이블이 이미 존재할 시 데이터를 덮어쓴다는 의미임.
iris.to_sql(name = 'iris', con = engine, index = False, if_exists = 'replace') 
engine.dispose()




#퀀트 투자에서 사용하는 시계열 데이터는 크게 두가지 특성이 있음.
#insert는 시간이 지남에 따라 데이터가 추가됨. update는 간혹 데이터를 수정됨.
from sqlalchemy_utils import create_database # <- 데이터베이스를 만들 때 사용하는 함수임.

#'exam'이라는 이름으로 데이터베이스를 만듦. 
create_database('mysql+pymysql://root:5787@127.0.0.1:3306/exam') 

price = pd.DataFrame({
    "날짜": ['2021-01-02', '2021-01-03'],
    "티커": ['000001', '000001'],
    "종가": [1340, 1315],
    "거래량": [1000, 2000]
})


engine2 = create_engine('mysql+pymysql://root:5787@127.0.0.1:3306/exam')
#if_exists='append'는 테이블이 존재할 경우 기존 테이블에 데이터를 추가함.
price.to_sql('price', con=engine2, if_exists='append', index=False)
data_sql = pd.read_sql('price', con=engine2)
engine2.dispose()




#새로운 데이터 추가하기
new = pd.DataFrame({
    "날짜": ['2021-01-04'],
    "티커": ['000001'],
    "종가": [1320],
    "거래량": [1500]
})

#concat으로 이렇게 추가하면 인덱스가 지저분해 진다.
#하지만 어차피 sql로 저장할때 index=False하면 되서 상관이 없기는 하다.
price = pd.concat([price, new])

engine = create_engine('mysql+pymysql://root:5787@127.0.0.1:3306/exam')
#진짜 문제점은 이렇게 'append'로 해버리면, 그냥 행방향으로 데이터가 추가되버린다는 것이다.
#그렇다고 'replace'를 사용하면 3개의 행이 잘 나오기는 하는데, 전 시계열 데이터가 있다면
#그것들이 전부 삭제되어 버리고 'price' 데이터만 남는 것이 문제다.
price.to_sql('price', con=engine, if_exists='append', index=False)
data_sql = pd.read_sql('price', con=engine)
engine.dispose()

#시계열 데이터 다룰 때, 수정주가 발생이나 데이터 전송 오류 시 재작업(Backfill)이 빈번함.
#때문에 기존 데이터프레임에 데이터를 추가하거나 또는 수정할 때, upsert 기능을 사용함.
#이 아래부터는 SQL문을 전부 실행하고 실행하셈.
price2 = pd.DataFrame({
    "날짜": ['2021-01-04', '2021-01-04'],
    "티커": ['000001', '000002'],
    "종가": [1320, 1315],
    "거래량": [2100, 1500]
})

#데이터프레임의 값들을 리스트 형태로 만듦.
args = price2.values.tolist()


con = pymysql.connect(user='root',
                      passwd='5787',
                      host='127.0.0.1',
                      db='exam',
                      charset='utf8mb4')

query4 = """
    insert into price_2 (날짜, 티커, 종가, 거래량)
    values (%s,%s,%s,%s) as new
    on duplicate key update
    종가 = new.종가, 거래량 = new.거래량;
"""

mycursor = con.cursor()
mycursor.executemany(query4, args)
con.commit()  #해당 메서드를 통해 데이터의 확정을 갱신
con.close()




#생성했던 exam 데이터베이스를 삭제함.
con = pymysql.connect(user='root',
                      passwd='5787',
                      host='127.0.0.1',
                      db='exam',
                      charset='utf8mb4')

query5 = """
    drop database exam;
"""

mycursor = con.cursor()
mycursor.execute(query5)
con.commit()


mycursor.close() 
con.close()




















