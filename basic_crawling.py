
"""
크롤링은 브라우저를 거치지 않고 HTTP 요청을 직접 보내 웹 서버로부터 웹 문서 (HTML, JSON 등) 를 자동 수집하는 과정이다.

인코딩이란 문자를 특정 숫자(code point)로 매핑하고, 이를 바이트로 표현하는 과정이다. 이것의 반대 과정은 디코딩임.
한글이 포함된 엑셀이나 CSV 파일을 불러오거나 한글로 된 데이터를 크롤링하면, 오류가 뜨거나 읽을 수 없는
 문자로 나타나는 경우가 있는데, 이는 한글 인코딩 때문에 발생하는 문제이며 흔히 '인코딩이 깨졌다'라 함.

EUC-KR, CP949 (EUC-KR의 확장형) 는 한국어 환경에서 사용되던 인코딩이며,
UTF-8은 전 세계 언어를 하나의 문자 집합으로 통합한 유니코드 인코딩 방식이다.
현재 웹과 파이썬, 대부분의 시스템에서는 UTF-8이 표준으로 사용된다.

다시 언급하자면, utf8mb4는 mySQL에서만 사용하는 것이고, mySQL에서의 utf8mb4이 실질적으로 UTF-8과 같다.

HTTP 요청 방식의 종류는 GET, POST, PUT, DELETE가 있으나, 크롤링에서는 실질적으로 앞의 2개만 사용된다.
GET은 URL에 파라미터를 포함해 데이터를 요청하는 방식이고, POST는 요청 본문(body)에 데이터를 담아 전송하는 방식임.
POST 요청은 URL 변화가 없으므로, 개발자도구(Network 탭)를 통해 확인해야 한다.


크롤링 하기에 앞서서, HTML과 CSS에 대한 기본적인 지식은 필요하다.
HTML의 요소는:

      <p align="center">ㅁㄴㅇㄹ</p>
<태그이름 속성명="속성값">내용</종료태그> 형태라고 보면 된다.

자세한 내용은 https://www.w3schools.com/html/default.asp

ul (unordered list) 태그는 순서가 없는 리스트, ol (ordered list) 태그는 순서가 있는 리스트다.
table 태그는 표를 만드는 태그다. tr태그는 각 행을 의미한다. th태그는 진하게 표현. td는 셀을 의미함.
a태그와 img는 속성과 결합해서 사용됨. a는 href 속성과 결합하여, a href="링크", img src="이미지 링크"
img src는 단독 태그라서 닫는 태그가 없다. div태그는 의미 없는 블록 컨테이너로, 레이아웃이나 영역 구분에 사용된다.

CSS는 웹페이지를 꾸며주는 역할을 한다.
"""




#requests는 웹 서버에 HTTP 요청을 보내고 원시 응답 데이터를 수신하는 라이브러리임.
#브라우저가 하는 일 중 "네트워크 통신 계층”만 구현한 라이브러리다.
import requests as rq
url = 'https://quotes.toscrape.com/' 
quote = rq.get(url)
quote  #2XX는 응답이 정상적으로 처리되었하는 뜻.
quote.content # 서버에서 받은 원시 바이트(bytes). 때문에 이것으로 데이터 수집은 불편함.




#BeautifulSoup는 웹 스크래핑 및 데이터 추출을 위한 라이브러리임.
from bs4 import BeautifulSoup
"""
모든 데이터는 사용하기 위해 파싱이 필요하며, HTML은 구조가 없는 문서이기 때문에 전용 파싱 도구가 필요함.
Python 환경에서는 BeautifulSoup이 표준적인 HTML 파싱 도구로 사용됨. 파싱(Parsing)이란 받아온 원시 데이터에서 
내가 원하는 정보만 추출하는 과정임. 참고로 JSON은 response.json()하는 것 자체가 파싱이다.
"""
quote_html = BeautifulSoup(quote.content, 'html.parser')  #BeautifulSoup 객체로 불러옴.
quote_html

#명언에 해당하는 부분을 추출해봄.
#개발자 도구를 보면 div태그에 class가 'quote'임을 알 수 있음. class가 아니라 class_해야함.
quote_div = quote_html.find_all('div', class_='quote')
quote_div[0]

#여기서 글 부분만 보면, span 태그에 class가 text인 것을 알 수 있다.
quote_span = quote_div[0].find_all('span', class_='text')
quote_span

#완전 택스트만 추출하는 방법은 .text를 하면 된다.
quote_span2 = quote_div[0].find_all('span', class_='text')[0].text
quote_span2

# 1페이지의 모든 명언 택스트만 추출하기.
[i.find_all('span', class_ ='text')[0].text for i in quote_div]




#만약 데이터가 존재하는 곳이 태그를 여러번 찾아 내려가야 할 경우에는 방금까지 사용한 find.all은 번거로울 수 있음.
#select (CSS Selector 방식) 함수는 좀 더 쉬운 방법으로 원하는 데이터가 존재하는 태그를 입력할 수 있음.
#해당 방식은 구조를 한 줄로 표현할 수 있고 유지보수 용이하기 때문에 실무에서 선호함.
quote_text = quote_html.select('div.quote > span.text')
quote_text 
[i.text for i in quote_text]
quote_text_list = [i.text for i in quote_text] 

#명언을 말한 사람들만 추출.
quote_author = quote_html.select('div.quote > span > small.author')
[i.text for i in quote_author]
quote_author_list = [i.text for i in quote_author]

#about 부분의 링크 추출.
quote_link = quote_html.select('div.quote > span > a')   #a=anchor
quote_link
#속성값의 경우 HTML 정보 뒤에 [속성]을 하면 추출할 수 있음.
quote_link[0]['href']   #hypertext reference
#이렇게 리스트 내포 형태로 추출하면 뒤에 링크 부분이 없으므로,
[i['href'] for i in quote_link]     
#이렇게 앞에다가 붙여서 처리할 수도 있다.
['https://quotes.toscrape.com' + i['href'] for i in quote_link]




#이번에는 종합해서 데이터를 각 100개씩 뽑아서 데이터프레임을 만들어봄.
import time
import pandas as pd

text_list = []
author_list = []
infor_list = []

for i in range(1, 100):

    url_ = f'https://quotes.toscrape.com/page/{i}/'
    quote = rq.get(url_)
    quote_html = BeautifulSoup(quote.content, 'html.parser')

    quote_text = quote_html.select('div.quote > span.text')
    quote_text_list = [i.text for i in quote_text]

    quote_author = quote_html.select('div.quote > span > small.author')
    quote_author_list = [i.text for i in quote_author]
    
    quote_link = quote_html.select('div.quote > span > a')
    quote_link_list = ['https://quotes.toscrape.com' + i['href'] for i in quote_link]

    if len(quote_text_list) > 0:  #데이터가 특정 개수 이상인가할 때 쓰임.

        text_list.extend(quote_text_list)
        author_list.extend(quote_author_list)        
        infor_list.extend(quote_link_list)        
        time.sleep(1) 

    else:
        break

quotes = pd.DataFrame({'text': text_list, 'author': author_list, 'infor': infor_list})




#예외처리를 넣은 버전임. 비교해보면 알다시피 처음부터 try except로 짜는 게 좋음.
#for 문의 암묵적 전제가 '모든 반복이 성공한다'이기 때문에 처음부터 try문으로 작성하는 게 맞음.
text_list2 = []
author_list2 = []
infor_list2 = []

for i in range(1, 100):

    url__ = f'https://quotes.toscrape.com/page/{i}/'

    try:
        response = rq.get(url__, timeout=5) #5초안에 응답없으면 예외처리
        response.raise_for_status() #HTTP 상태 코드(status code)가 에러면 예외처리

        quote_html2 = BeautifulSoup(response.content, 'html.parser')

        quote_text2 = quote_html2.select('div.quote > span.text')
        quote_author2 = quote_html2.select('div.quote > span > small.author')
        quote_link2 = quote_html2.select('div.quote > span > a')

        if not quote_text2:
            break

        text_list2.extend([q.text for q in quote_text2])
        author_list2.extend([a.text for a in quote_author2])
        infor_list2.extend(['https://quotes.toscrape.com' + l['href'] for l in quote_link2])

        time.sleep(1)

    except rq.exceptions.RequestException as e:
        print(f'Page {i} skipped due to request error: {e}')
        continue

quotes2 = pd.DataFrame({'text': text_list2, 'author': author_list2,'infor': infor_list2})





#네이버 페이 증권 실시간 속보 제목 추출
url2 = 'https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258'
fn_data = rq.get(url2)
fn_html = BeautifulSoup(fn_data.content, 'html.parser')
fn_html_select = fn_html.select('dl > dd.articleSubject > a') #제목 부분 경로

fn_html_select[0]['title'] #제목 부분의 속성 이름이 'title'임. 

[i['title'] for i in fn_html_select] #리스트 내포로 제목 부분만 추출.




#테이블 형태는 데이터는 HTML 정보를 불러온 후 태그와 속성을 찾을 필요 없이,
#pandas.read_html()로 손쉽게 불러올 수 있음.
#pandas.read_html은 내부적으로 HTTP 요청을 보내는데, User-Agent가 없어 일부 사이트에서 차단될 수 있다.
#예전에는 이 방식으로 되었지만, 현재는 위키피디아가 차단을 해서 안된다.
url3 = 'https://en.wikipedia.org/wiki/List_of_countries_by_stock_market_capitalization'
tables = pd.read_html(url3)

#차단이 되지 않으려면 '브라우저 처럼 보여야'한다.
#HTTP 헤더는 택배 상자의 취급 주의 딱지처럼, 통신의 성격과 처리 방식을 알려주는 메타데이터다.
url3 = "https://en.wikipedia.org/wiki/List_of_countries_by_stock_market_capitalization"

headers = {
    "User-Agent": "Mozilla/5.0" #모질라는 현대 웹 브라우저처럼 보이기 위한 관용적인 식별자임.
}

response = rq.get(url3, headers=headers)
pd_html = response.text
tables = pd.read_html(pd_html)





#지금까지 get 방식으로 데이터를 불러왔기 때문에, 이번에는 post 방식으로 데이터를 불러와보도록 함
#post 방식에서는 개발자도구에서 headers창에 나타나는 Request URL를 입력해야한다.
url4 = 'https://kind.krx.co.kr/disclosure/todaydisclosure.do'   #기업공시채널 KIND
#payload를 입력할 때는 값이 없는 항목은 입력할 필요가 없다. 값이 있는 부분만 딕셔너리 형태로 입력하면 된다.
payload = {
    'method': 'searchTodayDisclosureSub',
    'currentPageSize': '15',
    'pageIndex': '1',
    'orderMode': '0',
    'orderStat': 'D',
    'forward': 'todaydisclosure_sub',
    'chose': 'S',
    'todayFlag': 'Y',
    'selDate': '2025-12-22'
}

kind_data = rq.post(url4, data=payload)    #post 방식이기 때문에 get이 아니라 rq.post다.

kind_html = BeautifulSoup(kind_data.content, 'html.parser')
kind_html #형태를 보면 엑셀 데이터가 HTML 형태로 나타나있음.

#prettify 함수로 beautifulsoup에서 파싱한 파서 트리를 다시 유니코드 형태로 돌려줌.
html_unicode = kind_html.prettify() 
html_unicode

#유니코드 형태가 되면 다시 간단하게 데이터 추출이 가능함.
pd.read_html(html_unicode)
kind_table = pd.read_html(html_unicode)























