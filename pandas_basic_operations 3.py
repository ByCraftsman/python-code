import pandas as pd
#데이터 프레임을 합치는 방법
df1 = pd.DataFrame({
    "A": ["A0", "A1", "A2", "A3"],
    "B": ["B0", "B1", "B2", "B3"],
    "C": ["C0", "C1", "C2", "C3"],
    "D": ["D0", "D1", "D2", "D3"]
},
    index=[0, 1, 2, 3],
)

df2 = pd.DataFrame({
    "A": ["A4", "A5", "A6", "A7"],
    "B": ["B4", "B5", "B6", "B7"],
    "C": ["C4", "C5", "C6", "C7"],
    "D": ["D4", "D5", "D6", "D7"]
},
    index=[4, 5, 6, 7],
)

df3 = pd.DataFrame({
    "A": ["A8", "A9", "A10", "A11"],
    "B": ["B8", "B9", "B10", "B11"],
    "C": ["C8", "C9", "C10", "C11"],
    "D": ["D8", "D9", "D10", "D11"]
},
    index=[8, 9, 10, 11],
)

result = pd.concat([df1, df2, df3])
result




#concat의 사용법
df4 = pd.DataFrame({
    "B": ["B2", "B3", "B6", "B7"],
    "D": ["D2", "D3", "D6", "D7"],
    "F": ["F2", "F3", "F6", "F7"]
},
    index=[2, 3, 6, 7]
)

result = pd.concat([df1, df4])
result

#인덱스를 초기화함
result = pd.concat([df1, df4], ignore_index=True)

#axis=1는 열기준으로 합침.
result = pd.concat([df1, df4], axis=1)

#기본형은 합집합이고, 이너 조인을 하게 되면 교집합 형태로 합침.
result = pd.concat([df1, df4], axis=1, join="inner")

#시리즈를 하나 만들어서 이러한 방식으로 데이터 프레임에 추가가능.
s1 = pd.Series(["X0", "X1", "X2", "X3"], name="X")
result = pd.concat([df1, s1], axis=1)
result




#merge의 사용법
left = pd.DataFrame({
    "key": ["K0", "K1", "K2", "K3"],
    "A": ["A0", "A1", "A2", "A3"],
    "B": ["B0", "B1", "B2", "B3"]
})


right = pd.DataFrame({
    "key": ["K0", "K1", "K3", "K4"],
    "C": ["C0", "C1", "C3", "C4"],
    "D": ["D0", "D1", "D3", "D4"],
})

#key기준으로 교집합 합병함.
result2 = pd.merge(left, right, on="key")
result2

#기준을 left나 right의 데이터 프레임으로도 설정할 수 있음.
#기준이 되지 못한 것은 합병될 때 데이터 손실이 가능함.
#outer로 설정하면 합집합으로 합병되기 때문에 데이터 손실이 없음.
result2 = pd.merge(left, right, on="key", how='left')
result2
result2 = pd.merge(left, right, on="key", how='right')
result2
result2 = pd.merge(left, right, on="key", how='outer')
result2

#기준열의 이름이 서로 다른 경우의 데이터 처리
left2 = pd.DataFrame({
    "key_left": ["K0", "K1", "K2", "K3"],
    "A": ["A0", "A1", "A2", "A3"],
    "B": ["B0", "B1", "B2", "B3"]
})


right2 = pd.DataFrame({
    "key_right": ["K0", "K1", "K3", "K4"],
    "C": ["C0", "C1", "C3", "C4"],
    "D": ["D0", "D1", "D3", "D4"],
})

#key_left와 right의 값을 기준으로 교집합 해봄.
result3 = pd.merge(left2, right2, left_on='key_left',
                  right_on='key_right', how='inner')

result3 = left2.merge(right2, left_on='key_left',
                    right_on='key_right', how='inner')




#join method는 행 인덱스를 기준으로 데이터를 결합한다.
join_left = pd.DataFrame({
    "A": ["A0", "A1", "A2", "A3"],
    "B": ["B0", "B1", "B2", "B3"]},
    index=["K0", "K1", "K2", "K3"]
)


join_right = pd.DataFrame({
    "C": ["C0", "C1", "C3", "C4"],
    "D": ["D0", "D1", "D3", "D4"]},
    index=["K0", "K1", "K3", "K4"])

#join_left 값을 기준으로 join
join_result = join_left.join(join_right)



























