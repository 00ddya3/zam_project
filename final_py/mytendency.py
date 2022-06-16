import pandas as pd
import matplotlib.pyplot as plt
import logging



"""
데이터를 월별로 그룹화하여 발행량 plot
"""

def main(df) :

    df.date = pd.to_datetime(df.date)     #datetime type으로 변환
    df['month'] = df['date'].dt.month     #월추출
    
    months = ['2021-7','2021-8', '2021-9', '2021-10', '2021-11', '2021-12', '2022-1', '2022-2', '2022-3', '2022-4', '2022-5', '2022-6']
    cnts = []
        
    for month in months :
        month = month.split('-')[1]
        cnt = df[df['month'] == int(month)].shape[0]
        cnts.append(cnt)

    logging.basicConfig(level='INFO')

    mlogger = logging.getLogger('matplotlib')
    mlogger.setLevel(logging.WARNING)

    fig = plt.figure(figsize=(10, 6))
    plt.rc('font', family='Malgun Gothic')
    

    plt.plot(months, cnts, marker = 'o', linestyle='--', linewidth=3, color='#F68121')

    for i, v in enumerate(months):
        plt.text(v, cnts[i], cnts[i],                   # 좌표 (x축 = v, y축 = y[0]..y[1], 표시 = y[0]..y[1])
                fontsize = 20, 
                color='#F68121',
                horizontalalignment='right',            # horizontalalignment (left, center, right)
                verticalalignment='bottom')             # verticalalignment (top, center, bottom)

    plt.xticks(rotation=40, fontsize=15)
    plt.yticks(fontsize=15)

    plt.title('연간 컨텐츠 발행량 추이', fontsize=20)
    plt.xlabel ('months', fontsize=20)
    plt.ylabel('contents', fontsize=20)

    return fig


if __name__ == '__main__':
    df_count = main(input('df :'))