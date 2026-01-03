import seaborn as sns

df = sns.load_dataset('penguins')

"""melt함수는 ID 변수를 기준으로 원본 데이터프레임의 '열 이름'들을 variable 열에,
해당 열에 있던 데이터 값은 value열에 넣어, 행이 아주 많은 형태가 됨.
이와 같이 variable이라는 열이 생성되고, 그곳에 원래 열 이름들이 들어감.
그리고 열 이름들의 값들은 value라는 새로운 열에 들어가게 됨."""
df.melt(id_vars=['species', 'island']).head(15)


"""pivot_table은 데이터를 요약(summary)해서 행(index)과 열(columns)의 
교차 지점마다 특정 값(values)을 집계(aggfunc)한 결과를 테이블 형태로 만드는 기능임.

엑셀의 피벗 테이블과 개념이 거의 동일하며,
내부적으로는 groupby + aggregation + reshape가 결합된 연산이라고 볼 수 있다."""

#df.pivot_table을 이용하여 테이블을 생성할 수 있음.
df_pivot_1 = df.pivot_table(index='species',
                            columns='island',
                            values='bill_length_mm',
                            aggfunc='mean')

#인덱스나 밸류를 여러개 입력도 가능함
df_pivot_2 = df.pivot_table(index=['species', 'sex'],
                            columns='island',
                            values=['bill_length_mm', 'flipper_length_mm'],
                            aggfunc=['mean', 'count'])

df_pivot_3 = df.pivot_table(index=['species', 'sex'],
                            columns='island',
                            values='bill_length_mm',
                            aggfunc='mean')



#열 인덱스를 행 인덱스로 변환
df_pivot_3.stack()
#행 인덱스를 열 인덱스로 변환
df_pivot_3.unstack()

#stack method를 사용하면 series형태가 됨. 변환하고 싶으면 .to_frame()
type(df_pivot_3.stack())
type(df_pivot_3.stack().to_frame())




#numpy를 이용한 연산
import numpy as np
bill_length_mm = df['bill_length_mm']

#이런식으로 간단하게 연산 가능.
result = bill_length_mm.apply(np.sqrt)

#define으로 함수 만들어서 사용 가능
def mm_to_cm(num):
    return num / 10
result_2 = bill_length_mm.apply(mm_to_cm)


#최대값 구하기
df_num = df[['bill_length_mm', 'bill_depth_mm',
             'flipper_length_mm', 'body_mass_g']]

#각 열의 최대값
df_num.apply(max, axis=0)
#각 행의 최대값
df_num.apply(max, axis=1)




#groupby의 사용법
df_group = df.groupby(['species']) 
df_group.head(5)
#이렇게 숫자만 설정해야 됨. island와 sex가 문자열이라서.
df_group.mean(numeric_only=True)
#복수도 가능
df.groupby(['species', 'sex']).mean(numeric_only=True)

#최대 최소의 편차
def min_max(x):
    return x.max() - x.min()

df.groupby(['species'])['bill_length_mm'].agg(min_max)

#드룹별 최대값과 최소값 같이 계산
df2 = df.groupby('species')[df.select_dtypes(include='number').columns].agg(['max','min'])

#열마다 다른 함수도 적용 가능. length는 최대, 최소, island는 수.
df.groupby(['species']).agg({'bill_length_mm': ['max', 'min'],
                            'island': ['count']})

#z_sore를 구하는 법.
def z_score(x):
    z = (x - x.mean()) / x.std()
    return(z)

#transform은 원래 행(row) 개수를 그대로 유지한 채로 결과를 반환함.
df.groupby(['species'])['bill_length_mm'].transform('mean')
df.groupby('species')['bill_length_mm'].transform(min)
df.groupby(['species'])['bill_length_mm'].transform(z_score)

#apply는 그룹별로 함수를 적용하고, 함수가 반환하는 것에 따라 결과 형태가 자유롭게 바뀜.
df.groupby(['species'])['bill_length_mm'].apply('mean')
df.groupby(['species'])['bill_length_mm'].apply(min)
df.groupby(['species'])['bill_length_mm'].apply(z_score)




#시계열 데이터 다루기
import pandas as pd
df3 = sns.load_dataset('taxis')
df3.info()

#필요시 datetime으로 변환 (Data type이 시계열이여야 분석 가능함.)
df3['pickup'] = pd.to_datetime(df3['pickup'])

#데이터 연도 추출
df3['pickup'][0].year
df3['pickup'][0].month
df3['pickup'][0].day

df3['pickup'].dt.year
df3['pickup'].dt.month
df3['pickup'].dt.day


#데이터 정렬
df3.sort_values('pickup', inplace=True)
#인덱스 초기화
df3.reset_index(drop=True, inplace=True)

#열끼리의 계산도 가능함.
df3['dropoff'] - df3['pickup']

#pickup열을 행 인덱스로 변환함.
df3.set_index('pickup', inplace=True)

#DatetimeIndex 기반 시계열 인덱싱임. (리스트 형태 아님)
df3.loc['2019-02']
df3.loc['2019-03-01']
#날짜 범위 슬라이싱(양 끝 포함)
df3.loc['2019-03-01' : '2019-03-02']

#range를 이용하여 특정 주기의 데이터를 추출할 수 있음.
pd.date_range(start='2021-01-01',
              end='2021-12-31',
              freq='M')

pd.date_range(start='2021-01-01',
              end='2021-01-31',
              freq='3D')
#매주 월요일
pd.date_range(start='2021-01-01',
              end='2021-01-31',
              freq='W-MON')

#WOM = Week Of Month (월의 몇 번째 주). 아래는 2번째 주 목요일
pd.date_range(start='2021-01-01',
              end='2021-12-31',
              freq='WOM-2THU')








