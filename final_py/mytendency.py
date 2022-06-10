import pandas as pd

"""
데이터를 월별로 그룹화하여 카운트한 새로운 df 반환
"""

def main(df) :

    df.date = pd.to_datetime(df.date)     #datetime type으로 변환
    df['month'] = df['date'].dt.month     #월추출
    df_count = df.groupby('month').count()     #월별 게시글 개수 카운팅
    #df_count = df_count.reset_index()               #인덱스 초기화
    df_count = df_count[['title']]         #필요한 열만 추출
    #df_count.columns = ['month', 'num']             #컬럼명 교체
    
    return df_count


if __name__ == '__main__':
    df_count = main(input('df :'))