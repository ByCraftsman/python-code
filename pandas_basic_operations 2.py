#seaborn은 데이터를 통계적으로 보기 좋게 시각화하는 그래프 도구이다.
#pandas DataFrame과 호환성이 좋고, matplotlib보다 쉽게 빠르게 그래프 제작 가능.
#그렇기 때문에 금융 데이터 분석(손실분포, 상관관계, 리스크 분석)에 최적화됨.
import seaborn as sns
df = sns.load_dataset('titanic')
df.head()
df.tail()
df.shape

#info로 null값 수 확인가능
df.info()

#밸류 수를 보는 방법
df['sex'].value_counts()
df[['sex', 'survived']].value_counts()

#비율로 직관적으로 보는 방법.
df[['sex', 'survived']].value_counts(normalize=True)
df[['sex', 'survived']].value_counts(normalize=True).sort_index()

#평균, 중앙값
df['survived'].mean()
df[['survived', 'age']].mean()
df['fare'].min()
df['fare'].max()
df['fare'].median()


df.head().isnull()
df.head().notnull()


#null이 있는 모든 행 or 열을 삭제
df.dropna()
df.dropna(axis = 1)

#age 기준으로 널이 있는 행을 삭제함.
df.dropna(subset = ['age'], axis = 0)

#threshold를 설정해서, 데이터의 수가 적은 것은 삭제함.
#deck의 non-null은 203이므로, 204로 설정하면 제외됨.
df.info()
df.dropna(axis = 1, thresh=204)




#null값을 특정 열의 평균값으로 대체.
df2 = df.copy()
df2.head(6)

mean_age = df2['age'].mean()
mean_age

df2['age'] = df2['age'].fillna(mean_age)
df2.head(6)

#데이터 값을 채우기. f->앞, b->뒤 값 기준으로 채움.
df2['deck_ffill'] = df2['deck'].ffill()
df2['deck_bfill'] = df2['deck'].bfill()
df2[['deck', 'deck_ffill', 'deck_bfill']].head(12)




#인덱스 다루기
df3 = sns.load_dataset('mpg')
#인덱스를 'name'열로 대체
df3.set_index('name', inplace = True)
#오름차순으로 정렬
df3.sort_index(inplace = True)
#내림차순으로 정렬
df3.sort_index(inplace = True, ascending = False)
#설정된 인덱스를 초기화
df3.reset_index(inplace = True)

#중복되지 않는 값들만 반환
df3['cylinders'].unique()

#실린더 수가 4인 것들만 필터링
filter_bool = (df3['cylinders'] == 4)
df3.loc[filter_bool, ]

#이런 식으로 여러 조건을 사용해서 필터링할 수 있음
filter_bool_2 = (df3['cylinders'] == 4) & (df3['horsepower'] >= 100)
df3.loc[filter_bool_2, ['cylinders', 'horsepower', 'name']]

#name 열에서 특정 차들만 뽑는 법.
filter_bool_3 = (df3['name'] == 'ford maverick') | (
    df3['name'] == 'ford mustang ii') | (df3['name'] == 'chevrolet impala')
df3.loc[filter_bool_3]
#isin method로 하면 더 간단히 작성 가능.
filter_isin = df3['name'].isin(
    ['ford maverick', 'ford mustang ii', 'chevrolet impala'])
df3.loc[filter_isin]

#이러한 방식으로 새로운 열을 만들 수 있음.
df3['ratio'] = df3['mpg'] / df3['weight'] * 100




#numpy는 기초 수치 계산 엔진이다. 숫자 계산은 거의 numpy에 의존한다.
#벡터, 행렬 연산 같은 수치 계산과 다차원 배열(N-dimensional array) 지원함.
#numpy를 이용하여 엑셀의 if함수와 유사하게 사용하여 열을 만들 수 있다.
import pandas as pd
import numpy as np

num = pd.Series([-2, -1, 1, 2])
#해당 조건의 위치를 말함
np.where(num >= 0)
#if 함수라고 보면 됨
np.where(num >= 0, '양수', '음수')
#이러한 식으로 새로운 열을 조건에 따라 구분하여 만들 수 있음.
df3['horse_power_div'] = np.where(
    df3['horsepower'] < 100, '100 미만', 
    np.where((df3['horsepower'] >= 100) & (df3['horsepower'] < 200), '100 이상 200 미만',
             np.where(df3['horsepower'] >= 200, '200 이상', '기타')))







