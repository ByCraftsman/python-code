use shop;

-- 파이썬에서 commit 메소드를 사용 후, 행이 하나 추가된 것을 볼 수 있음.
select * from goods;

-- 파이썬 seaborn 데이터 셋을 불러오기
select * from iris;

-- 파이썬에서 데이터 베이스 생성하기
use exam;
select * from price;

-- 파이썬에서 price.to_sql('price', con=engine, if_exists='append', index=False) 후에 보면
-- 기존 데이터에 또 추가되서 중복되는 것을 볼 수 있다.
select * from price;


-- upsert란 기존에 있는 데이터를 그대로 두면서 새로운 데이터를 추가하거나 수정하는 것을 말함.
-- SQL에서 upsert를 구현하는 법은 insert를 사용하는 것임.
use exam;
create table price_2(
  날짜 varchar(10),
  티커 varchar(6),
  종가 int,
  거래량 int,
  primary key(날짜, 티커) -- 같은 날짜에도 여러 티커 (종목) 이 있으므로, PK를 날짜, 티커로 설정함.
);

select * from price_2;



insert into price_2 (날짜, 티커, 종가, 거래량)
values
('2021-01-02', '000001', 1340, 1000),
('2021-01-03', '000001', 1315, 2000),
('2021-01-02', '000002', 500, 200);

select * from price_2;



insert into price_2 (날짜, 티커, 종가, 거래량)
values
('2021-01-02', '000001', 1340, 1000),
('2021-01-03', '000001', 1315, 2000),
('2021-01-02', '000002', 500, 200),
('2021-01-03', '000002', 1380, 3000)
as new -- 별명
on duplicate key update
종가 = new.종가, 거래량 = new.거래량; -- PK를 뺀 나머지 열들.

select * from price_2;



insert into price_2 (날짜, 티커, 종가, 거래량)
values
('2021-01-02', '000001', 1300, 1100), -- < 종가, 거래량 부분 없데이트
('2021-01-04', '000001', 1300, 2000) -- < 1월 4일 정보는 없기 때문에, 이것은 insert를 한다고 봄.
as new
on duplicate key update
종가 = new.종가, 거래량 = new.거래량;

select * from price_2;




