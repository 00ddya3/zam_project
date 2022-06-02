import streamlit as st
import pandas as pd

## Title
st.title('Streamlit Tutorial')

#side bar
st.sidebar.text('zamcodings')
st.sidebar.selectbox("왼쪽 사이드바 Select Box", ("의류", "도서", "가구"))

## Header/Subheader
st.header('This is header')
st.subheader('This is subheader')

## Text
st.text('Hello Streamlit! 이 글은 튜토리얼 입니다.')

## Select Box
occupation = st.selectbox("직군을 선택하세요.", ['aa', 'bb', 'cc', 'dd'])
st.write("당신의 직군은 ", occupation, " 입니다.")

if occupation == 'aa' : 
    second = st.selectbox("multi combobox", ['a1', 'a2', 'a3'])
elif occupation == 'bb' :
    second = st.selectbox("multi combobox", ['b1', 'b2', 'b3'])
elif occupation == 'cc' :
    #layout
    col1, col2 = st.columns(2)
    with col1 :
        st.video('https://www.youtube.com/watch?v=z1jOb9PTe9E', start_time=2)
    with col2 :
        st.video('https://www.youtube.com/watch?v=z1jOb9PTe9E', start_time=2)


df = pd.read_csv("C:/jupiter_workspace/data/naver_api.csv", header=None)
df.columns=['title', 'uploader', 'date', 'url']

st.dataframe(df)