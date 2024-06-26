import requests
import pprint
import xml.etree.ElementTree as ET
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def date_change(date):
    nowdate = datetime.strptime(date, "%Y-%m-%d")

    nextYear = nowdate.replace(year=nowdate.year + 1)
    endDate = (nextYear - timedelta(days=1)).strftime("%Y%m%d")
    startDate = nowdate.strftime("%Y%m%d")

    return startDate, endDate


def parse_month(year, month, stnid, stnnm, m_temp, m_gtemp):

    try:

        # 지점 이름, 지점 아이디

        return {
            "년도": year,
            "월": month,
            "지점 번호": stnid,
            "지점명": stnnm,
            "월평균 기온": m_temp,
            "월평균 지면온도": m_gtemp,
        }

    except AttributeError as e:
        return {
            "년도": None,
            "월": None,
            "지점 번호": None,
            "지점명": None,
            "월평균 기온": None,
            "월평균 지면온도": None,
        }


def mean_cul(item, result_m):

    STNID = item.find("stnId").get_text()
    STNNM = item.find("stnNm").get_text()
    try:
        temp = float(item.find("avgTa").get_text())
        ground_temp = float(item.find("avgTs").get_text())
    except ValueError:
        temp = 0
        ground_temp = 0
        if "error" in result_m:
            result_m["error"] = result_m["error"] + 1
        else:
            result_m["error"] = 1

    result_m["stnid"] = STNID
    result_m["stnnm"] = STNNM

    if "t_total" in result_m:
        result_m["t_total"] = result_m["t_total"] + temp
        result_m["gt_total"] = result_m["gt_total"] + ground_temp
        result_m["cnt"] = result_m["cnt"] + 1
    else:
        result_m["t_total"] = temp
        result_m["gt_total"] = ground_temp
        result_m["cnt"] = 1

    return result_m


def init(result_m):
    result_m = {}
    return result_m


def data_calling(day, id, month_result):
    startDt, endDt = date_change(day)

    url = "http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList"
    params = {
        "serviceKey": "JblClLk+uLRS6hB9k3LbHV8cJYUxFo3XL4pNRgX5yJOdGf8E8wlFkrB8so5AunCF9QnI/tIdf/vkDbpqcWwzKg==",
        "pageNo": 1,
        "numOfRows": "365",
        "dataType": "XML",
        "dataCd": "ASOS",
        "dateCd": "DAY",
        "startDt": startDt,
        "endDt": endDt,
        "stnIds": id,
    }

    response = requests.get(url, params=params)

    # pprint.pprint(response.text, depth=4)

    soup = BeautifulSoup(response.content, features="xml")
    # pprint.pprint(soup.text)
    header = soup.find("header")
    if header is None:
        return month_result

    result_Msg = header.find("resultMsg").get_text()

    if result_Msg == "NORMAL_SERVICE":

        items = soup.find_all("item")

        if items is None:
            print("nothing in items")
            return month_result

        month = "01"

        result_m = {}
        # result_m = init(result_m)

        for item in items:
            TM = item.find("tm").get_text()

            months = TM.split("-")

            if month == months[1]:
                result_m = mean_cul(item, result_m)

            else:
                if "error" in result_m:
                    count = result_m["cnt"] - result_m["error"]
                else:
                    count = result_m["cnt"]

                m_temp = result_m["t_total"] / count
                m_gtemp = result_m["gt_total"] / count
                month_result.append(
                    parse_month(
                        months[0],
                        month,
                        result_m["stnid"],
                        result_m["stnnm"],
                        m_temp,
                        m_gtemp,
                    )
                )
                month = months[1]
                result_m = {}
                # result_m = init(result_m)
                result_m = mean_cul(item, result_m)

        if "error" in result_m:
            count = result_m["cnt"] - result_m["error"]
        else:
            count = result_m["cnt"]

        m_temp = result_m["t_total"] / count
        m_gtemp = result_m["gt_total"] / count

        month_result.append(
            parse_month(
                months[0], month, result_m["stnid"], result_m["stnnm"], m_temp, m_gtemp
            )
        )

        return month_result

    else:
        print(f"{id}, ")
        return month_result


# year_result = []
month_result = []
date_list = [
    "2014-01-01",
    "2015-01-01",
    "2016-01-01",
    "2017-01-01",
    "2018-01-01",
    "2019-01-01",
    "2020-01-01",
    "2021-01-01",
    "2022-01-01",
    "2023-01-01",
]
id_list = [
    127,
    129,
    130,
    131,
    133,
    135,
    136,
    137,
    138,
    140,
    # 177,
    226,
    232,
    235,
    236,
    238,
    # 239,
    271,
    272,
    273,
    276,
    277,
    278,
    279,
]


for date in date_list:
    for id in id_list:
        month_result = data_calling(date, id, month_result)


df = pd.DataFrame(month_result)
print("df pass")
print(df)

# csv 파일로 저장하기
df.to_csv("month_mean.csv", index=False)
