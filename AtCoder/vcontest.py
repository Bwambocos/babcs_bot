# import
from PIL import Image, ImageDraw, ImageFont
import requests
from bs4 import BeautifulSoup
import urllib
import time
import datetime
import tweepy
import os


def vcontest():

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY"]
    CS = os.environ["CONSUMER_SECRET"]
    AT = os.environ["ACCESS_TOKEN_KEY"]
    AS = os.environ["ACCESS_TOKEN_SECRET"]

    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # 開催予定のコンテストを取得
    listURL = "https://not-522.appspot.com/"
    listHTML = requests.get(listURL)
    listHTML.raise_for_status()
    listData = BeautifulSoup(listHTML.text, "html.parser")
    print("cper_bot-AtCoder-vcontest: Downloaded listData")

    listTable = listData.find_all("tbody")
    list1 = []
    list2 = []
    vcontestsList = []
    for row in listTable[0].find_all("tr"):
        detail = row.find("a")
        name = str(detail.contents[0])
        beginTime = str(detail.parent.contents[2].contents[0])
        endTime = str(detail.parent.contents[2].contents[1].contents[0])
        list1.append(
            ({"name": name, "beginTime": beginTime, "endTime": endTime}))
    for row in listTable[1].find_all("tr"):
        detail = row.find("a")
        name = str(detail.contents[0])
        beginTime = str(detail.parent.contents[2].contents[0])
        endTime = str(detail.parent.contents[2].contents[1].contents[0])
        list2.append(
            ({"name": name, "beginTime": beginTime, "endTime": endTime}))
    if len(list1 + list2) == 0:
        api.update_status(
            "現在予定されている AtCoder バーチャルコンテストはありません．\nhttps://not-522.appspot.com/\n\n" + timeStamp)
        return

    # 画像生成
    listFontR = ImageFont.truetype("AtCoder/data/fontR.ttc", 32)
    listFontB = ImageFont.truetype("AtCoder/data/fontB.ttc", 32)
    vcontestsListFirstImg = Image.open(
        "AtCoder/data/vcontest/vcontestsListImg (first).jpg")
    vcontestsListImg = Image.new("RGB", (1772, 68 + 64 * len(list1 + list2)))
    vcontestsListImg.paste(vcontestsListFirstImg, (0, 0))
    idx = 0
    for vcontest in list1:
        vcontestListImg = Image.open(
            "AtCoder/data/vcontest/vcontestsListImg (cell).jpg")
        vcontestListDraw = ImageDraw.Draw(vcontestListImg)
        vcontestListDraw.text((10, 7), str(
            vcontest["beginTime"]), fill=(200, 20, 20), font=listFontB)
        vcontestListDraw.text((360, 7), str(
            vcontest["endTime"]), fill=(200, 20, 20), font=listFontB)
        vcontestListDraw.text((710, 7), str(
            vcontest["name"]), fill=(200, 20, 20), font=listFontB)
        vcontestsListImg.paste(vcontestListImg, (0, 68 + 64 * idx))
        idx += 1
    for vcontest in list2:
        vcontestListImg = Image.open(
            "AtCoder/data/vcontest/vcontestsListImg (cell).jpg")
        vcontestListDraw = ImageDraw.Draw(vcontestListImg)
        vcontestListDraw.text((10, 7), str(
            vcontest["beginTime"]), fill=(0, 0, 0), font=listFontR)
        vcontestListDraw.text((360, 7), str(
            vcontest["endTime"]), fill=(0, 0, 0), font=listFontR)
        vcontestListDraw.text((710, 7), str(
            vcontest["name"]), fill=(0, 0, 0), font=listFontR)
        vcontestsListImg.paste(vcontestListImg, (0, 68 + 64 * idx))
        idx += 1
    vcontestsListImg.save("AtCoder/vcontestsListImg_fixed.jpg")

    # リストをツイート
    listTweetText = "現在 " + \
        str(idx) + " の AtCoder バーチャルコンテストが行われて or 予定されています．\nhttps://not-522.appspot.com/\n"
    api.update_status_with_media(
        filename="AtCoder/vcontestsListImg_fixed.jpg", status=listTweetText + "\n" + timeStamp)
    print(
        "cper_bot-AtCoder-vcontest: Tweeted vcontestsListImg_fixed")


if __name__ == '__main__':
    print("cper_bot-AtCoder-vcontest: Running as debug...")
    vcontest()
    print("cper_bot-AtCoder-vcontest: Debug finished")
