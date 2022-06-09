from powernad.API.Campaign import *
from powernad.API.RelKwdStat import *
import pandas as pd

"""
powernad api에 접속하여 키워드에 대한 검색기록과 광고 관련 정보를 받아옴
"""

def main(searchword) :
    """
    API에 접속
    ...
    parameters 
        searchword : 검색어
    ...
    return
        None 
    """

    NAVER_SECRET_KEY = 'AQAAAABZZNcmQnJhsoPKPB+OVnz+yKMx8Mk5JTgbo9VG/XAJEA=='
    NAVER_API_KEY = '01000000005964d726427261b283ca3c1f8e567cfeff6fee2fb0c3e7915c994f165a35bfbe'
    CUSTOMER_ID = '910516'
    NAVER_BASE_URL = 'https://api.naver.com'

    # API 연결
    c=Campaign(NAVER_BASE_URL, NAVER_API_KEY, NAVER_SECRET_KEY, CUSTOMER_ID)
    rel = RelKwdStat(NAVER_BASE_URL, NAVER_API_KEY, NAVER_SECRET_KEY, CUSTOMER_ID)

    #ApI에서 searchword에 관한 정보와 그 연관검색어를 받아옴
    kwdDataList = rel.get_rel_kwd_stat_list(siteId=None, biztpId=None, hintKeywords=searchword, event=None, month=None, showDetail='1')

    # 빈 데이터프레임 만들기
    df = pd.DataFrame(
        columns=['연관키워드', '30일간 PC 조회수', '30일간 모바일 조회수', '30일간 평균 PC 클릭수', '30일간 평균 모바일 클릭수', 
            '30일간 평균 PC 클릭율', '30일간 평균 모바일 클릭율', '30일간 평균 PC 광고 수', 'PC 광고 기반 경쟁력']
        )

    # 데이터 삽입
    for i in range(len(kwdDataList)) :
        df.loc[i] = [kwdDataList[i].relKeyword, kwdDataList[i].monthlyPcQcCnt, kwdDataList[i].monthlyMobileQcCnt, kwdDataList[i].monthlyAvePcClkCnt,
            kwdDataList[i].monthlyAveMobileClkCnt, kwdDataList[i].monthlyAvePcCtr, kwdDataList[i].monthlyAveMobileCtr, kwdDataList[i].plAvgDepth, kwdDataList[i].compIdx]

    df.head()


if __name__ == '__main__':
    main(input('검색어: '))

    