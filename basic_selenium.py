from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time



driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


url = 'https://www.naver.com'
driver.get(url)
driver.page_source #html 정보
#브라우저 상에서 보이는 버튼, 검색창, 사진, 테이블, 동영상 등을 엘레먼트라 함.
driver.find_element(By.LINK_TEXT, value = '뉴스').click() #find_element로 쉽게 찾을 수 있음.
driver.back()


#네이버를 기준으로 2023년도와 2025년도에서 클래스명이 꽤나 바뀌어 있음.
#이렇게 종종 바뀌는 경우가 있기 때문에, 유지보수차원에서는 고려를 해야할듯? 
driver.find_element(By.CLASS_NAME, value = 'search_input').send_keys('selenium package') #텍스트 전송
driver.find_element(By.CLASS_NAME, value = 'btn_search').send_keys(Keys.ENTER)
driver.find_element(By.CLASS_NAME, value = 'box_window').clear()

driver.find_element(By.CLASS_NAME, value = 'box_window').send_keys('위치마다 클래스가 바뀜')
driver.find_element(By.CLASS_NAME, value = 'bt_search').click()





#XPATH를 이용해서 접근할 수도 있음. XPATH는 HTML이나 XML 중 특정 값의 태그나 속성을 찾기 쉽게 만든 주소임.
#개발자 도구에서 우클릭 -> Copy -> Copy Xpath 하면 된다.
driver.find_element(By.XPATH, value = '//*[@id="lnb"]/div[1]/div/div[1]/div/div[1]/div[3]/a').click()

#페이지 다운 기능 수행
#''부분은 웹페이지의 가장 하단까지 스크롤을 내리라는 자바스크립트 명령어이다. 
driver.execute_script('window.scrollTo(0, document.body.scrollHeight);') 
# driver.find_element(By.TAG_NAME, value = 'body').send_keys(Keys.PAGE_DOWN) 로도 같은 기능을 수행한다.


#while문으로 페이지를 끝가지 내려보도록 함.
prev_height = driver.execute_script('return document.body.scrollHeight') # 현재의 창 높이를 반환함.

while True:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(5) 
    
    curr_height = driver.execute_script('return document.body.scrollHeight')
    if curr_height == prev_height: #현재 높이가 prev_height와 동일하다면 보통 페이지가 끝까지 내려왔다는 의미.
        break
    prev_height = curr_height #prev_height에 curr_height를 저장함.
    


#이러한 방식으로 selenium으로 웹페이지를 제어한 후, beautifulsoup로 원하는 부분을 추출하면 된다.
driver.quit()
    

"""
실시간 대량 데이터 수집에서 Selenium은 너무 느리기도 하고, 위의 코드들을 보면 알 수 있듯이, 
 제어 대상이 불안정하기 때문에 제한적으로 현업에서 사용된다. 즉, 신뢰성과 유지보수 문제로
가능하면 API 기반 수집을 우선하는 편이다.
"""

    
    
    
    
    
    
    
    
    
    