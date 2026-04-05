use stock_db;

create table kor_value
(
종목코드 varchar(6),
기준일 date,
지표 varchar(3),
값 double,
primary key (종목코드, 기준일, 지표)
);

select * from kor_value
where 종목코드 = '005930';

-- 중복 검증
select 종목코드, 기준일, 지표, count(*) as cnt
from kor_value
where 종목코드 = '005930'
group by 종목코드, 기준일, 지표
having count(*) > 1;