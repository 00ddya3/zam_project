import streamlit as st
import streamlit_wordcloud as wordcloud
import pandas as pd
import time

## Title
st.title('Streamlit Tutorial')

#side bar
st.sidebar.text('zamcodings')
category = st.sidebar.selectbox("왼쪽 사이드바 Select Box", ("의류", "도서", "가구"))

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


# 데이터프레임
df = pd.read_csv("C:/jupiter_workspace/data/naver_api.csv", header=None)
df.columns=['title', 'uploader', 'date', 'url']

st.dataframe(df)


# 워드클라우드
word = [dict(text='원피스', value=167), dict(text='뷔스티에', value=121), dict(text='롱', value=36), dict(text='코디', value=36), dict(text='행복', value=25)]
return_obj = wordcloud.visualize(word, per_word_coloring=False)


#import pandas as pd
#import streamlit as st

link1 = "https://stackoverflow.com/questions/71641666/hyperlink-in-streamlit-dataframe"
link2 = "https://stackoverflow.com/questions/71731937/how-to-plot-comparison-in-streamlit-dynamically-with-multiselect"
df = pd.DataFrame(
    {
        "url": [
            f'<a target="_blank" href="{link1}">Hyperlink in Streamlit dataframe</a>',
            f'<a target="_blank" href="{link2}">How to plot comparison in Streamlit dynamically with multiselect?</a>'
        ],
        "label": ["question", "question"]
    }
)

st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

# not centered
st.markdown(
    """<a href="https://www.example.com/">example.com</a>""", unsafe_allow_html=True,
)

#centered
st.markdown(
    """<a style='display: block; text-align: center;' href="https://www.example.com/">example.com</a>
    """,
    unsafe_allow_html=True,
)

if st.button('sid') :
    st.write('sss')

time.sleep(50)