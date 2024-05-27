# 온도 데이터 표시

import pandas as pd
import folium
import imageio
import os
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image, ImageDraw, ImageFont

# 온도 데이터 계산
temp_data = pd.read_csv('./month_mean.csv')
month_mean_temp = temp_data[['년도','월','지점 번호','지점명','월평균 기온']]
Diff_DF = pd.DataFrame()
for num, group in month_mean_temp.groupby('지점 번호'):
    temp_list = group['월평균 기온'].to_list()
    year_list = group['년도'].to_list()
    month_list = group['월'].to_list()
    row = []
    for i in range(len(group)-12):
        temp_diff = temp_list[i] - temp_list[i+12]
        year_diff = str(year_list[i]) + '-' + str(year_list[i+12])
        month = month_list[i]
        row.append([year_diff,month,num,temp_diff])
    split_df = pd.DataFrame(row)
    Diff_DF = pd.concat([Diff_DF,split_df])

Diff_DF.columns = ['비교 년도','월','지점 번호','평균온도 차이']
Diff_DF

# 온도 데이터 로딩
temp_data = Diff_DF

# 관측지점 데이터를 통해 좌표 데이터 생성
data = pd.read_csv('./observation_point_info.csv',encoding="CP949")
OPI_df = pd.DataFrame(data)

# 사용하는 관측지점 목록
id_list = [127,129,130,131,133,135,136,137,138,140,# 177,
226,232,235,236,238,# 239,
271,272,273,276,277,278,279,]

# 관측지점 데이터에서 사용하는 관측지점만 추출
indexing = []
for opi in OPI_df['지점']:
    if opi in id_list:
        indexing.append(True)
    else:
        indexing.append(False)
index_opi_df = OPI_df[indexing]
fin_opi_df = index_opi_df[index_opi_df['종료일'].isna()]

# 데이터 추출
key = fin_opi_df['지점']
value_latitude = fin_opi_df['위도']
value_longitude = fin_opi_df['경도']
value_gps = [list(gps) for gps in zip(value_latitude,value_longitude)]

# 딕셔너리로 좌표 데이터 정리
point_gps_dict = {key: value for key, value in zip(key,value_gps)}

# 좌표 데이터 로딩
coordinates = point_gps_dict

# 이미지 저장 폴더 생성
if not os.path.exists('maps'):
    os.makedirs('maps')

# 컬러맵 설정
cmap = plt.get_cmap('coolwarm', 30)

# 최소/최대 온도 계산
min_temp = temp_data['평균온도 차이'].min()
max_temp = temp_data['평균온도 차이'].max()

# 웹 드라이버 초기화
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# 폰트 설정
try:
    font = ImageFont.truetype("arial.ttf", 15)
except IOError:
    font = ImageFont.load_default()

# 월별 데이터를 지도에 표시하고 이미지로 저장
filenames = []
for (year, month), group in temp_data.groupby(['비교 년도', '월']):
    m = folium.Map(location=[36.5, 127.5], zoom_start=8, tiles='cartodbpositron')

    for index, row in group.iterrows():
        if row['지점 번호'] in coordinates:
            lat, lon = coordinates[row['지점 번호']]
            # 온도에 따른 색상 적용
            norm_temp = (row['평균온도 차이'] - min_temp) / (max_temp - min_temp)  # 정규화
            color = mcolors.rgb2hex(cmap(norm_temp))  # 색상 변환
            radius = 10000 + (row['평균온도 차이'] * 100)  # 온도가 높을수록 크게 표시
            folium.Circle(
                location=[lat, lon],
                radius=radius,
                color=color,
                fill=True,
                fill_opacity=0.7
            ).add_to(m)
            # 원 안에 텍스트로 온도 표시
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=f'<div style="font-size: 12pt; color: black; text-align: center;">{row["평균온도 차이"]:.1f}°C</div>')
            ).add_to(m)
    
    # 파일 저장
    filename = f'maps/map_{year}_{month}.png'
    m.save(f'{year}_{month}.html')
    driver.get(f'file://{os.getcwd()}/{year}_{month}.html')
    sleep(1)  # 페이지 로드 대기
    driver.save_screenshot(filename)
    filenames.append(filename)
    os.remove(f'{year}_{month}.html')

driver.quit()

# GIF 생성
images = [imageio.imread(filename) for filename in filenames]
imageio.mimsave('temperature_map.gif', images, fps=1)

# 생성한 이미지 파일 정리
for filename in filenames:
    os.remove(filename)
