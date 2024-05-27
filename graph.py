import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 한글 깨짐 방지
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

df = pd.read_csv('month_mean.csv')
point_num = sorted(set(df['지점 번호']))

colors = [
    'red', 'blue', 'green', 'black', 'purple', 'orange', 'brown', 'pink', 'gray', 'olive',
    'cyan', 'magenta', 'yellow', 'lime', 'teal', 'lavender', 'maroon', 'navy', 'gold', 'salmon',
    'indigo', 'violet'
]

data = []

for j in range(22):
    df_point = df[df['지점 번호']==point_num[j]]['월평균 기온'].to_list()

    comp_prev_year = []
    for i in range(len(df_point)-12):
        comp_prev_year.append(df_point[i] - df_point[i+12])

    plt.plot(comp_prev_year,marker = '', color = colors[j])
    row = [point_num[j],df[df['지점 번호']==point_num[j]]['지점명'].tolist()[0],np.mean(comp_prev_year),np.std(comp_prev_year)]
    data.append(row)



plt.show()

result = pd.DataFrame(data)
result.columns = ['지점번호','지점명','평균','표준편차']
result
