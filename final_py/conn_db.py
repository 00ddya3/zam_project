import psycopg2
import pandas as pd
from ckonlpy.tag import Twitter
from pykospacing import Spacing
import streamlit as st

"""
사용자가 입력한 단어가 있는 데이터를 DB에서 불러와 반환
"""


def tokenWord(keyword) :
    """
    사용자가 입력한 단어를 형태소 단위로 자르고 사이에 %를 삽입하여 DB에서 검색할 수 있도록 변환
    ...
    parameters
        keyword : 검색할 단어 (str)
    ...
    returns
        clean_word : 형태소 단위로 정제된 단어 (str)
    """
    
    twitter = Twitter()
    spacing = Spacing()

    #외래어 읽어오기
    loanwords = pd.read_csv('loanwords.txt', encoding = 'cp949')
    loanwords = loanwords['word'].tolist()
    for word in loanwords :
        twitter.add_dictionary(word, 'Noun')

    #불용어제거 + 토큰화 + %
    clean_word = '%'
    kospacing_word = spacing(keyword) # 띄워쓰기 보완
    tokenized_word = twitter.morphs(kospacing_word) # 토큰화
    for tk in tokenized_word :
        clean_word = clean_word + tk + '%'
    # 여름원피스 -> 여름 원피스 -> ['여름', '원피스'] -> %여름%원피스%
    # 크롭자켓 -> 크롭자켓 -> ['크롭', '자켓'] -> %크롭%자켓%
    
    return clean_word

@st.cache
def getTitleData(table, clean_word) :
    """
    DB에서 검색 단어가 타이틀에 포함된 데이터를 불러오고 dataFrame 생성 
    ...
    parameters
        table : 데이터가 저장되어 있는 DB 내 테이블 명 (str)
        clean_word : 형태소 단위로 정제된 단어 (str)
    ...
    returns
        df : DB에서 가져온 데이터가 담긴 데이터프레임 (dataFrame; shape[n,4])
    """
    #postgresql 접속
    conn_string = "host='localhost' dbname='postgres' user='postgres' password='admin'"
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()

    #데이터 가져오기
    command = "select distinct title, date, url, hashtag from " + table + " where title like '" + clean_word + "'"
    cur.execute(command)
    conn.commit()
    data = cur.fetchall()

    #DF화
    df = pd.DataFrame(data)
    df.columns = ['title', 'date', 'url', 'hashtag']

    #db 연결 종료
    conn.cursor().close()
    conn.close()

    return df


def getHashData(table, keyword) :
    """
    DB에서 검색 단어가 포함된 데이터를 불러오고 dataFrame 생성 
    ...
    parameters
        table : 데이터가 저장되어 있는 DB 내 테이블 명 (str)
        keyword : 검색할 단어 (str)
    ...
    returns
        df : DB에서 가져온 데이터가 담긴 데이터프레임 (dataFrame; shape[n,4])
    """
    #postgresql 접속
    conn_string = "host='localhost' dbname='postgres' user='postgres' password='admin'"
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()

    #데이터 가져오기
    command = "select distinct title, date, url, hashtag from " + table + " where hashtag like '%" + keyword + "%'"
    cur.execute(command)
    conn.commit()
    data = cur.fetchall()

    #DF화
    df = pd.DataFrame(data)
    df.columns = ['title', 'date', 'url', 'hashtag']

    #db 연결 종료
    conn.cursor().close()
    conn.close()

    return df

def dropIrrel(df) :
    """
    컨텐츠의 제목에 관련없는 단어가 포함되어 있는 열을 삭제
    ...
    parameters
        df : DB에서 가져온 데이터가 담긴 데이터프레임 (dataFrame; shape[n,4])
    ...
    returns    
        df : 관련없는 데이터가 빠진 데이터프레임 (dataFrame; shape[n,4])
    """

    #관련 없는 단어 읽어오기
    irrelwords = pd.read_csv('irrelwords.txt')
    irrelwords = irrelwords['word'].tolist()

    #단어가 포함되어 있는 열 삭제
    for word in irrelwords :
        irreldata = df[df['title'].str.contains(word, case = False)].index
        df.drop(irreldata, inplace=True)
    
    return df

def main(keyword, table) :
    clean_word = tokenWord(keyword)

    df_title = getTitleData(table, clean_word)          #title에 검색어가 포함된 데이터
    
    df_hash = getHashData(table, keyword)               #hashtag에 검색어가 포함된 데이터

    df = pd.concat([df_title, df_hash], axis=0)         #두 데이터를 합침

    df = df.drop_duplicates(['url'])                    #url을 기준으로 중복 데이터 삭제

    df = dropIrrel(df)                                  #관련없는 데이터 삭제

    return df
    

if __name__ == '__main__':
    keyword = input('keyword: ')
    table = input('table: ')
    df = main(keyword, table)