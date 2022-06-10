import pandas as pd
from tqdm import tqdm
from tensorflow.keras.preprocessing.text import Tokenizer
import re
from ckonlpy.tag import Twitter
from pykospacing import Spacing
from collections import Counter


def tokenWord(keyword) :
    """
    사용자가 입력한 단어를 형태소 단위로 잘라서 반환
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
    clean_word = '%'
    kospacing_word = spacing(keyword) # 띄워쓰기 보완
    tokenized_word = twitter.morphs(kospacing_word) # 토큰화
    
    return tokenized_word


def rmEmoji(inputData):
    """
    텍스트에서 이모지 제거
    ...
    parameters
        inputData : 텍스트 (str)
    ...
    returns
        data : 이모지가 제거된 텍스트 (str)
    """

    emoji_pattern = re.compile("["
        u"\U00010000-\U0010FFFF"  #BMP characters 이외
            "]+", flags=re.UNICODE)

    data = emoji_pattern.sub(r'', inputData) # no emoji

    return data

def nlpData(df) :
    """
    1. 데이터 띄워쓰기 보완
    2. 데이터 이모지&불용어 제거
    3. 토큰화
    ...
    parameters
        df : DB에서 가져온 데이터가 담긴 데이터프레임 (dataFrame; shape[n,4])
        tokenized_word : 검색 단어를 형태소 단위로 자른 리스트 (list)
    ...
    returns
        tokenizer : tokenizer
    """

    # 모든 타이틀 제목을 연결해서 하나의 텍스트 문서로 만들려 함
    titles = df['title'].tolist()

    twitter = Twitter()
    spacing = Spacing()

    #불용어 읽어오기
    stopwords = pd.read_csv("stopwords.txt")
    stopwords = stopwords['word'].tolist()
    stopwords.extend([',', '.', '+', '[', ']', '!', '?', '(', ')', '|', '_', '~', '#', '/'])

    #외래어 읽어오기
    loanwords = pd.read_csv('loanwords.txt', encoding = 'cp949')
    loanwords = loanwords['word'].tolist()
    for word in loanwords :
        twitter.add_dictionary(word, 'Noun')

    #불용어제거 + 토큰화
    tks = []
    for sentence in tqdm(titles) :
        reEmoji_sent = rmEmoji(sentence) # 이모티콘 제거
        kospacing_sent = spacing(reEmoji_sent) # 띄워쓰기 보완
        tokenized_sent = twitter.morphs(kospacing_sent) # 토큰화
        stopwords_removed_sentence = [word for word in tokenized_sent if not word in stopwords] # 불용어 제거
        tks.append(stopwords_removed_sentence)

    #토큰화된 단어들을 다시 한 문장으로 만들어주기
    clean_sentences = []
    for tk in tks :
        clean_sentences.append(" ".join(tk))

    # 정수 인코딩
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(tks)

    return tokenizer


def counting(tokenizer, tokenized_word) :
    """
    토큰화한 단어 중 가장 많이 나온 단어 15개를 뽑아 딕셔너리형태로 반환
    ...
    parameters
        tokenizer : 토크나이저
    returns
        words : 상위 15단어의 딕셔너리 타입 (dict; (text : count_num))
    """
    
    #상위 20개 추출
    top20 = Counter(tokenizer.word_counts).most_common(20)

    words = []
    for top in top20 :

        if top[0] in tokenized_word :
            continue #검색어 제거
        else:
            words.append(dict(text=top[0], value=top[1])) #연관어만 딕셔너리화

    return words

def main(keyword, df) :
    tokenized_word = tokenWord(keyword)

    tokenizer = nlpData(df)

    words = counting(tokenizer, tokenized_word)

    return words