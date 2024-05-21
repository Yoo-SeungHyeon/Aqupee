import requests
import pprint
import xml.etree.ElementTree as ET
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def date_change(date):
    nowdate = datetime.strptime(date, "%Y-%m-%d")
    tdate = (nowdate - timedelta(days=1)).strftime("%Y-%m-%d")
    ldate = (nowdate.replace(year=nowdate.year - 1)).strftime("%Y-%m-%d")
    vdate = nowdate.strftime("%Y-%m-%d")

    return tdate, ldate, vdate


def parse(item, date):

    try:
        SUGE = item.find("suge").get_text()
        DAMNM = item.find("damnm").get_text()
        TODAYRAIN = item.find("zerosevenhourprcptqy").get_text()
        YESTERDAYRAIN = item.find("prcptqy").get_text()
        CUMYEARRAIN = item.find("pyacurf").get_text()
        CUMLASTYRAIN = item.find("vyacurf").get_text()
        CUMLLASTRAIN = item.find("oyaacurf").get_text()
        LASTDAYINPUTRAIN = item.find("inflowqy").get_text()
        LASTDAYOUTPUTRAIN = item.find("totdcwtrqy").get_text()
        LASTDAYOUTPUTJO = item.find("totdcwtrqyjo").get_text()
        NOWLOWLEVEL = item.find("nowlowlevel").get_text()
        LASTLOWLEVEL = item.find("lastlowlevel").get_text()
        LLYEARLOWLEVEL = item.find("nyearlowlevel").get_text()
        NOWSAVEWATER = item.find("nowrsvwtqy").get_text()
        LASTSAVEWATER = item.find("lastrsvwtqy").get_text()
        LLASTSAVEWATER = item.find("nyearrsvwtqy").get_text()
        NOWSAVERATIO = item.find("rsvwtrt").get_text()
        ENERGY_SUCCESS = item.find("dvlpqyacmtlacmslt").get_text()
        ENERGY_PLAN = item.find("dvlpqyacmtlplan").get_text()
        ENERGY_ERROR = item.find("dvlpqyacmtlversus").get_text()
        YEARENERGYPLAN = item.find("dvlpqyfyerplan").get_text()
        YEARENERGYPREPARE = item.find("dvlpqyfyerversus").get_text()

        return {
            "날짜": date,
            "수계": SUGE,
            "댐이름": DAMNM,
            "금일 강우량": TODAYRAIN,
            "전일 강우량": YESTERDAYRAIN,
            "금년 누계 강우량": CUMYEARRAIN,
            "전년 누계 강우량": CUMLASTYRAIN,
            "예년 누계 강우량": CUMLLASTRAIN,
            "전일 유입량": LASTDAYINPUTRAIN,
            "전일 방류량(본댐)": LASTDAYOUTPUTRAIN,
            "전일 방류량(조정지)": LASTDAYOUTPUTJO,
            "현재 저수위": NOWLOWLEVEL,
            "전년 저수위": LASTLOWLEVEL,
            "예년 저수위": LLYEARLOWLEVEL,
            "현재 저수량": NOWSAVEWATER,
            "전년 저수량": LASTSAVEWATER,
            "예년 저수량": LLASTSAVEWATER,
            "현재 저수율": NOWSAVERATIO,
            "발전량 실적": ENERGY_SUCCESS,
            "발전량 계획": ENERGY_PLAN,
            "발전량 계획대비": ENERGY_ERROR,
            "연간발전계획": YEARENERGYPLAN,
            "연간계획대비": YEARENERGYPREPARE,
        }
    except AttributeError as e:
        return {
            "날짜": date,
            "수계": None,
            "댐이름": None,
            "금일 강우량": None,
            "전일 강우량": None,
            "금년 누계 강우량": None,
            "전년 누계 강우량": None,
            "예년 누계 강우량": None,
            "전일 유입량": None,
            "전일 방류량(본댐)": None,
            "전일 방류량(조정지)": None,
            "현재 저수위": None,
            "전년 저수위": None,
            "예년 저수위": None,
            "현재 저수량": None,
            "전년 저수량": None,
            "예년 저수량": None,
            "현재 저수율": None,
            "발전량 실적": None,
            "발전량 계획": None,
            "발전량 계획대비": None,
            "연간발전계획": None,
            "연간계획대비": None,
        }


def data_calling(day, page, damnm, row):
    tdate, ldate, vdate = date_change(day)

    url = "http://opendata.kwater.or.kr/openapi-data/service/pubd/dam/multipurPoseDam/list"
    params = {
        "serviceKey": "JblClLk%2BuLRS6hB9k3LbHV8cJYUxFo3XL4pNRgX5yJOdGf8E8wlFkrB8so5AunCF9QnI%2FtIdf%2FvkDbpqcWwzKg%3D%3D",
        "tdate": tdate,
        "ldate": ldate,
        "vdate": vdate,
        "vtime": "07",
        "numOfRows": "10",
        "pageNo": page,
    }

    response = requests.get(url, params=params)
    # pprint.pprint(response.text, depth=4)

    soup = BeautifulSoup(response.content)
    # pprint.pprint(soup.text)
    items = soup.find_all("item")

    check = False

    for item in items:
        if item.find("damnm").get_text() == damnm:
            row.append(parse(item, vdate))
    return row


row = []
damlist = ["횡성", "충주", "보령", "안동", "밀양"]
datelist_dry = ["2020-11-30", "2021-01-12", "2022-03-12", "2023-01-05"]
datelist_rain = ["2020-11-30", "2021-01-12", "2022-03-12", "2023-01-05"]

i = 1
for date in datelist_dry:
    for name in damlist:
        if name in ["보령", "밀양"]:
            i = 1

        elif name in ["안동", "충주"]:
            i = 2
        else:
            i = 3

        row = data_calling(date, i, name, row)

df = pd.DataFrame(row)
print("df pass")
print(df)

# csv 파일로 저장하기
df.to_csv("output.csv", index=False)


import sqlite3

conn = sqlite3.connect("")
