#파이썬 하나의 리스트는 행도 열도 아니다. 그냥 데이터가 일렬로 나열된 형태.
var = [1, 2, 3]

for i in var:
    print(i)


var = [10, 15, 17, 20]

for i in var:
    if i % 2 == 0:     # %는 나머지임.
        print(f'{i}는 짝수입니다.')
    else:
        print(f'{i}는 홀수입니다.')
        
        
#범위
for i in range(5):
    print(i)



#append. <- a는 변하지 않고, 그것을 기반으로 수정된 값을 result에 반환.
a = [1, 2, 3]

result = []

for i in a:
    result.append(i**2)

print(result)


#리스트 컴프리헨션 방식 (축약형)
result = [i**2 for i in a]
result



#익셉트 연습
number = [1, 2, 3, "4", 5]
for i in number:
    print(i ** 2)
#i가 정수(int)일때만 가능. 문자열(str)은 안됨.
#파이썬에서 문자열은 제곱 연산을 숫자와 같이 못 함.


for i in number:
    try:
        print(i ** 2)
    except:
        print('Error at : '+i)
#+는 문자열끼리 열결할때 사용함. 


#함수 연습
def f(x):
    y = x + 1
    return y

f(3)
f(5)


def f2(x):
    res = x**(1/2)
    return res

f2(4)
f2(16)
f2(25)

#변수 2개
def multiply(x, y):
    res = x**y
    return res

multiply(x = 3, y = 4)
multiply(2, 5)
        

#변수 상수는 이렇게 섞음
def divide(x, n=2):
    res = x/n
    return(res)

divide(6)
divide(6, 3)    #n를 다시 설정할 수도 있음.
divide(10, 2)




#람다는 익명 함수(anonymous function)를 만드는 문법.
#즉, 함수 이름 없이 함수를 만들 수 있다.

#람다 사용법
#함수명 = lambda 매개변수1, 매개변수2, ...: statement
divide_lam =lambda x, n: x/n       #즉, x, n은 매개변수, x/n은 statement.
divide_lam(10, 2)
divide_lam(20, 5)
#보면 알다시피 return 없이 반환함.











