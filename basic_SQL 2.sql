use shop;

create table SampleMath
(m  numeric (10,3),  -- 전체 10자리에서, 소수점은 3자리까지
 n  integer,
 p  integer);
 
insert into SampleMath(m, n, p) values (500, 0, NULL);
insert into SampleMath(m, n, p) values (-180, 0, NULL);
insert into SampleMath(m, n, p) values (NULL, NULL, NULL);
insert into SampleMath(m, n, p) values (NULL, 7, 3);
insert into SampleMath(m, n, p) values (NULL, 5, 2);
insert into SampleMath(m, n, p) values (NULL, 4, NULL);
insert into SampleMath(m, n, p) values (8, NULL, 3);
insert into SampleMath(m, n, p) values (2.27, 1, NULL);
insert into SampleMath(m, n, p) values (5.555,2, NULL);
insert into SampleMath(m, n, p) values (NULL, 1, NULL);
insert into SampleMath(m, n, p) values (8.76, NULL, NULL);

select * from samplemath;

-- 절대값 구하기
select m, abs(m) as abs_m
from SampleMath;

-- n/p의 나머지 구하기
select n, p, mod(n, p) as mod_col
from SampleMath;

-- m열을 소수 n번째짜리까지 반올림하기
select m, n, round(m, n) as round_col
from SampleMath;


-- 문자 데이터를 처리할 때 사용되는 문자열 함수 사용법
create table SampleStr
(str1  varchar(40),
 str2  varchar(40),
 str3  varchar(40));

insert into SampleStr (str1, str2, str3) values ('가나다', '라마', NULL);
insert into SampleStr (str1, str2, str3) values ('abc', 'def', NULL);
insert into SampleStr (str1, str2, str3) values ('김', '철수', '입니다');
insert into SampleStr (str1, str2, str3) values ('aaa', NULL, NULL);
insert into SampleStr (str1, str2, str3) values (NULL, '가가가', NULL);
insert into SampleStr (str1, str2, str3) values ('@!#$%', NULL,	NULL);
insert into SampleStr (str1, str2, str3) values ('ABC',	NULL, NULL);
insert into SampleStr (str1, str2, str3) values ('aBC',	NULL, NULL);
insert into SampleStr (str1, str2, str3) values ('abc철수', 'abc', 'ABC');
insert into SampleStr (str1, str2, str3) values ('abcdefabc','abc', 'ABC');
insert into SampleStr (str1, str2, str3) values ('아이우', '이','우');

select * from samplestr;

-- concat 함수는 여러 열의 문자열을 연결할 때 사용됨.
-- null 이 있으면 null을 반환한다.
select str1, str2, concat(str1, str2) as str_concat
from SampleStr;

-- 대소문자로 변환
select str1, lower(str1) as low_str
from SampleStr;

select str1, upper(str1) as low_str
from SampleStr;

-- replace는 대상 문자열, 치환할 문자열, 반환될 문자열의 형태이다
select str1, str2, str3,
	replace(str1, str2, str3) as rep_str
from SampleStr;

-- 현재 날짜나 시간을 다루는 함수는 from 구문 없이 사용 가능.
-- DB 서버 기준 시간으로 적용됨.
select current_date, current_time, current_timestamp;

-- 이런식으로 일부분 추출 가능함.
select
    current_timestamp,
    extract(year from current_timestamp) as year,
    extract(month from current_timestamp) as month,
    extract(day	from current_timestamp) as day,
    extract(hour from current_timestamp) as hour,
    extract(minute from current_timestamp) as minute,
    extract(second from current_timestamp) as second;


create table SampleLike
(strcol varchar(6) not null,
primary key (strcol));

insert into SampleLike (strcol) values ('abcddd');
insert into SampleLike (strcol) values ('dddabc');
insert into SampleLike (strcol) values ('abdddc');
insert into SampleLike (strcol) values ('abcdd');
insert into SampleLike (strcol) values ('ddabc');
insert into SampleLike (strcol) values ('abddc');

select * from samplelike;

-- like 술어는 문자열 중 부분 일치를 검색할 때 사용됨.
-- 전방일치
select *
from samplelike
where strcol like 'ddd%';

-- 중간일치는 모든 ddd
select *
from SampleLike
where strcol like '%ddd%';

-- 후방일치
select *
from SampleLike
where strcol like '%ddd';


-- between은 범위 검색을 수행함.
select *
from goods
where sell_price between 100 and 1000;

-- null은 비교가 불가능한 특별한 표시어라서 등호를 못쓰고, is, is not을 써야함.
select *
from goods
where buy_price is null;

select *
from goods
where buy_price is not null;

-- 이런 나열식의 쿼리는 효율성이 떨어짐.
select *
from goods
where buy_price = 320 
	or buy_price = 500
	or buy_price = 5000;

-- in 술어를 사용하면 이렇게 간단하게 조건을 작성할 수 있음.
select *
from goods
where buy_price in (320, 500, 5000);

select *
from goods
where buy_price not in (320, 500, 5000);


select goods_name, sell_price,
	case when sell_price >=  6000 then '고가'    
		 when sell_price >= 3000 and sell_price < 6000 then '중가'
         when sell_price < 3000 then '저가'
		 else null -- 필수는 아니지만 있는 게 좋음. 실무에서는 else '기타' 또는 '미분류' 이런 식으로 자주 씀.
end as price_classify -- 열 이름 지정.
from goods;


-- union은 세로로 붙이는 방식임 (행추가). 열 개수, 열 타입, 순서가 완전히 동일해야함.
-- union은 중복되는 건 제거하고 합치고, union all은 그냥 합침. 실무적으로는 union all정도만 사용됨.
CREATE TABLE Goods2
(goods_id CHAR(4) NOT NULL,
 goods_name VARCHAR(100) NOT NULL,
 goods_classify VARCHAR(32) NOT NULL,
 sell_price INTEGER,
 buy_price INTEGER,
 register_date DATE,
 PRIMARY KEY (goods_id));

insert into Goods2 values ('0001', '티셔츠' ,'의류', 1000, 500, '2020-09-20');
insert into Goods2 values ('0002', '펀칭기', '사무용품', 500, 320, '2020-09-11');
insert into Goods2 values ('0003', '와이셔츠', '의류', 4000, 2800, NULL);
insert into Goods2 values ('0009', '장갑', '의류', 800, 500, NULL);
insert into Goods2 values ('0010', '주전자', '주방용품', 2000, 1700, '2020-09-20');

select *
from goods
union
select *
from goods2;

select *
from goods
union all
select *
from goods2;


-- INNER JOIN: 양쪽 테이블에 모두 존재하는 행만 반환.
-- OUTER JOIN: 한쪽 테이블의 행을 기준으로, 매칭되지 않는 경우 NULL로 채워 반환.
-- 교집합과 합집합으로 이해하는 건 엄밀히 말하면 틀림. 
-- OUTER JOIN LEFT는 A, B가 있으면 A, RIGHT는 B값이 전부 나오는 거임.
CREATE TABLE StoreGoods
(store_id CHAR(4) NOT NULL,
 store_name VARCHAR(200) NOT NULL,
 goods_id CHAR(4) NOT NULL,
 num INTEGER NOT NULL,
 PRIMARY KEY (store_id, goods_id));

insert into StoreGoods (store_id, store_name, goods_id, num) values ('000A', '서울',	'0001',	30);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000A', '서울',	'0002',	50);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000A', '서울',	'0003',	15);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000B', '대전',	'0002',	30);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000B',' 대전',	'0003',	120);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000B', '대전',	'0004',	20);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000B', '대전',	'0006',	10);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000B', '대전',	'0007',	40);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000C', '부산',	'0003',	20);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000C', '부산',	'0004',	50);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000C', '부산',	'0006',	90);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000C', '부산',	'0007',	70);
insert into StoreGoods (store_id, store_name, goods_id, num) values ('000D', '대구',	'0001',	100);

select * from storegoods;
select * from goods; -- 전에 만든 goods 테이블 참조

-- 엑셀의 vlookup과 비슷함. INNER JOIN은 가장 많이 쓰는 방법임.
select *
from storegoods as store
inner join goods as goods
on store.goods_id = goods.goods_id;

-- 이런식으로 2개의 테이블에서 원하는 열들만 선택해서 INNER JOIN할 수도 있음.
select store.store_id, store.store_name, store.goods_id, goods.sell_price, goods.buy_price
from storegoods as store
inner join goods as goods
on store.goods_id = goods.goods_id;

-- OUTER JOIN의 사용.
-- storegoods는 5, 8이 없음을 알 수 있음.
select distinct(goods_id) from StoreGoods;
select distinct(goods_id) from Goods;

-- 5, 8이 NULL로 채워지는 것을 볼 수 있음.
select store.store_id, store.store_name, goods.goods_id,
	goods.goods_name, goods.sell_price
from StoreGoods as store 
right outer join Goods as goods -- 오른쪽 테이블에 해당하는 goods는 모두 출력
	on store.goods_id = goods.goods_id;

-- 5, 8이 없는 것을 볼 수 있음.
select store.store_id, store.store_name, goods.goods_id,
	goods.goods_name, goods.sell_price
from StoreGoods as store 
left outer join Goods as goods -- 왼쪽 테이블에 해당하는 storegoods는 모두 출력
	on store.goods_id = goods.goods_id;
    
    
    
-- goods_classify열로 나누고, sell_price로 정렬함. rank() over로 랭킹을 구하고, ranking이라는 열을 생성함.
-- partition by를 통해 구분된 행 집합을 '왼도우'라고 표현하며, 범위를 나타냄.
select goods_name, goods_classify, sell_price,
	rank() over (partition by goods_classify order by sell_price) as ranking
from Goods;
-- partition by 없어도 사용이 가능하기는 함. 더 세세하게 정렬이 안되기는 하지만 .
select goods_name, goods_classify, sell_price,
	rank () over (order by sell_price) as ranking
from Goods; 

/*
왼도우 전용 함수
rank는 같은 순위인 행이 복수개 있으면 후순위를 건너뜀. ex. 1위,1위,1위,4위
dense_rank는 같은 순위인 행이 복수개 있어도 후순위를 건너뛰지 않음. ex. 1위,1위,1위,2위
row_number는 순위와 상관없이 연속 번호를 부여함. ex. 1위,2위,3위,4위
*/ 
select goods_name, goods_classify, sell_price,
	rank() over (order by sell_price) as ranking,
    dense_rank() over (order by sell_price) as ranking,
    row_number() over (order by sell_price) as ranking
from Goods;


-- sum이나 avg와 같은 집약 함수도 윈도우 함수로 사용이 가능함.
select goods_id, goods_name, sell_price,
	sum(sell_price) over() as current_sum
from Goods;

-- order by로 정렬해서 누적합계를 구할 수 있음.
select goods_id, goods_name, sell_price,
	sum(sell_price) over(order by goods_id) as current_sum
from Goods;

-- 비슷한 논리로 누적평균도 구할 수 있음.
select goods_id, goods_name, sell_price,
	avg(sell_price) over(order by goods_id) as current_sum
from Goods;

-- 윈도우 별로 구하기.
select goods_id, goods_classify, goods_name, sell_price,
	sum(sell_price) over(partition by goods_classify order by goods_id) as current_sum
from Goods;

-- 이동평균도 구할 수 있음. rows 2 preceding은 현재 행과 위의 2개의 행을 말함.
select goods_id, goods_classify, goods_name, sell_price,
	avg(sell_price) over(order by goods_id rows 2 preceding) as moving_avg
from Goods;

-- rows between current row and 2 following은, 현재 행과 아래의 2개의 행을 말함.
select goods_id, goods_classify, goods_name, sell_price,
	avg(sell_price) over(order by goods_id rows between current row and 2 following) as moving_avg
from Goods;

-- rows between 1 preceding and 1 following는 현재 행과 위 아래 행을 말함.
select goods_id, goods_classify, goods_name, sell_price,
	avg(sell_price) over(order by goods_id
    rows between 1 preceding and 1 following)
    as moving_avg
from goods;














