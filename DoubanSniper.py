# -*- coding: utf-8 -*-
# @Time    : 2021.8.3 19:59
# @Author  : Dreaner
# @FileName: DoubanSniper.py
# @Software: PyCharm


from bs4 import BeautifulSoup
import re
import urllib.request,urllib.error
import sqlite3


def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 获取网页
    datalist = getDate(baseurl)
    dbpath = "movie.db"
    # 保存数据
    saveDataDB(datalist, dbpath)


head = {
        "User-Agent":"Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / "
                     "85.0.4183.121Safari / 537.36 "
}

# 影片详情链接规则
findLink = re.compile(r'<a href="(.*?)">')
# 影片图片的链接
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)
# 影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
# 概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
# 找到影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


# 爬取网页
def getDate(baseurl):
    datalist = []
    x = 1
    # 调用获取页面信息的函数(10次)
    for i in range(0,10):
        url = baseurl + str(i*25)
        html = askURL(url) # 保存获取到的网页源码
        # 逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_="item"):    # 查找符合要求的字符串，形成列表,class加下划线表示属性值
            data = []   # 保存一部电影的所有信息
            item = str(item)    # 将item转换为字符串
            # 影片详情链接
            link = re.findall(findLink, item)[0]
            # 追加内容到列表
            data.append(link)

            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)

            titles = re.findall(findTitle, item)
            if len(titles) == 2:
                ctitle = titles[0]
                data.append(ctitle)     # 添加中文名
                otitle = titles[1].replace("/", "")     # 去掉无关符号
                data.append(otitle)     # 添加外国名
            else:
                data.append(titles[0])
                data.append(' ')    # 外国名如果没有则留空

            rating = re.findall(findRating,item)[0]
            data.append(rating)

            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)

            inq = re.findall(findInq, item)
            if len(inq) != 0 :
                inq = inq[0].replace("。", "")
                data.append(inq)
            else:
                data.append(' ')

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ", bd)    # 去掉<br/>
            bd = re.sub('/', " ", bd)   # 去掉/
            data.append(bd.strip())     # 去掉前后空格

            datalist.append(data) # 把处理好的一部电影信息放入datalist
            # print(link)

            # 下载图片到本地
            # root = "E://DoubanPic//"
            # path = root + str(x) + '.jpg'
            # try:
            #     if not os.path.exists(root):
            #         os.mkdir(root)
            #     if not os.path.exists(path):
            #         #r = requests.get(imgSrc, headers=head)
            #         urllib.request.urlretrieve(imgSrc,path)
            #         #with open(path, 'wb') as f:
            #         #   f.write(r.content)
            #         #   f.close()
            #         print("下载第%d部电影封面"%(x))
            #         x += 1
            #     else:
            #         print("文件保存成功")
            # except:
            #     print("下载失败")
    return datalist


# 得到指定一个url的网页内容
def askURL(url):
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)       # 打印错误信息
        if hasattr(e, "reason"):
            print(e.reason)     # 打印错误原因
    return html


# 保存数据到database
def saveDataDB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index == 5:
                continue
            data[index] = '"'+data[index]+'"'
        sql = '''
                insert into movie_top250 (info_link, pic_link, cname, ename, score, rated, instroduction, info)
                values(%s)'''%",".join(data)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


# 创建数据库
def init_db(dbpath):
    sql = '''
        create table movie_top250    
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar ,
        ename varchar ,
        score numeric ,
        rated numeric ,
        instroduction text,
        info text
        )
'''''

    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
    print("爬取完毕")

