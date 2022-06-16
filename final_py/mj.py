import conn_csv
import mytendency
import mycloud
import myrecent

import pandas as pd
import streamlit as st
import streamlit_wordcloud as wordcloud
import time

#전체 데이터 읽어오기
yt_clothes = pd.read_csv('C:/jupiter_workspace/zam_project/final_py/data/yt_clothes.csv', encoding='utf-8')
view_clothes = pd.read_csv('C:/jupiter_workspace/zam_project/final_py/data/view_clothes.csv', encoding='utf-8')
yt_books = pd.read_csv('C:/jupiter_workspace/zam_project/final_py/data/yt_books.csv', encoding='utf-8')
view_books = pd.read_csv('C:/jupiter_workspace/zam_project/final_py/data/view_books.csv', encoding='utf-8')
yt_interior = pd.read_csv('C:/jupiter_workspace/zam_project/final_py/data/yt_interior.csv', encoding='utf-8')
view_interior = pd.read_csv('C:/jupiter_workspace/zam_project/final_py/data/view_interior.csv', encoding='utf-8')


#사이드바
category = st.sidebar.selectbox("Category", ("의류", "도서", "가구"))
if category == '의류' :
    yt_table = yt_clothes
    view_table = view_clothes
elif category == '도서' :
    yt_table = yt_books
    view_table = view_books
elif category == '가구' :
    yt_table = yt_interior
    view_table = view_interior


keyword = st.text_input('keyword : ')

if keyword != '' :
      
    # 다단 2개로 나눠서 보여줄거임
    col1, col2 = st.columns(2)

    # 다단 1 : 유튜브
    with col1 :
        st.header('☆YOUTUBE☆')
        yt_data = conn_csv.main(keyword, yt_table)       # 데이터 읽어오기
        st.text('최근 1년 유튜브 게시 영상 수 :' + str(yt_data.shape[0]))       #1년 간 총 컨텐츠량 제공

    # 다단 2 : 네이버뷰
    with col2 :
        st.header('☆NAVER_VIEW☆')
        view_data = conn_csv.main(keyword, view_table)       # 데이터 읽어오기
        st.text('최근 1년 네이버 뷰 포스트 수 :' + str(view_data.shape[0]))     #1년 간 총 컨텐츠량 제공


    # 다단 2개로 나눠서 보여줄거임
    col3, col4 = st.columns(2)

    # 다단 3 : 유튜브
    with col3 :
        fig = mytendency.main(yt_data)     #1년 간 게시된 컨텐츠의 발행 추이 제공
        st.pyplot(fig)

    # 다단 4 : 네이버뷰
    with col4 :
        fig = mytendency.main(view_data)   #1년 간 게시된 컨텐츠의 발행 추이 제공
        st.pyplot(fig)


    # 다단 2개로 나눠서 보여줄거임
    col5, col6 = st.columns(2)

    # 다단 5 : 유튜브
    with col5 :
        #검색어와 함께 많이 언급된 단어 워드클라우드 제공
        yt_words = mycloud.main(keyword, yt_data)
        return_obj = wordcloud.visualize(yt_words, per_word_coloring=False)
                
    # 다단 6 : 네이버뷰
    with col6 :        
        #검색어와 함께 많이 언급된 단어 워드클라우드 제공
        view_words = mycloud.main(keyword, view_data)
        return_obj = wordcloud.visualize(view_words, per_word_coloring=False)


    col7, col8 = st.columns(2)

     # 다단 7 : 유튜브
    with col7 :
        #최근 발행 컨텐츠 2개 url 제공
        urllist, titlelist = myrecent.main(yt_data)

        link1 = urllist[0]
        link2 = urllist[1]
        title1 = titlelist[0]
        title2 = titlelist[1]

        if st.button(title1):
            st.markdown(link1, unsafe_allow_html=True)

        if st.button(title2) :
            st.markdown(link2, unsafe_allow_html=True)
                
    # 다단 8 : 네이버뷰
    with col8 :        
         #최근 발행 컨텐츠 2개 url 제공
        urllist, titlelist = myrecent.main(view_data)

        link1 = urllist[0]
        link2 = urllist[1]
        title1 = titlelist[0]
        title2 = titlelist[1]

        if st.button(title1):
            st.markdown(link1, unsafe_allow_html=True)

        if st.button(title2) :
            st.markdown(link2, unsafe_allow_html=True)

time.sleep(20)


