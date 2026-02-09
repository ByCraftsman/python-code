
use stock_db;

-- 전종목 시계열 정보 적제
create table kor_price
(
    날짜 date,
    시가 double,
    고가 double,
    저가 double,
    종가 double,
    거래량 double,
    종목코드 varchar(6), -- 국내주식 코드는 6자리.
    -- 같은 날짜에도 여러 종목코드가 있고, 같은 종목코드도 여러 날짜에 해당하는 데이터가 있음.
    primary key(날짜, 종목코드) 
);

-- 기본적인 뼈대가 만들어 진것을 확인가능.
select * from kor_price;


-- 데이터가 잘 들어오는 지 확인용
select distinct(종목코드) from kor_price;

select count(distinct(종목코드)) from kor_price;




-- 전종목 재무제표 정보 적제
use stock_db;

create table kor_fs
(
    계정 varchar(30),
    기준일 date,
    값 float,
    종목코드 varchar(6),
    공시구분 varchar(1),
    primary key(계정, 기준일, 종목코드, 공시구분)
)

select * from kor_fs;












