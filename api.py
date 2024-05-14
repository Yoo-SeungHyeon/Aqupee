import requests

url = "http://opendata.kwater.or.kr/openapi-data/service/pubd/dam/multipurPoseDam/list?_wadl&_type=json"
params ={'serviceKey' : "fF%2FEkuf8awXAsiiMYAivKxzIu1Hyl76PXGGqz88Dvs7sMLoKbSaWzAxF2%2F%2FkihhIurY9PYr5kxC6lEvw8mDC4Q%3D%3D",
        'tdate' : '2023-06-29',
        'ldate' : '2022-06-30',
        'vdate' : '2023-06-30',
        'vtime' : '12',
        'numOfRows' : '10',
        'pageNo' : '1'}

response = requests.get(url, params=params)
print(response.content)