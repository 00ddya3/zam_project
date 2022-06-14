import pandas as pd

"""
최근 데이터 2개 반환
"""

def main(df) :
    #날짜순 정렬
    df = df.sort_values(by = 'date')

    urllist = df.tail(2)['url'].tolist()

    titlelist = df.tail(2)['title'].tolist()

    return urllist, titlelist


if __name__ == '__main__':
    urllist, titlelist = main(input('df :'))