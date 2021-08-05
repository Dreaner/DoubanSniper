# -*- coding: utf-8 -*-
# @Time    : 2021.8.3 19:59
# @Author  : Dreaner
# @FileName: DoubanSniper.py
# @Software: PyCharm

from bs4 import BeautifulSoup
import re  # 正则表达式
import urllib.error, urllib.request
import xlwt
import sqlite3


def main():
    baseurl = "https://movie.douban.com/top250?start="
    datalist = getData(baseurl)
    savepath = ".\\豆瓣电影top250.xls"
    # 保存数据到xls文档
    saveData(datalist, savepath)
    # askURL("https://movie.douban.com/top250?start=")


# 影片详情链接
findLink = re.compile(r'<a href="(.*?)">')
# 影片图片
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)
# 影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 影片评价人数
findJudgeNum = re.compile(r'<span>(\d*)人评价</span>')
# 影片介绍
findIntro = re.compile(r'<span class="inq">(.*)</span>')
# 影片信息
findInfo = re.compile(r'<p class="">(.*?)</p>', re.S)


# 爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0, 10):  # 豆瓣top250一共10页 每页25个条目
        url = baseurl + str(i * 25)
        html = askURL(url)  # 保存获取到的网页的源码

        # 解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_="item"):
            # print(item)        # 查看电影item的全部信息
            data = []  # 保存电影的所有信息
            item = str(item)

            # 影片详情链接
            link = re.findall(findLink, item)[0]
            data.append(link)
            # 影片图片
            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)
            # 影片片名
            title = re.findall(findTitle, item)
            if len(title) == 2:
                chineseTitle = title[0]  # 中文片名
                data.append(chineseTitle)
                foreignTitle = title[1].replace("/", "")  # 外文片名
                data.append(foreignTitle)
            else:
                data.append(title[0])
                data.append(' ')
            # 影片评分
            rating = re.findall(findRating, item)[0]
            data.append(rating)
            # 影片评价人数
            judgeNum = re.findall(findJudgeNum, item)
            data.append(judgeNum)
            # 影片介绍
            intro = re.findall(findIntro, item)
            if len(intro) != 0:
                intro = intro[0].replace("。", "")
                data.append(intro)
            else:
                data.append(' ')
            # 影片信息
            info = re.findall(findInfo, item)[0]
            info = re.sub('<br(\s+)?/>(\s+)', " ", info)  # 去掉<br/>
            info = re.sub('/', " ", info)  # 把/换成空格
            data.append(info.strip())  # 去掉空格

            datalist.append(data)  # 将一部处理过的电影信息放入datalist
            # print(datalist)
    return datalist


# 得到指定一个URL的网页内容
def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) "
                      "AppleWebKit / 537.36(KHTML, likeGecko) "
                      "Chrome / 92.0.4515.107 "
                      "Safari / 537.36 "
                      "Edg / 92.0.902.62"
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# 保存数据
def saveData(datalist, savepath):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=0)
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外文名", "评分", "评价人数", "介绍", "相关信息")
    for i in range(0, 8):
        sheet.write(0, i, col[i])
    for i in range(0, 250):
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 8):
            sheet.write(i + 1, j, data[j])

    book.save(savepath)  # 保存到xls文档


if __name__ == "__main__":
    main()
    print("爬取完毕！")

