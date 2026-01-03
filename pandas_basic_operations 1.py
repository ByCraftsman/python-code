import pandas as pd
#pandas는 Series, DataFrame, 벡터 연산, 시계열 처리를 제공한다.
#때문에 데이터분석에 아주 유용하다.


dict_data = {'a':1,'b':2, 'c':3}
#{}는 key–value mapping, 집합의 의미를 가짐. 
#그렇기 때문에 딕셔너리는 순서가 중요하지 않음.

#Series는 index(라벨)를 가진 1차원 배열임. 
#때문에 라벨을 정렬한 후, 그것을 시계열 데이터 분석하기에 유용함.
series = pd.Series(dict_data) # pd.Series, 대문자써야함.
series.index
series.values




#list로도 series를 만들 수 있음.
list_data = ['a', 'b', 'c']
#[]는 배열 원소 접근할 때 쓰는 표기법. 그렇기 때문에 순서가 존재함.
#list에 위치개념이 있어서 이것으로 Series를 만들면 인덱스를 자동으로 부여한다.
series2 = pd.Series(list_data)
series2

#list의 인덱스 이름을 바꾸는 방법은 다음과 같음.
series3 = pd.Series(list_data, index=['AA', 'BB', 'CC'])
series3




#{}가 딕셔너리니까, 이것은 딕셔너리 기반으로 Series를 만든 거다.
capital = pd.Series({'Korea': 'Seoul',
                     'Japan': 'Tokyo',
                     'China': 'Beijing',
                     'USA': 'Washington, D.C.',
                     'India': 'New Delhi',
                     'Taiwan': 'Taipei'})

capital
capital['Korea']
#pandas에서는 복수개를 가져올 때 리스트로 감싸야 한다.
capital[['Japan', 'India']]
capital[['Korea', 'China', 'USA']]




#Series는 사칙연산이 가능하다.
series_1 = pd.Series([1,2,3])
series_2 = pd.Series([4,5,6])

series_1 + series_2
series_1*10
series_2**2




#다수의 Series를 공통 index 기준으로 정렬한 것은 DataFrame이다. 
#하나의 Series가 하나의 Column을 이루고, Index의 개수만큼 행이 형성됨.
#pandas에서는 딕셔너리형태는 열기준이고, 리스트형태는 행기준으로 되어있음.
#pandas에서 행(row)은 index, 열(column)은 columns이다.
dict_data2 = {'col1':[1,2,3],'col2':[4,5,6],'col3':[7,8,9]}
df = pd.DataFrame(dict_data2)
df

df2 = pd.DataFrame([[1,2,3],[4,5,6],[7,8,9]])
df2




#데이터프레임 행렬의 기본 조작
df3 = pd.DataFrame([[1,2,3],[4,5,6],[7,8,9]],
                   index=['index1','index2','index3'],
                   columns=['col1','col2','col3'])
df3

df3.index = ['행수정1','행수정2','행수정3']
df3

df3.columns = ['열수정1','열수정2','열수정3']
df3

#특정 하나의 행, 열 이름을 바꾸는 법.
df3.rename(index={'행수정1':'특정행1'}, inplace=True)
df3.rename(columns={'열수정3':'특정열3'}, inplace=True)
df3

#행, 열의 삭제법. axis=0이 행이고 1이 열임.
df3.drop('특정행1', axis=0, inplace=True)
df3.drop('특정열3', axis=1, inplace=True)
df3



#loc과 iloc의 기본적인 사용
dict_data4 = {'col1': [1, 2, 3, 4], 'col2': [5, 6, 7, 8],
             'col3': [9, 10, 11, 12], 'col4': [13, 14, 15, 16]}
df4 = pd.DataFrame(dict_data4, index=['index1', 'index2', 'index3', 'index4'])
df4

#[]로 하면 Series
df4['col1']
type(df4['col1'])

#[[]]는 DataFrame 형태로 추출됨
df4[['col1']]
type(df4[['col1']])

#DataFrame은 복수도 가능
df4[['col1', 'col2']]


#loc과 iloc은 “행/열을 동시에 지정할 수 있는 인덱싱 도구 (인덱서)”임.
#loc은 인덱스 이름으로, iloc은 위치 인덱스로 사용함.
df4.loc['index1']
df4.iloc[0]

#Data Frame 형태도 마찬가지로 [[]]
df4.loc[['index2']]
df4.iloc[[1]]

#주의해야 할 점은. 슬라이싱할 때, loc은 마지막 값을 포함하나, iloc은 제외함.
df4.loc['index1': 'index3']
df4.iloc[0:2]



#이런 식으로 여러방법으로 사용 가능함
df4.loc['index1', 'col1']
df4.loc['index3', 'col4']
df4.loc[['index2', 'index3'], ['col1', 'col3']] 
df4.loc['index1':'index2', 'col1':'col3']

df4.iloc[0, 0]
df4.iloc[[0, 2], [0, 3]]
df4.iloc[0:2, 0:3]



#pandas로 엑셀이나 csv파일을 간단히 불러오거나 저장할 수 있다.
#sheet_name = 는 특정 시트를 불러옴. 이것을 지정 안하면 첫번째 시트를 불러옴.
data_excel = pd.read_excel(
    r"C:\Users\minec\OneDrive\바탕 화면\파이썬 엑셀파일\판다스 연습용 kospi 자료.xlsx")
data_excel

#파일을 파이썬으로 저장도 가능 (경로는 파이썬 우상단에서 확인.)
data_excel.to_excel('데이터_파이썬으로_저장하기.xlsx')









