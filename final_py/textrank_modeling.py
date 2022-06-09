import psycopg2
import pandas as pd
import numpy as np
from tqdm import tqdm
import re
from ckonlpy.tag import Twitter
from pykospacing import Spacing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


"""
1. 로컬 DB에서 검색어를 포함하는 데이터를 불러옴
2. 자연어처리
3. TextRank
4. 관련도가 낮은 하위 5개 반환
"""

def tokenWord(keyword) :
    """
    사용자가 입력한 단어를 형태소 단위로 자르고 사이에 %를 삽입하여 DB에서 검색할 수 있도록 변환
    ...
    parameters
        keyword : 검색할 단어 (str)
    ...
    returns
        tokenized_word : 검색 단어를 형태소 단위로 자른 리스트 (list)
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
    
    return tokenized_word, clean_word


def getData(table, clean_word) :
    """
    DB에서 검색 단어가 포함된 데이터를 불러오고 dataFrame 생성 
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


def nlpData(df, tokenized_word) :
    """
    1. 데이터 띄워쓰기 보완
    2. 데이터 이모지&불용어 제거
    3. 토큰화
    4. 검색어 제거
    ...
    parameters
        df : DB에서 가져온 데이터가 담긴 데이터프레임 (dataFrame; shape[n,4])
        tokenized_word : 검색 단어를 형태소 단위로 자른 리스트 (list)
    ...
    returns
        replaced_sentences : 1~4번이 진행된 title열 (list; shape[n])
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

    #정확도를 높이기 위해 검색단어 제거
    replace_sentences = []
    for sent in clean_sentences :
        for tk in tokenized_word :
            sent = sent.replace(tk, '')
        replace_sentences.append(sent)

    return replace_sentences


def tfidfMat(replace_sentences) :
    """
    title수 * title수 의 TF-IDF 상관행렬 만들기
    ...
    parameters
        replace_sentences : title열 (list; shape[n])
    ...
    returns
        text_mat : TF-IDF 상관행렬 (matrix; n*n)
    """

    # title수 * title수 의 빈 행렬 만들기
    n = len(replace_sentences)
    text_mat = np.zeros(shape=(n,n), dtype=np.float64)

    #TF-IDF
    tfidf = TfidfVectorizer(analyzer='word', encoding='utf-8')
    tfidf.fit(replace_sentences)

    #문장의 모든 순서쌍마다 vector 간의 cosine similarity를 구함
    for idxi, i in enumerate(replace_sentences) :
        for idxj, j in enumerate(replace_sentences) :
            # row, col이 같으면 스킵
            if idxi == idxj:
                continue
            
            text_mat[idxi][idxj] = cosine_similarity(tfidf.transform([i]), tfidf.transform([j]))[0][0]

    return text_mat


def TextRank(text_mat) : 
    """
    TextRank 알고리즘 적용
    ...
    parameters
        text_mat : TF-IDF 상관행렬 (matrix; n*n)
    ...
    returns
        TR : title 별 textrank 값이 저장된 리스트 (list, shape[n])
    """
    
    # 인접리스트 방식으로 노드 간의 연결관계 표현
    mat = text_mat.copy()
    output_node = [] # 각 title 별 비슷한 title 번호 리스트의 리스트

    for row in mat: # row : 한 title과 다른 title 간의 코사인유사도 array; shape[28,]
        
        tmp=[] #한 title에 대해 비슷한 title의 번호
        for i in range(len(row) ):
            if row[i]>0.1 : # 다른 title과 유사도가 0.1보다 크다면
                tmp.append(i)

        output_node.append(tmp)

    # 각 title 별 비슷한 title의 수
    for i in range(len(output_node)) :
        print(len(output_node[i]), end=' ')

    d = 0.85 #현실에서 발생하는 예상외의 요인들로 인해 확률이 변동되는 것을 계산하기 위한 damping factor
    initial_tr=1/len(mat) #초기 textrank 값 지정
    TR = [initial_tr]*len(mat)

    history = [] #error 값을 저장하기 위한 변수
    stop = False #while문을 탈출하기 위한 boolean 변수
    step = 0

    # 각 title 별 TR 값 조정
    while stop == False:
        # A,B,C,D를 업데이트할 때 원래값과 수정된 값의 차이의 합
        #error = S_k+1(V_i) + S_k(V_i)
        total_error = 0
        # A,B,C,D를 순회하면서
        for node in range(len(mat)):
            # 초항 : 1-d
            update_val = (1-d)
            tmp = 0
            # A 노드와 연결된 노드 중에서 (B, D)
            for i in output_node[node] :
                s=0
                # B에 연결된 노드의 가중치 합을 S에 저장
                for j in output_node[i] :
                    s+= mat[i][j]
                # TR['B'] * mat[A->B] / sigma(B)
                k=TR[i]*(mat[node][i]/s)
                tmp += k
            # update_val은 기존의 1-d + d*tmp, d=0.85
            update_val +=tmp*d
            # error는 기존값과 update_val의 차이
            error = abs(TR[node] - update_val)
            # total_error에 error를 더해줌
            total_error += error
            TR[node] = update_val

        #만약 error가 e^-10보다 작다면 early stop flag
        if total_error < 1e-10:
            stop = True
        
        history.append(total_error)
        step+=1
        print("step:", step, " error:", total_error)
        if stop == True :
            break
    
    return TR


def showBot5(df, TR) :
    """
    TR값 순으로 정렬하여 하위 5개 print
    ...
    parameters
        df : DB에서 가져온 데이터가 담긴 데이터프레임 (dataFrame; shape[n,4])
        TR : title 별 textrank 값이 저장된 리스트 (list, shape[n])
    ...
    returns
        None    
    """
    #정렬
    ans=[]
    for idx, val in enumerate(TR) :
        ans.append((val, idx))

    # 내림차순 정렬 & 상위 5개 선택
    bot_5 = sorted(ans, reverse=False)[:5]

    titles = df['title'].tolist()

    for idx, i in enumerate(bot_5) :
        print(idx+1, '번째: ', titles[idx])


def main(table, keyword) :
    tokenized_word, clean_word = tokenWord(keyword)

    df = getData(table, clean_word)

    replace_sentences = nlpData(df, tokenized_word)

    text_mat = tfidfMat(replace_sentences)

    TR = TextRank(text_mat)

    showBot5(df, TR)


if __name__ == '__main__':
    main(input('테이블명: '))