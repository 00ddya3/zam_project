import pandas as pd
import numpy as np
from imblearn.over_sampling import RandomOverSampler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import pickle


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
    3. 벡터화를 진행하기 위해 다시 X, y 데이터로 합쳐줌
    ...
    parameters
        dff_x : 독립변수 시리즈 (dataFrame; shape[n,1])
        dff_y : 종속변수 시리즈 (dataFrame; shape[n,1])
    ...
    returns
        X : 독립변수 시리즈 (dataFrame; shape[n,1])
        y : 종속변수 시리즈 (dataFrame; shape[n,1])
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

    # train data와 test data 합쳐주기
    X = pd.concat([X_train, X_test], axis = 0)
    y = pd.concat([y_train, y_test], axis = 0)

    return X, y


def modeling(X, y) :
    """
    CountVectorizer + MultinomialNB 실행
    ...
    parameters
        X : 독립변수 시리즈 (dataFrame; shape[n,1])
        y : 종속변수 시리즈 (dataFrame; shape[n,1])
    ...
    returns
        clf : 모델
    """
    # count vectorizer
    cv = CountVectorizer()
    X = cv.fit_transform(X) #fit the data

    X.toarray()

    # train data, test data 재정의
    X_train = X[:4048]
    X_test = X[4048:]
    y_train = y[:4048]
    y_test = y[4048:]

    # 나이브 베이즈 분류모델
    clf = MultinomialNB()
    clf.fit(X_train, y_train)
    clf.score(X_test,y_test)

    predictions = clf.predict(X_test)
    print(classification_report(y_test, predictions))

    return clf


def saveModel(table, clf) : 
    """
    구축한 모델을 피클 파일으로 저장
    ...
    parameters
        table : 데이터가 저장되어 있는 DB 테이블명이자 csv명 (str)
        clf : 모델
    ...
    returns
        None
    """
    # 모델 저장
    with open('CVNB_'+table++'.pkl', 'wb') as f:
        pickle.dump(clf, f)


def main(table) :
    dff_x, dff_y = getData(table)

    X, y = balancingData(dff_x, dff_y)

    clf = modeling(X, y)

    saveModel(table, clf)
    

if __name__ == '__main__':
    main(input('테이블명: '))