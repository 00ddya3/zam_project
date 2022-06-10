import conn_db
import mytendency
import mycloud
import pandas as pd
import streamlit as st
import streamlit_wordcloud as wordcloud

"""
1. 민정DB에서 검색어가 포함된 데이터 추출
2. 유튜브와 네이버뷰에서 각각 1년 내에 발행된 컨텐츠의 개수 제공
3. 유튜브와 네이버뷰에서 컨텐츠 발행 추이 그래프 제공
4. 유튜브와 네이버뷰에서 검색어와 함께 많이 언급된 단어 워드클라우드 제공
"""

#st.sidebar

# 데이터 읽어오기
yt_data = conn_db.main('반팔티셔츠', 'yt_clothes')
view_data = conn_db.main('반팔티셔츠', 'view_clothes')

# 다단 2개로 나눠서 보여줄거임
col1, col2 = st.columns(2)

# 다단 1 : 유튜브
with col1 :
    st.header('☆YOUTUBE☆')
    
    #1년 간 총 컨텐츠량 제공
    st.text('최근 1년 유튜브 게시 영상 수 :' + str(yt_data.shape[0]))

    #1년 간 게시된 컨텐츠의 발행 추이 제공
    yt_count = mytendency.main(yt_data)
    st.line_chart(yt_count)

    #검색어와 함께 많이 언급된 단어 워드클라우드 제공
    yt_words = mycloud.main('반팔티셔츠', yt_data)
    return_obj = wordcloud.visualize(yt_words, per_word_coloring=False)
    

# 다단 2 : 네이버뷰
with col2 :
    st.header('☆NAVER_VIEW☆')

    #1년 간 총 컨텐츠량 제공
    st.text('최근 1년 네이버 뷰 포스트 수 :' + str(view_data.shape[0]))

    #1년 간 게시된 컨텐츠의 발행 추이 제공
    view_count = mytendency.main(view_data)
    st.line_chart(view_count)

    #검색어와 함께 많이 언급된 단어 워드클라우드 제공
    view_words = mycloud.main('반팔티셔츠', view_data)
    return_obj = wordcloud.visualize(view_words, per_word_coloring=False)

