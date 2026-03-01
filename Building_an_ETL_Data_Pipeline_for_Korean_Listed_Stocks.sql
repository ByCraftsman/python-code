create database stock_db;

use stock_db;

/*
DECIMAL (고정 소수점)	FLOAT (부동 소수점)이다.
decimal은 정확성(10진수 기반)이 중요할 떄 사용하고, 약간의 오차를 감안하고 효율성를 중시할때는 float (2진수 기반)를 사용한다.
재무 실무와 금융 시스템 설계에서 DECIMAL을 사용하는 것은 무조건적인 기본 원칙이다.
*/
create table kor_ticker
(
    종목코드 varchar(6) not null, #국내주식의 티커는 6자리임.
    종목명 varchar(20),
    시장구분 varchar(6),
    종가 float,  
    시가총액 float,
    기준일 date,
    EPS float,
    선행EPS float,
    BPS float,
    주당배당금 float,
    종목구분 varchar(5),
    primary key(종목코드, 기준일)
);

select * from kor_ticker;



use stock_db;

create table kor_sector
(
    IDX_CD varchar(3),
    CMP_CD varchar(6),
    CMP_KOR varchar(20),
    SEC_NM_KOR varchar(10),
    기준일 date,
    primary key(CMP_CD, 기준일)
);

select * from kor_sector;




