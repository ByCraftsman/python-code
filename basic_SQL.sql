-- 쿼리 실행 단축키는 Ctrl + Shift + Enter.
-- 데이터 베이스를 만듦.
create database shop;

-- 데이터 베이스를 만들고 난 후에는, use를 이용하여 사용할 수 있음.
use shop;


-- 열(컬럼)만 정의된 빈 테이블을 만듦.
create table goods   
(
goods_id char(4) not null, -- 열이름, 고정 길이 4 (무조건 길이가 4가 됨.), 널값 X
goods_name varchar(100) not null, -- 열이름, 가변 길이 (최대 100자까지 허용한다는 뜻.), 널값 X
goods_classify varchar(32) not null,
sell_price integer,
buy_price integer,
register_data date,
primary key (goods_id) -- PK는 중복과 NULL 불가, 자동 인덱스 생성, 테이블의 기준점임.
);


-- table에 열을 추가하거나, 삭제하는 방법.
alter table goods add column goods_name_eng varchar(100);
alter table goods drop column goods_name_eng;


-- SQL은 행단위로 데이터를 입력하니까, 8줄이라서 8행을 생성함. 그리고 6개의 사전에 정의한 열에 맞춰서 값을 삽입하였음. 
insert into goods values ('0001', '티셔츠', '의류', 1000, 500, '2020-09-20');
insert into goods values ('0002', '펀칭기', '사무용품', 500, 320, '2020-09-11');
insert into goods values ('0003', '와이셔츠', '의류', 4000, 2800, NULL);
insert into goods values ('0004', '식칼', '주방용품', 3000, 2800, '2020-09-20');
insert into goods values ('0005', '압력솥', '주방용품', 6800, 5000, '2020-01-15');
insert into goods values ('0006', '포크', '주방용품', 500, NULL, '2020-09-20');
insert into goods values ('0007', '도마', '주방용품', 880, 790, '2020-04-28');
insert into goods values ('0008', '볼펜', '사무용품', 100, NULL, '2020-11-11');

-- 실무에서는 이런 식으로 사용한다.
/* insert into goods (goods_id, goods_name, goods_classify, sell_price, buy_price, register_data)
values
('0009', '마우스', '사무용품', 1200, 800, '2020-12-01');
*/

-- select를 이용하여 3가지의 열을 goods 테이블에서 가져옴.
SELECT 
    goods_id, goods_name, buy_price
FROM
    goods;


-- 테이블의 모든 열을 불러오는 법.    
SELECT * from goods;


-- 열 이름이 길 경우 as를 이용하여 짧게 불러올 수 있음.
select goods_id as id,
	goods_name as name,
	buy_price as price
from goods;


-- select로 상수 및 계산식도 작성이 가능함.
select '상품' as category, -- 상수
    38 as num,            -- 상수
    '2022-01-01' as date, -- 상수 
    goods_id,
    goods_name,
    sell_price,
    buy_price,
    sell_price - buy_price as profit -- 계산식
from goods;


-- 고유값만 확인하고 싶을 때 사용함.
select distinct goods_classify
from goods;


-- 엑셀의 필터와 비슷하다고 보면 됨. '의류'라는 값만 찾아옴.
-- WHERE: 행 필터링
select goods_name, goods_classify
from goods
where goods_classify = '의류';
-- 전체 열
select *
from goods
where goods_classify = '의류';

-- where에서 profit을 못쓰는 이유는 벌명이 쿼리를 모두 실행한 후 부여하는 것이라서 그런 것임.
-- 정확하게는 SELECT 절은 WHERE 이후에 논리적으로 실행되기 때문에, SELECT에서 정의한 alias는 WHERE에서 참조할 수 없다.
-- alias(별칭)는 컬럼이나 테이블에 “임시 이름”을 붙이는 것임. SQL이 실행되는 동안만 쓰이고, 실제 테이블 구조가 바뀌지는 않는다.
select *, sell_price - buy_price as profit
from goods
where sell_price - buy_price >= 500;

select goods_name, goods_classify, sell_price
from goods
where sell_price >= 1000;

select goods_name, goods_classify, register_data
from goods
where register_data < '2020-09-27';


-- 복수 조건은 where에 and나 or을 사용해서 사용함.
select goods_name, goods_classify, sell_price
from goods
where goods_classify = '주방용품'
and sell_price >= 3000;

select goods_name, goods_classify, sell_price
from goods
where goods_classify = '주방용품'
or sell_price >= 3000;


select * from goods;
-- 카운트를 이용해서 테이블의 행의 갯수를 확인할 수 있음.
select count(*)
from goods;

-- 이렇게 특정 열을 선택하면 널 값을 제외해서 반환함.
select count(buy_price)
from goods;


-- 기초적인 함수 사용법.
select sum(sell_price), sum(buy_price)
from goods;

select avg(sell_price)
from goods;

select count(distinct goods_classify) as cnt
from goods;


-- 그룹 바이의 기초적 사용.
select goods_classify, count(*)
from goods -- 사용할 테이블
group by goods_classify;

-- 그룹 바이는 NULL도 나오는 것을 볼 수 있다.
select buy_price, count(*)
from goods
group by buy_price;

-- where을 사용하여, 특정 (의류) 데이터에서 그룹바이를 사용할 수 있다.
select buy_price, count(*)
from goods
where goods_classify = '의류'
group by buy_price;

-- having을 쓰는 이유는, where은 group by 이전에 적용되고, having은 group by 이후에 적용 되기 때문임.
-- 연산 순서의 차이가 존재하기 때문에 반드시 숙지해둬야 함. -- HAVING: 그룹 필터링
select goods_classify, avg(sell_price)
from goods
group by goods_classify
having avg(sell_price) >= 2500;


-- 오더 바이는 기본적으로 오름차순으로 정렬함.
select *
from goods
order by sell_price;
-- 내림차순으로 정렬.
select *
from goods
order by sell_price desc;

select goods_name,
       sell_price - buy_price as profit
from goods
order by profit desc;



-- 여기서 연산 순서를 확실히 하도록 하자.
/*
1. FROM
2. WHERE
3. GROUP BY
4. HAVING
5. SELECT
6. ORDER BY
*/


-- 뷰는 데이터를 저장하지 않고, 내부적으로 쿼리를 실행해서 일시적인 가상 테이블을 생성함.
-- 즉, 데이터가 아니라 쿼리를 저장하고 있음. 때문에 데이터가 갱신되면 뷰의 결과 역시 자동으로 갱신됨.
create view GoodSum (goods_classify, cnt_goods) -- GoodSum이라는 뷰를 생성함.
as
select goods_classify, count(*)
from goods
group by goods_classify;

-- 아래의 코드로 뷰를 조회하면, 위에 작성된 쿼리가 실행되어서 결과가 보인다고 생각하면 됨.
select * from goodsum;

-- 드랍으로 뷰를 제거해도 되고, 왼쪽의 SCHEMAS에서 직접 제거해도 됨.
drop view goodsum;

-- 서브쿼리는 쿼리 내의 쿼리임. 일종의 일회용 뷰를 의미함.
-- 뷰를 정의하는 구문을 그대로 다른 구안에 산입하는 것이라고 보면 됨.
-- 스칼라 서브쿼리는 단일 값이 반환되는 서브쿼리임. 이를 통해 = > < 등 비교 연산자의 입력값으로 사용할 수 있음.
select avg(sell_price)
from goods;

select * from goods
where sell_price > (select avg(sell_price) -- <--(select avg(sell_price) from goods) 이 부분이 서브쿼리임.
from goods);

select goods_id, goods_name, sell_price,
	(select avg(sell_price) from goods) as avg_price  -- <-- (select avg(sell_price) from goods) 마찬가지.
from goods;




