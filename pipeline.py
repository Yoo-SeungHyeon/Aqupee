from datetime import datetime
from airflow import DAG
from pathlib import Path
from airflow.operators.python import PythonOperator
import requests

# 데이터를 저장할 디렉토리 확인 및 생성하는 함수 정의
def make_data_store():
    Path(DATA_DIR).mkdir(exist_ok=True, parents=True)

# 공공 데이터 가져오는 함수 정의
def get_api(api_key, url, params):
    URL = url + api_key # 형식에 맞게 url 구성
    response = requests.get(URL,params=params) # get 요청을 보내서 응담을 받아옴
    contents = response.content # 내용을 저장
    decode_xml= contents.decode('UTF-8') # 활용을 위해 xml decode
    return decode_xml.replace('/','').replace('>','').split('<') # 기호 정리 및 리스트화

# 데이터 정제하는 함수 정의
def get_data(list,char):
    result = []
    for i in list:
        char_len = len(char) # 탐색할 글자의 크기 계산
        if char in i:
            result.append(i[char_len:]) # 앞서 계산한 글자의 크기를 이용해 슬라이싱 -> 원하는 데이터만 추출
    return [item for item in result if item and item.strip()] # none값이나 빈 문자열 정리

# 필요한 데이터 추출하는 함수 정의
def data_filter(data,dict):
    result = {}
    for a,b in dict.items(): # 딕셔너리의 키와 값을 구분
        result = {**result,**{a:get_data(data,b)}} # 키마다 적합한 값들을 get_data()함수를 이용해서 매칭시키고 기존의 딕셔너리에 추가
    return result



# 데이터 저장 위치 선언
DATA_DIR = "/data"

# 필요 객체 선언
api_key = "fF%2FEkuf8awXAsiiMYAivKxzIu1Hyl76PXGGqz88Dvs7sMLoKbSaWzAxF2%2F%2FkihhIurY9PYr5kxC6lEvw8mDC4Q%3D%3D"
url = "http://opendata.kwater.or.kr/openapi-data/service/pubd/dam/multipurPoseDam/list?tdate=2018-08-19&ldate=2017-08-20&vdate=2018-08-20&vtime=07&serviceKey=" + api_key
params = {  
    'tdate' : '2018-08-19', #선택 날짜 기준 전일
    'ldate' : '2017-08-20', #선택 날짜 기준 전년
    'vdate' : '2018-08-20', #선택 날짜
    'vtime' : '07', #조회 시간
    'numOfRows' : '10', #줄 수
    'pageNo' : '1' #페이지 번호
}
#응답 메시지 명세
dict = {
    '수계' : 'suge',
    '댐이름' : 'damnm',
    '강우량 금일' : 'zerosevenhourprcptqy',
    '금년 누계강우량' : 'pyacurf',
    '전년 누계강우량' : 'vyacurf',
    '예년 누계강우량' : 'oyaacurf',
    '전일 유입량' : 'inflowqy',
    '전일 방류량(조정지)' : 'totdcwtrqyjo',
    '저수위(현재)' : 'nowlowlevel',
    '저수위(전년)' : 'lastlowlevel',
    '저수의(예년)' : 'nyearlowlevel',
    '저수량(현재)' : 'nowrsvwtqy',
    '저수량(전년)' : 'lastrsvwtqy',
    '저수량(예년)' : 'nyearrsvwtqy',
    '현재저수율' : 'rsvwtrt',
    '발전량(실적)' : 'dvlpqyacmtlacmslt',
    '발전량(계획)' : 'dvlpqyacmtlplan',
    '발전량(계획대비)' : 'dvlpqyacmtlversus',
    '연간발전계획' : 'dvlpqyfyerplan',
    '연간계획대비' : 'dvlpqyfyerversus'
    }


#dag 정의
dag = DAG(
    dag_id = "api_pipeline", #DAG 이름
    description = "공공데이터 api 활용 pipeline", #DAG 설명
    start_date = datetime(2024,5,19), #실행 시간
    schedule_interval = None, #반복 횟수
    catchup = False, #과거 작업 허용 여부
)

# make_data_store()을 실행하는 task 정의
make_data_store = PythonOperator(
    task_id = "data_store_setting", # task 이름
    python_callable = make_data_store, # 실행할 python 함수 호출
    dat = dag # dag 지정
)

get_data = PythonOperator(
    task_id = "get_data",
    python_callable = get_data(get_api(api_key,url,params),dict),
    dag = dag
    )

# data_store = PythonOperator(
#     task_id = 'data_store',
#     python_callable = data_store(),
#     dag = dag
# )