import pandas as pd
from ckonlpy.tag import Twitter
from pykospacing import Spacing
import streamlit as st

"""
사용자가 입력한 단어가 있는 데이터를 csv에서 불러와 반환
"""

def tokenWord(keyword) :
    """
    사용자가 입력한 단어를 형태소 단위로 자르고 사이에 %를 삽입하여 DB에서 검색할 수 있도록 변환
    ...
    parameters
        keyword : 검색할 단어 (str)
    ...
    returns
        tokenized_word : 형태소 단위로 정제된 단어 (list)
    """
    
    twitter = Twitter()
    spacing = Spacing()

    #외래어 읽어오기
    loanwords = pd.read_csv('loanwords.txt', encoding = 'cp949')
    loanwords = loanwords['word'].tolist()
    for word in loanwords :
        twitter.add_dictionary(word, 'Noun')

    #불용어제거 + 토큰화 + %
    kospacing_word = spacing(keyword) # 띄워쓰기 보완
    tokenized_word = twitter.morphs(kospacing_word) # 토큰화
    
    return tokenized_word


@st.cache(allow_output_mutation=True)
def getData(df, tokenized_word) :
    """
    csv에서 검색 단어가 포함된 데이터를 불러오고 dataFrame 생성 
    ...
    parameters
        df : 전체 데이터가 저장되어 있는 df (dataFrame; shape[n,4])
        tokenized_word : 형태소 단위로 정제된 단어 (list)
    ...
    returns
        df : 해당 단어가 포함된 데이터가 담긴 데이터프레임 (dataFrame; shape[n,4])
    """

    #reac_csv 과정에서의 오류 방지
    df['title'] = df['title'].astype(str)
    df['hashtag'] = df['hashtag'].astype(str)
    
    df_title = df[df['title'].map(lambda x: all(tt in x for tt in tokenized_word))]     # title에 해당 단어가 있는 값만 추출
    df_hash = df[df['hashtag'].map(lambda x: all(tt in x for tt in tokenized_word))]    # hashtag에 해당 단어가 있는 값만 추출

    df = pd.concat([df_title, df_hash], axis=0)         #두 데이터를 합침
    df = df.drop_duplicates(['url'])                    #url을 기준으로 중복 데이터 삭제

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


def main(keyword, df) :
    tokenized_word = tokenWord(keyword)

    df = getData(df, tokenized_word)

    df = dropIrrel(df) 

    return df
    

if __name__ == '__main__':
    keyword = input('keyword: ')
    table = input('table: ')
    df = main(keyword, table)