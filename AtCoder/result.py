﻿# import
import os
import tweepy
import datetime
import time
import dropbox
import requests
import pickle
import json
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# グローバル変数
AtCoderID = []
TwitterID = []
ratings = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AtCoderID
    global TwitterID
    global ratings

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderID をダウンロード
    dbx.files_download_to_file("AtCoder/AtCoderID.txt", "/AtCoder/AtCoderID.txt")
    with open("AtCoder/AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("AtCoder-result: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("AtCoder/TwitterID.txt", "/AtCoder/TwitterID.txt")
    with open("AtCoder/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("AtCoder-result: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")

    # ratings をダウンロード
    dbx.files_download_to_file("AtCoder/ratings.txt", "/AtCoder/ratings.txt")
    with open("AtCoder/ratings.txt", "rb") as f:
        ratings = pickle.load(f)
    print("AtCoder-result: Downloaded ratings (size : ", str(len(ratings)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global ratings
    
    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # ratings をアップロード
    with open("AtCoder/ratings.txt", "wb") as f:
        pickle.dump(ratings, f)
    with open("AtCoder/ratings.txt", "rb") as f:
        dbx.files_delete("/AtCoder/ratings.txt")
        dbx.files_upload(f.read(), "/AtCoder/ratings.txt")
    print("AtCoder-result: Uploaded ratings (size : ", str(len(ratings)), ")")

def epoch_to_datetime(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

def makeRanking(type, listData, unit):

    global AtCoderID
    global TwitterID
    global ratings
    
    colors = [[0, 0, 0], [128, 128, 128], [128, 64, 0], [0, 128, 0], [0, 192, 192], [0, 0, 255], [192, 192, 0], [255, 128, 0], [255, 0, 0]]
    rows = 30

    flag = int(listData[0][str(type)]) > int(listData[len(listData) - 1][str(type)])
    rankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("AtCoder/data/fontR.ttc", 32)
    rankingFontS = ImageFont.truetype("AtCoder/data/fontB.ttc", 32)
    rankingFirstImg = Image.open("AtCoder/data/result/" + str(type) + "RankingImg (first).jpg")
    resImg = Image.new("RGB", (738 * int((len(listData) + rows - 1) / rows), 65 + 63 * min(len(listData), rows)))
    awardsList = []
    for idx in range(len(listData)):
        if idx % rows == 0:
            resImg.paste(rankingFirstImg, (738 * int(idx / rows), 0))
        rankingImg = Image.open("AtCoder/data/result/rankingImg (cell).jpg")
        rankingDraw = ImageDraw.Draw(rankingImg)
        if idx > 0:
            if flag and int(listData[idx - 1][str(type)]) > int(listData[idx][str(type)]):
                rankNum = rankNum + countNum
                countNum = 1
            elif (not flag) and int(listData[idx - 1][str(type)]) < int(listData[idx][str(type)]):
                rankNum = rankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1

        colorIndex = 0
        for border in range(7, 0, -1):
            if str(listData[idx]["user"]) in ratings:
                if ratings[str(listData[idx]["user"])] >= border * 400:
                    colorIndex = border + 1
                    break   
        if rankNum <= 8:
            rankingDraw.text((10, 7), str(rankNum), fill = (0, 0, 0), font = rankingFontS)
            rankingDraw.text((120, 7), listData[idx]["user"], fill = (colors[colorIndex][0], colors[colorIndex][1], colors[colorIndex][2]), font = rankingFontS)
            rankingDraw.text((560, 7), str(listData[idx][str(type)]), fill = (0, 0, 0), font = rankingFontS)
            awardsList.append("@" + str(TwitterID[myIndex(listData[idx]["user"], AtCoderID)]))
        else:
            rankingDraw.text((10, 7), str(rankNum), fill = (0, 0, 0), font = rankingFont)
            rankingDraw.text((120, 7), listData[idx]["user"], fill = (colors[colorIndex][0], colors[colorIndex][1], colors[colorIndex][2]), font = rankingFont)
            rankingDraw.text((560, 7), str(listData[idx][str(type)]), fill = (0, 0, 0), font = rankingFont)
        resImg.paste(rankingImg, (738 * int(idx / rows), 65 + 63 * (idx % rows)))
    resImg.save("AtCoder/data/result/" + str(type) + "RankingImg_fixed.jpg")
    return " ランキング TOP " + str(rankNum) + "\n入賞の " + " , ".join(awardsList) + " さん おめでとうございます！\n"

def result():
    
    # グローバル変数
    global AtCoderID
    global TwitterID
    global contestFlag
    global ratings

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY"]
    CS = os.environ["CONSUMER_SECRET"]
    AT = os.environ["ACCESS_TOKEN_KEY"]
    AS = os.environ["ACCESS_TOKEN_SECRET"]
    
    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    # データをダウンロード
    downloadFromDropbox()

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    ## 色が変化したユーザーに通知
    for user in AtCoderID:
        
        # 現在の色を取得
        profileURL = "https://atcoder.jp/users/" + str(user)
        profileHTML = requests.get(profileURL)
        try:
            profileHTML.raise_for_status()
            profileData = BeautifulSoup(profileHTML.text, "html.parser")
        except:
            print("AtCoder-result: profileHTML Error")
            continue
        print("AtCoder-result: Downloaded " + str(user) + "'s profileData")
        profileTable = profileData.find_all("table", class_ = "dl-table")
        try:
            nowRating = int(profileTable[1].contents[3].contents[1].contents[0].contents[0])
        except:
            nowRating = -1

        # 色が変わったか調べる
        strs = ["灰色", "茶色", "緑", "水色", "青", "黄色", "オレンジ", "レッド"]
        if user in ratings:
            for border in range(7, 0, -1):
                if ratings[str(user)] < border * 400 and border * 400 <= nowRating:
                    api.update_status(str(user) + " ( @" + TwitterID[myIndex(user, AtCoderID)] + " ) さんの AtCoder レートが " + str(ratings[str(user)]) + " -> " + str(nowRating) + " となり，" + strs[border] + "コーダーになりました！おめでとうございます！！！\n" + profileURL + "\n" + timeStamp)
                    print("AtCoder-result: Tweeted " + str(user) + " ( @" + TwitterID[myIndex(user, AtCoderID)] + " )'s rating change")
                    break
        ratings[str(user)] = nowRating

    ## コンテスト結果のランキング処理
    # 取得すべきコンテストを取得
    session = requests.Session()
    request = session.get(url = "https://atcoder-api.appspot.com/contests")
    contestsJsonData = json.loads(request.text)
    print("AtCoder-result: Downloaded contestsJsonData")
    newcontests = []
    yesterday = datetime.datetime.today() - datetime.timedelta(1)
    for contest in contestsJsonData:
        date = epoch_to_datetime(contest["startTimeSeconds"] + contest["durationSeconds"])
        if yesterday <= date and date < datetime.datetime.today():
            newcontests.append(str(contest["title"]))

    # コンテストごとに処理
    for contest in newcontests:
        rankList = []
        perfList = []
        diffList = []

        # ユーザーの成績を取得
        for user in AtCoderID:
            reslistURL = "https://atcoder.jp/users/" + str(user) + "/history"
            reslistHTML = requests.get(reslistURL)
            try:
                reslistHTML.raise_for_status()
                reslistData = BeautifulSoup(reslistHTML.text, "html.parser")
            except:
                print("AtCoder-result: reslistHTML Error")
                continue
            print("AtCoder-result: Downloaded " + str(user) + "'s reslistData")
            reslistTable = reslistData.find_all("table")
            if len(reslistTable) == 0:
                continue
            reslistRows = reslistTable[0].find_all("tr")
            del reslistRows[0]
            for row in reslistRows:
                if str(contest) == str(row.contents[3].contents[0].contents[0]):
                    if str(row.contents[5].contents[0].contents[0]) != "-":
                        rankList.append({ "user" : str(user), "rank" : int(row.contents[5].contents[0].contents[0]) })
                    if str(row.contents[7].contents[0]) != "-":
                        perfList.append({ "user" : str(user), "perf" : int(row.contents[7].contents[0]) })
                    if str(row.contents[11].contents[0]) != "-":
                        if str(row.contents[11].contents[0]) == "±0":
                            diffList.append({ "user" : str(user), "diff" : int(0) })
                        else:
                            diffList.append({ "user" : str(user), "diff" : int(row.contents[11].contents[0]) })
                    break
        print("AtCoder-result: Checked " + str(contest) + " result")

        # ランキングを作成
        if len(rankList) > 0:
            rankList.sort(key = lambda x: x["rank"])
            tweetText = str(contest) + " 順位表" + makeRanking("rank", rankList, "位")
            api.update_with_media(filename = "AtCoder/data/result/rankRankingImg_fixed.jpg", status = tweetText + "\n" + timeStamp)
            print("AtCoder-result: Tweeted " + str(contest) + " rankRanking")
        if len(perfList) > 0:
            perfList.sort(key = lambda x: x["perf"], reverse = True)
            tweetText = str(contest) + " パフォーマンス値" + makeRanking("perf", perfList, "perf.")
            api.update_with_media(filename = "AtCoder/data/result/perfRankingImg_fixed.jpg", status = tweetText + "\n" + timeStamp)
            print("AtCoder-result: Tweeted " + str(contest) + " perfRanking")
        if len(diffList) > 0:
            diffList.sort(key = lambda x: x["diff"], reverse = True)
            tweetText = str(contest) + " レート変動値" + makeRanking("diff", diffList, "")
            api.update_with_media(filename = "AtCoder/data/result/diffRankingImg_fixed.jpg", status = tweetText + "\n" + timeStamp)
            print("AtCoder-result: Tweeted " + str(contest) + " diffRanking")

    # データをアップロード
    uploadToDropbox()

if __name__ == '__main__':
    print("AtCoder-result: Running as debug...")
    result()
    print("AtCoder-result: Debug finished")
