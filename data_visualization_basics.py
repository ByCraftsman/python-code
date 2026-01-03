#이 코드는 plt, pd, sns을 이용하여 기본적인 데이터 시각화를 하는 방법을 다룬다.

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

#===========matplotlib를 이용한 데이터 시각화==========================
#matplotlib은 한글 폰트 지원안해서, rc로 지정이 필요함.
#rc는 실행 시 적용되는 전역 설정(run commands)을 뜻함.
plt.rc('font', family = 'Malgun Gothic') 

df = sns.load_dataset('penguins')

#산점도 그리기
plt.scatter(df['flipper_length_mm'], df['body_mass_g'])

#species를 groupby하여 바디 매스의 평균을 구함.
df.groupby('species')['body_mass_g'].mean()
#그래프를 그릴때는 x축 y축이 필요하므로, 아래의 방식으로 인덱스를 초기화 시켜야 한다.
df_group = df.groupby('species')['body_mass_g'].mean().reset_index()
df_group

#df_group로 bar 그래프 그리기
plt.bar(x=df_group['species'], height=df_group['body_mass_g'])

#히스토그램 그리기
plt.hist(df['body_mass_g'], bins = 10)

#하나의 그래프에 관한 코드는 전부 같이 실행해야함.
plt.hist(df['body_mass_g'], bins = 30)
plt.xlabel('Body mass')
plt.ylabel('Count')
plt.title('펭권의 몸무게 분포')




#==========실업자 데이터 가져와서 그래프 만들기==========================
#https://fred.stlouisfed.org/series/UNRATE 에서 실업자 데이터 받아옴.
df_unrate = pd.read_excel(
    r"C:\Users\minec\OneDrive\바탕 화면\파이썬 엑셀파일\UNRATE.xlsx", sheet_name='Monthly'
)

df_unrate.info()
#그래프 그리기
plt.plot(df_unrate['observation_date'], df_unrate['UNRATE'])




#=====================================================================================
#API(Application Programming Interface)는 라이브러리가 제공하는 사용 방법(인터페이스)임.
#matplotlib에서는 object-oriented (OO) api로 직접 figure와 axes를 지정하는 객체지향적인 방법.
#그리고 stateful api로 '현재의 figure와 axes'에 그림을 그리는 방법이 있다.

#=========OO API=================
fig, axes = plt.subplots(2, 1, figsize=(10, 6))
axes[0].scatter(df['flipper_length_mm'], df['body_mass_g'])
axes[0].set_xlabel('날개 길이(mm)')
axes[0].set_ylabel('몸무게(g)')
axes[0].set_title('날개와 몸무게간의 관계')

axes[1].hist(df['body_mass_g'], bins=30)
axes[1].set_xlabel('Body Mass')
axes[1].set_ylabel('Count')
axes[1].set_title('펭귄의 몸무게 분포')

#그래프 간격 조정. trial and error하면서 적당하게 맞추면 됨.
plt.subplots_adjust(left=0.25,
                    right=1,
                    bottom=0.1,
                    top=0.95,
                    wspace=0.5,
                    hspace=0.5)

#================stateful API================
plt.figure(figsize=(10, 6))
#2,1,1는 2행, 1열 1번째 그래프라는 뜻
plt.subplot(2, 1, 1)
plt.scatter(df['flipper_length_mm'], df['body_mass_g'])
plt.xlabel('날개 길이(mm)')
plt.ylabel('몸무게(g)')
plt.title('날개와 몸무게간의 관계')

plt.subplot(2, 1, 2)
plt.hist(df['body_mass_g'], bins=30)
plt.xlabel('Body Mass')
plt.ylabel('Count')
plt.title('펭귄의 몸무게 분포')

plt.subplots_adjust(left=0.25,
                    right=1,
                    bottom=0.1,
                    top=0.95,
                    wspace=0.5,
                    hspace=0.5)




#===============pandas를 이용한 데이터 시각화==============
df2 = sns.load_dataset('diamonds')

df2.plot.scatter(x='carat', y='price', figsize=(10, 6), title='캐럿과 가격 간의 관계')

#c = 'cut'는 cut별로 color 구분한다는 의미.
df2.plot.scatter(x = 'carat', y = 'price', c = 'cut')

#cmap를 이용하면 더 정확하게 구분할 수 있음.
df2.plot.scatter(x = 'carat', y = 'price', c = 'cut', cmap = 'Set2')

#히스토그램
df2['price'].plot.hist(bins = 20)

#color별로 그룹을 나눠서, carat의 평균을 구함. 그것을 바로 막대 그래프로 그림. 
#판다스를 이용하면 이런 방식으로 데이터 분석과 시각화를 한줄로 작성할 수도 있음.
df2.groupby('color')['carat'].mean().plot.bar()




#===============seaborn을 이용한 데이터 시각화==============
df3 = sns.load_dataset('titanic')

#hue는 색깔, style은 모양임. 즉, 'class'기준으로 색깔과 모양을 구분하라는 뜻.
sns.scatterplot(data = df3, x = 'age', y = 'fare',
                hue = 'class', style = 'class')


df3_pivot = df3.pivot_table(index='class',
                          columns='sex',
                          values='survived',
                          aggfunc='mean',
                          )
df3_pivot

#========피벗 테이블의 시각화=================
sns.heatmap(df3_pivot)
#annot=True -> 값이 나옴. cmap으로 더 직관적으로 색상을 바꿀 수 있음.
sns.heatmap(df3_pivot, annot=True, cmap='coolwarm')




#===displot의 사용법 (figure-level 분할. replot, catplot도 figure-level)=====
sns.displot(data = df3, x = 'age', hue = 'class', kind = 'hist')
sns.displot(data = df3, x = 'age', hue = 'class', kind = 'hist', alpha = 0.3)
sns.displot(data = df3, x = 'age', col ='class', kind = 'hist')
sns.displot(data = df3, x = 'age', row ='class', kind = 'hist')
sns.displot(data = df3, x = 'age', col = 'class', row ='sex', kind = 'hist')




#====axes-level의 그래프 그리기=============
g, axes = plt.subplots(2, 1, figsize=(8, 6))
sns.histplot(data=df3, x='age', hue='class', ax=axes[0])
sns.barplot(data=df3, x='class', y='age', ax=axes[1])

axes[0].set_title('클래스 별 나이 분포도')
axes[1].set_title('클래스 별 평균 나이')

#그래프 간격 맞추기
g.tight_layout()











