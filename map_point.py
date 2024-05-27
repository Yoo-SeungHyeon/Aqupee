import pandas as pd
import geopandas as gpd
import folium

# 좌표로 상한선 하한선 중앙 지정하기
top_line = [[37,126],[37,130]]
middle_point = [36.5,128]
bottom_line = [[36,126],[36,130]]

# 지도 가져오기
map = folium.Map(location=middle_point, zoom_start=8)

# 상한선 하한선 그리기
folium.PolyLine(locations=top_line).add_to(map)
folium.PolyLine(locations=bottom_line).add_to(map)

# shp 데이터 가져오기
EMD = gpd.read_file('./sig_20230729/sig.shp', encoding='cp949', crs='EPSG:5179')
EMD.set_crs('EPSG:5179',inplace=True)

# 좌표계를 WGS84로 변환
EMD_wgs84 = EMD.to_crs(epsg=4326)

# 변환된 GeoDataFrame 확인
EMD_wgs84

for _, row in EMD_wgs84.iterrows():
    # 각 구역의 경계를 그리기
    folium.GeoJson(
        row['geometry'],
        name=row['SIG_KOR_NM'],
        tooltip=row['SIG_ENG_NM']
    ).add_to(map)

# 레이어 컨트롤러 추가
folium.LayerControl().add_to(map)

# 관측지점 데이터 가져오기
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
fin_opi_df = index_opi_df[index_opi_df['종료일'].isna()] # 더이상 관측하지 않는 곳은 제거

# 데이터 프레임을 관리하기 쉽게 분할
key = fin_opi_df['지점']
value_adress = fin_opi_df['지점주소']
value_latitude = fin_opi_df['위도']
value_longitude = fin_opi_df['경도']

# 위도와 경도를 합쳐서 하나의 좌표 리스트로
value_gps = [list(gps) for gps in zip(value_latitude,value_longitude)]

# 좌표에 지점 위치 원으로 표시
for gps in value_gps:
    folium.CircleMarker(location=gps,color = 'red', fill_color = '#EC4074').add_to(map)

# 딕셔너리로 데이터 관리
point_adress_dict = {key: value for key, value in zip(key,value_adress)}
point_gps_dict = {key: value for key, value in zip(key,value_gps)}

# 온도 데이터 로딩
temp_data = pd.read_csv('./month_mean.csv')

# 좌표 데이터
coordinates = point_gps_dict

# 각 지점에 대한 마커 및 월별 온도 데이터 추가
for index, row in temp_data.iterrows():
    # 지점 번호를 기반으로 좌표 얻기
    if row['지점 번호'] in coordinates:
        lat, lon = coordinates[row['지점 번호']]
        popup_content = f"{row['지점명']} ({row['년도']}-{row['월']}): 평균 기온 {row['월평균 기온']}°C, 지면 온도 {row['월평균 지면온도']}°C"
        folium.Marker(
            [lat, lon],
            popup=popup_content,
            icon=folium.Icon(color='blue')
        ).add_to(map)

# 지도 저장 및 표시
map.save('map_with_temperature.html')
map