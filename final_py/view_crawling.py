from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas  as pd 
import psycopg2
from datetime import date, timedelta
import re


"""
키워드를 입력받아 네이버 뷰에서 1년 내에 업로드된 포스트를 크롤링하고 DB에 적재함
"""

def getPage(driver, query_txt) :
    """
    1. 키워드를 입력받아 네이버에 검색
    2. 네이버뷰로 이동 후 필터 1년 내 업로드로 설정
    3. 가능한 곳까지 스크롤 다운
    ...
    parameters
        driver : 크롬 드라이버
        query_txt : 검색하고자 하는 단어 (str)
    ...
    returns
        driver : 1~3번이 실행된 크롬 웹페이지
    """

    #크롬드라이버 실행
    driver.get('http://www.naver.com')
    time.sleep(2)

    #키워드를 검색한 네이버창 접속
    element = driver.find_element_by_id("query")
    element.send_keys(query_txt)
    element.submit()

    # 뷰 클릭
    driver.find_element_by_link_text("VIEW").click()
    time.sleep(2)

    #필터 클릭
    driver.find_element_by_xpath('//*[@id="snb"]/div[1]/div/div[3]/a').click()
    time.sleep(2)

    #기간 1년 설정
    driver.find_element_by_xpath('//*[@id="snb"]/div[2]/ul/li[3]/div/div[1]/a[8]').click()
    time.sleep(3)

        #더이상 스크롤이 안되면 종료
    i = 1
    time.sleep(1)

    #현재 스크롤 위치를 last_height로 받아옴
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        #스크롤 한 번 실행 후 스크롤 위치를 new_height로 받아옴
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        #더이상 스크롤이 안되면 종료
        if new_height == last_height:
            break

        last_height = new_height
        i += 1

    return driver

def getInfo(driver) :
    """
    네이버뷰 포스트 별 제목과 url, 업로드일, 해시태그를 받아오는 함수
    ...
    parameters
        driver : 크롬 드라이버
    ...
    returns
        title2 : 포스트 제목 리스트 (list)
        bdate2 : 포스트 업로드일 리스트 (list)
        url2 : 포스트 주소 리스트 (list)
        hashtag2 : 포스트 해시태그 리스트 (list)
    """
    no2 = [ ]           # 게시글 번호 컬럼
    title2 = [ ]        # 게시물 제목 컬럼
    bdate2 = [ ]        # 작성 일자 컬럼
    url2 = [ ]          # url 컬럼
    hashtag2 = [ ]      # 해시태그 컬럼

    no = 1

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    view_list = soup.find('ul','lst_total').find_all('li')

    for i in view_list :
        
        no2.append(no)                            # 게시물 번호 리스트에 추가

        all_title = i.find_all('a')
        title = all_title[5].get_text( )          # 게시물 제목
        title2.append(title)                      # 게시물 제목 리스트에 추가

        time.sleep(2)

        bdate = i.find('span','sub_time sub_txt').get_text( )  # 작성일자
        bdate.replace('.', '-')
        bdate2.append(bdate)                     # 작성일자 리스트에 추가

        time.sleep(2)

        url = str(all_title[0])
        url = url.split('"')[5]                 # 게시물 url
        url2.append(url)                        # url 리스트에 추가

        time.sleep(2)

        # 카페글은 hashtag가 없다면 댓글을 보여줌
        try :
            outline_test = i.find('div', 'total_tag_area').get_text()    
            
            # hashtag가 안달려있는 블로그 글도 있기때문에 오류 방지
            try:
                hashtag = " ".join(re.findall("#[가-힣]{1,}", outline_test))
                hashtag2.append(hashtag)
                    
            except Exception as e:
                hashtag = ""
                hashtag2.append(hashtag)

        except : 
            hashtag = ""
            hashtag2.append(hashtag)


        if no == 200 : #한번에 200개 까지만 크롤링 가능
            break
            
        no += 1

    return title2, bdate2, url2, hashtag2

def preDate(bdate2) :
    """
    가져온 포스트의 업로드일 정보를 datetime 형식으로 들어갈 수 있도록 전처리 
    (yyyy.mm.dd -> yyyy-mm-dd)
    ...
    parameters
        bdate2 : 업로드일 리스트 (list)
    ...
    returns
        bdate3 : 전처리 후 업로드일 리스트 (list)
    """

    bdate3 = [] #전처리 후 작성일자

    # 작성일자를 날짜형식으로 통일화
    for day in bdate2 :

        if '시간 전' in day :       # n시간 전 업로드 글
            day = date.today()
        elif '분 전' in day :       # n분 전 업로드 글
            day = date.today()
        elif '일 전' in day :       # n일 전 업로드 글 
            day = date.today() - timedelta(int(day[0])) #8일전 글 부터는 날짜로 반환
        elif day == '어제' :        # 어제 업로드 글
            day = date.today() - timedelta(1)
        else :
            day = day.rstrip('.')
            day = day.replace('.', '-')
        
        bdate3.append(day)
    
    return bdate3

def makeDf(title2, bdate3, url2, hashtag2) :
    """
    크롤링한 정보를 데이터프레임 형태로 변경
    ...
    parameters 
        title2 : 포스트 제목 리스트 (list; shape[n])
        bdate2 : 포스트 업로드일 리스트 (list; shape[n])
        url2 : 포스트 주소 리스트 (list; shape[n])
        hashtag2 : 포스트 해시태그 리스트 (list; shape[n])
    ...
    returns
        naver_blog : 포스트 제목, 포스트 주소, 게시일, 해시태그가 담긴 데이터프레임 (dataFrame; shape[n,4])
    """
    # df화
    naver_blog = pd.DataFrame()
    naver_blog['제목'] = title2
    naver_blog['작성일자'] = bdate3
    naver_blog['주소'] = url2
    naver_blog['해시태그'] = hashtag2

    #date-time 타입으로 변환
    naver_blog['작성일자'] = pd.to_datetime(naver_blog['작성일자'])

    print(naver_blog.tail())

    return naver_blog


def insert_command(table) :
    """
    로컬DB에 데이터 삽입
    ...
    parameters
        table : 데이터를 삽입할 테이블명 (str)
    ...
    returns
        command : 삽입 명령문 (str)
    """
    command = 'insert into ' + table + ' (title, date, url, hashtag) values (%s, %s, %s, %s);'
    return command


def loadDB(naver_blog, table) :
    """
    1. 로컬 DB에 접속
    2. 입력받은 테이블에 데이터 삽입
    3. DB 연결 종료
    ...
    parameters
        youtubeDf : DB에 삽입할 데이터 프레임 (dataFrame; shape[n,4])
        table : 데이터를 삽입할 DB에 존재하는 테이블 명 (str)
    ...
    returns
        None
    """
    # DB연결
    conn_string = "host='localhost' dbname='postgres' user='postgres' password='admin'"
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()

    # DB에 데이터 입력
    for i in range(len(naver_blog)) :
        cur.execute(insert_command(table), (naver_blog.iloc[i][0], naver_blog.iloc[i][1], naver_blog.iloc[i][2], naver_blog.iloc[i][3]))
        conn.commit()

    # DB 연결 종료
    conn.cursor().close()
    conn.close()


def main(query_txt) :
    driver = webdriver.Chrome('C:\chromedriver.exe')

    driver = getPage(driver, query_txt)

    title2, bdate2, url2, hashtag2 = getInfo(driver)

    bdate3 = preDate(bdate2)

    naver_blog = makeDf(title2, bdate3, url2, hashtag2)

    table = input('테이블명: ')
    
    loadDB(naver_blog, table)

    
if __name__ == '__main__':
    main(input('키워드: '))