from urllib.request import urlopen
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import warnings
import re
import psycopg2


"""
키워드를 입력받아 유튜브에서 추천순으로 상위 약 150개(스크롤다운 50번)를 크롤링하고 DB에 적재함
"""

def getPage(driver, keyword) :
    """
    1. 키워드를 입력받아 유튜브에 검색
    2. 필터 1년 내 업로드로 설정
    3. 스크롤 다운 50번 진행
    ...
    parameters
        driver : 크롬 드라이버
        keyword : 검색하고자 하는 단어 (str)
    ...
    returns
        driver : 1~3번이 진행된 크롬 웹페이지
    """

    # 키워드를 검색한 유튜브 주소 접속
    url = 'https://www.youtube.com/results?search_query={}'.format(keyword)
    driver.get(url)

    #사이트 최대화
    driver.maximize_window()

    # 필터 클릭
    driver.find_element_by_xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[1]/div[2]/ytd-search-sub-menu-renderer/div[1]/div/ytd-toggle-button-renderer/a/tp-yt-paper-button').click()
    time.sleep(1)

    # 구분 -> 동영상 클릭
    driver.find_element_by_xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[1]/div[2]/ytd-search-sub-menu-renderer/div[1]/iron-collapse/div/ytd-search-filter-group-renderer[2]/ytd-search-filter-renderer[1]/a/div/yt-formatted-string').click()

    # 업로드 날짜 -> 올해 클릭
    driver.find_element_by_xpath('/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[1]/div[2]/ytd-search-sub-menu-renderer/div[1]/iron-collapse/div/ytd-search-filter-group-renderer[1]/ytd-search-filter-renderer[5]/a').click()

    # 스크롤 다운 50번 실행
    body = driver.find_element_by_tag_name('body')
    body.send_keys(Keys.PAGE_DOWN)

    for i in range(1,50):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    return driver


def getHashtag(hashtag_list, outline_test) :
    """
    유튜브 영상 설명란에서 해시태그만 가져오는 함수
    ...
    parameters
        hashtag_list : 영상 별 해시태그가 담길 리스트 (list)
        outline_test : 유튜브 영상 설명 전문 (str)
    ...
    returns
        None
    """
    # hash_tag가 안달려있는 영상이 있기 때문에 오류 방지
    try:
        hash_tag = " ".join(re.findall("#[가-힣]{1,}", outline_test)) #설명 전문에서 #@@@으로 표현된 단어만 가져옴
        print(hash_tag)
        hashtag_list.append(hash_tag)
            
    except Exception as e:
        hash_tag = ""
        print(hash_tag)
        hashtag_list.append(hash_tag)


def getInfo(driver) :
    """
    유튜브 영상 별 제목과 url, 업로드일, 해시태그를 받아오는 함수
    ...
    parameters
        driver : 크롬 드라이버
    ...
    returns
        name_list : 영상제목 리스트 (list)
        url_list : 영상주소 리스트 (list)
        day_list : 업로드일 리스트 (list)
        hashtag_list : 해시태그 리스트 (list)
    """

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    name = soup.select('a#video-title')
    video_url = soup.select('a#video-title')

    video_num_list = [] #영상번호
    name_list = [] #영상제목
    url_list = [] #영상주소

    for i in range(len(name)):
        #영상번호 카운트
        video_num_list.append(i+1)
        #영상제목 가져오기
        name_list.append(name[i].text.strip())

    #영상주소 가져오기
    for i in video_url:
        url_list.append('{}{}'.format('https://www.youtube.com',i.get('href')))

    print('영상 개수: ', len(name_list))

    day_list = [] #업로드일
    hashtag_list = [] #해시태그

    for i in range(0,len(url_list)):
        
        if url_list[i].split('/')[3] == 'shorts':  #쇼츠

            print(i+1, ': 쇼츠', end=' ')

            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'html.parser')
            
            driver.get(url_list[i])

            time.sleep(2)

            #더보기 클릭
            driver.find_element_by_xpath('/html/body/ytd-app/div[1]/ytd-page-manager/ytd-shorts/div[1]/ytd-reel-video-renderer[1]/div[2]/ytd-reel-player-overlay-renderer/div[2]/div[1]/ytd-menu-renderer/yt-icon-button/button/yt-icon').click()
            time.sleep(2)

            #설명 클릭
            driver.find_element_by_xpath('/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-menu-popup-renderer/tp-yt-paper-listbox/ytd-menu-service-item-renderer/tp-yt-paper-item').click()
            time.sleep(2)

            #업로드일 정보 가져오기
            day = driver.find_element_by_id("publish-time").text.split(':')[1].strip()

            print(day)
            day_list.append(day)

            time.sleep(2) 

            # 해시태그 가져오기
            outline_test = driver.find_element_by_class_name("style-scope ytd-reel-description-sheet-renderer").text
            getHashtag(hashtag_list, outline_test)

        else :
            print(i+1, ': 일반', end=' ')

            driver.get(url_list[i])
                
            time.sleep(2)    

            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'html.parser')

            time.sleep(2)  

            #업로드일 정보 가져오기
            #day = soup.select('#formatted-snippet-text > span:nth-child(3)')[0].text
            day = driver.find_element_by_id("info-strings").text.split('\n')[0]
            
            print(day)
            day_list.append(day)

            time.sleep(2) 

            # 해시태그 가져오기
            outline_test = soup.find("yt-formatted-string", {"class":"content style-scope ytd-video-secondary-info-renderer"}).text    
            getHashtag(hashtag_list, outline_test)

    return name_list, url_list, day_list, hashtag_list


def preDate(day_list) :
    """
    가져온 영상 업로드일 정보를 datetime 형식으로 들어갈 수 있도록 전처리 
    (yyyy. mm. dd -> yyyy-mm-dd)
    ...
    parameters
        day_list : 업로드일 리스트 (list)
    ...
    returns
        day_list2 : 전처리 후 업로드일 리스트 (list)
    """
    day_list2 = [] #전처리 후 업로드일

    #업로드일 날짜형식으로 통일화
    for day in day_list : 
        day = day.replace('.', '')
        day = day.replace('최초 공개: ', '')
        day = day.replace('실시간 스트리밍 시작일: ', '')
        day = day.replace(' ', '-')
        day_list2.append(day)
    
    return day_list2

def makeDf(name_list, day_list2, url_list, hashtag_list) :
    """
    크롤링한 정보를 데이터프레임 형태로 변경
    ...
    parameters 
        name_list : 영상제목 리스트 (list; shape[n])
        url_list : 영상주소 리스트 (list; shape[n])
        day_list2 : 업로드일 리스트 (list; shape[n])
        hashtag_list : 해시태그 리스트 (list; shape[n])
    ...
    returns
        youtubdDf : 영상제목, 영상주소, 업로드일, 해시태그가 담긴 데이터프레임 (dataFrame; shape[n,4])
    """

    youtubeDic = {
        '제목': name_list,
        '업로드일': day_list2,
        '주소': url_list,
        '해시태그' : hashtag_list
    }

    youtubeDf = pd.DataFrame(youtubeDic)

    # datetime 타입으로 변환
    youtubeDf['업로드일'] = pd.to_datetime(youtubeDf['업로드일'])

    # 중복값제거
    youtubeDf = youtubeDf.drop_duplicates(['주소'], keep='first')

    return youtubeDf


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


def loadDB(youtubeDf, table) :
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
    for i in range(len(youtubeDf)) :
        cur.execute(insert_command(table), (youtubeDf.iloc[i][0], youtubeDf.iloc[i][1], youtubeDf.iloc[i][2], youtubeDf.iloc[i][3]))
        conn.commit()

    # DB 연결 종료
    conn.cursor().close()
    conn.close()


def main(keyword) :
    warnings.filterwarnings(action='ignore')
    driver = webdriver.Chrome('C:\chromedriver.exe')

    driver = getPage(driver, keyword)

    name_list, url_list, day_list, hashtag_list = getInfo(driver)

    day_list2 = preDate(day_list)

    youtubeDf = makeDf(name_list, day_list2, url_list, hashtag_list)

    table = input('테이블명: ')
    
    loadDB(youtubeDf, table)

    
if __name__ == '__main__':
    main(input('키워드: '))

