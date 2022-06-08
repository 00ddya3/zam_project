import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import warnings
from tqdm import tqdm

from ckonlpy.tag import Twitter
from pykospacing import Spacing

from imblearn.over_sampling import RandomOverSampler
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense, Dropout, LSTM, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, LSTM, Embedding
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


"""
1. DB에 저장된 각 테이블에서 랜덤으로 20%를 추출
2. class 열을 추가해서 엑셀 안에서 직접 관련있음(1), 관련없음(0) 작성
3. 다시 데이터를 파이썬에 불러와 CountVectorizer
4. NaiveBayes 분류모델 실행
5. 피클 파일로 모델 저장
** 3번 이후의 코드만 수록
"""

def getData(table) :
    """
    csv파일을 읽어오고 모델링을 진행할 수 있도록 독립변수와 종속변수 df로 나누어줌
    ...
    parameters
        table : 데이터가 저장되어 있는 DB 테이블명이자 csv명 (str)
    ...
    returns
        dff_x : 독립변수 시리즈 (dataFrame; shape[n,1])
        dff_y : 종속변수 시리즈 (dataFrame; shape[n,1])
    """
    # class 추가된 데이터 가져오기
    df = pd.read_csv('./outputs/' + table + '_class.csv', encoding='cp949')
    
    # 종속변수, 독립변수 분리
    dff_x = df['title']
    dff_y = df['class']

    return dff_x, dff_y


def balancingData(dff_x, dff_y) :
    """
    1. 데이터를 train_data와 test data로 나누어 줌
    2. 데이터 불균형을 처리하기 위해 오버샘플링을 진행함
    ...
    parameters
        dff_x : 독립변수 시리즈 (dataFrame; shape[n,1])
        dff_y : 종속변수 시리즈 (dataFrame; shape[n,1])
    ...
    returns
        X_train : 독립변수 학습데이터 (dataFrame; shape[m, 1])
        X_test : 독립변수 시험데이터 (dataFrame; shape[0.3*n, 1])
        y_train : 종속변수 학습데이터 (dataFrame; shape[m, 1])
        y_test : 종속변수 시험데이터 (dataFrame; shape[0.3*n, 1])
    """
    # 데이터셋 분리
    X_train, X_test, y_train, y_test = train_test_split(dff_x, dff_y, test_size=0.3, random_state=25)

    # 훈련 데이터 오버샘플링
    oversample = RandomOverSampler(sampling_strategy='minority')

    #샘플러에 들어가기 위해 array 타입으로 바꾸기
    X_np_train = np.array(X_train) 
    X_np_train = np.reshape(X_np_train, (len(X_train), 1))
    y_np_train = np.array(y_train)

    # resample
    X_sample_train, y_sample_train = oversample.fit_resample(X_np_train, y_np_train)

    # 다시 시리즈 형태로 만들어주기
    X_list_train = X_sample_train.tolist() # type(X_list_train[0]) : list
    X_train = [] # type(X_train[0]) : str
    for i in range(len(X_list_train)) :
        X_train.append(X_list_train[i][0])
    X_train = pd.Series(X_train)
    y_train = pd.Series(y_sample_train.tolist())

    return X_train, X_test, y_train, y_test


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


def nlpData(X_train, X_test) :
    """
    1. 데이터 띄워쓰기 보완
    2. 데이터 이모지&불용어 제거
    3. 토큰화
    4. 정수인코딩
    5. 패딩
    ...
    parameters
        X_train : 독립변수 학습데이터 (dataFrame; shape[m, 1])
        X_test : 독립변수 시험데이터 (dataFrame; shape[0.3*n, 1])
    ...
    returns
        tk : 토큰화된 단어 리스트가 담긴 리스트 (list)
        word_dict : 데이터에서 추출한 단어들의 딕셔너리 (dictionary; (index, word))
        X_train_pad : 1~5번이 진행된 독립변수 학습데이터 (dataFrame; shape[m, 1])
        X_test_pad : 1~5번이 진행된 독립변수 시험데이터 (dataFrame; shape[0.3*n, 1])
    """

    twitter = Twitter()
    spacing = Spacing()

    # 띄워쓰기 보완
    X_train = X_train.apply(lambda x : spacing(x))
    X_test = X_test.apply(lambda x : spacing(x))

    #외래어 읽어오기
    loanwords = pd.read_csv('loanwords.txt', encoding = 'cp949')
    loanwords = loanwords['word'].tolist()
    for word in loanwords :
        twitter.add_dictionary(word, 'Noun')

    #불용어 읽어오기
    stopwords = pd.read_csv("stopwords.txt")
    stopwords = stopwords['word'].tolist()
    stopwords.extend([',', '.', '+', '[', ']', '!', '?', '(', ')', '|', '_', '~', '#', '/'])

    #불용어 제거 + 토큰화
    tk = [] # 토큰화된 리스트가 저장될 리스트
    for sentence in tqdm(X_train) :
        reEmoji_sent = rmEmoji(sentence) # 이모티콘 제거
        tokenized_sent = twitter.morphs(reEmoji_sent) # 토큰화
        stopwords_removed_sentence = [word for word in tokenized_sent if not word in stopwords] # 불용어 제거
        tk.append(stopwords_removed_sentence)

    # 정수 인코딩
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(tk)
    word_dict = tokenizer.index_word

    X_train_seq = tokenizer.texts_to_sequences(X_train)
    X_test_seq = tokenizer.texts_to_sequences(X_test)

    # pad를 일정한 길이로 맞춰줌
    X_train_pad = pad_sequences(X_train_seq, maxlen=40, padding='post')
    X_test_pad = pad_sequences(X_test_seq, maxlen=40, padding='post')

    return tk, word_dict, X_train_pad, X_test_pad


def denseModel(X_train_pad, X_test_pad, y_train, y_test, tk, word_dict) :
    """
    Dense Network 모델링    
    ...
    parameters
        X_train_pad : 1~5번이 진행된 독립변수 학습데이터 (dataFrame; shape[m, 1])
        X_test_pad : 1~5번이 진행된 독립변수 시험데이터 (dataFrame; shape[0.3*n, 1])
        y_train : 종속변수 학습데이터 (dataFrame; shape[m, 1])
        y_test : 종속변수 시험데이터 (dataFrame; shape[0.3*n, 1])
        tk : 토큰화된 단어 리스트가 담긴 리스트 (list)
        word_dict : 데이터에서 추출한 단어들의 딕셔너리 (dictionary; (index, word))
    ...
    returns 
        model : 모델
        history : 데이터를 학습시킨 모델
    """

    # Hyper Parameters
    max_len = max(len(word) for word in tk)
    vocab_size = len(word_dict)+1
    embeding_dim = 16
    drop_value = 0.2

    # Model Architecture for dense network
    model = Sequential()
    model.add(Embedding(vocab_size, embeding_dim, input_length=max_len))
    model.add(GlobalAveragePooling1D())
    model.add(Dense(2, activation='relu')) #24: 네트워크 크기
    model.add(Dropout(drop_value))
    model.add(Dense(1, activation='sigmoid'))

    model.summary()

    warnings.filterwarnings('ignore')

    # Compiling the dense model
    model.compile(loss = 'binary_crossentropy', optimizer ='adam', metrics = ['accuracy'])

    num_epochs = 10
    early_stop = EarlyStopping(monitor = 'val_loss', patience = 3)

    history = model.fit(X_train_pad, y_train,
                        epochs = num_epochs, validation_data = (X_test_pad, y_test),
                        callbacks = [early_stop], verbose = 2)

    return model, history

def plotHistory(history) :
    # Read the metrics as a dataframe 
    metrics = pd.DataFrame(history.history)
    # Rename column for plotting
    metrics.rename(columns = {'loss': 'Training_Loss', 'accuracy': 'Training_Accuracy', 'val_loss': 'Validation_Loss', 'val_accuracy': 'Validation_Accuracy'}, inplace = True)



def main(table) :
    dff_x, dff_y = getData(table)

    X_train, X_test, y_train, y_test = balancingData(dff_x, dff_y)

    word_dict, X_train_pad, X_test_pad = nlpData(X_train, X_test)

    model, history = denseModel(X_train_pad, X_test_pad, y_train, y_test, word_dict)
    

if __name__ == '__main__':
    main(input('테이블명: '))