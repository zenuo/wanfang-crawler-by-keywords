from urllib.parse import quote_plus
from urllib.request import urlopen
from urllib.error import URLError,HTTPError
from bs4 import BeautifulSoup
from http.client import HTTPException
from pybloom import BloomFilter
import re,time,math,pymysql.cursors,sys,varibles


def searchUrlCreator(quoted_kw,pageNum):
    #构造查询记录Url，每页10条记录
    varibles.Url = "http://s.wanfangdata.com.cn/Paper.aspx?q=" + quoted_kw + "%20DBID%3AWF_"+ varibles.typeName + "&f=top&p=" + (str)(pageNum)

def getRecordAmount():
    while True:
        try:
            varibles.recordAmount = (int)(re.findall("an>(.+?)条", (str)(varibles.bsObj.findAll("div",{"class":"total-records"})).replace(',',''))[0])
            break
        except:
            getBsObj()
            print(time.strftime("%Y/%m/%d %H:%M:%S,") + 'search page error,rerty.')
        
def getUrl_Title_IndexTerm_Included_Source_Date_Author_Major():
    while True:
        try:
            text = (str)(varibles.bsObj.findAll("a",{"class":"title"}))
            varibles.recordUrlList = re.findall("href=\"(.+?)\" tar",text)
            varibles.recordTitleList = re.findall("nk\">(.+?)</a>",text.replace('<em>','').replace('</em>',''))
            #期刊论文
            if varibles.typeName == 'QK':
                varibles.recordCategoryList = ["期刊论文"] * 10
                text = (list)(varibles.bsObj.findAll("div",{"class":"record-keyword"}))
                for i in range(len(text)):
                    #Index Term
                    varibles.recordIndexTermList[i] = re.findall("<span>(.+?)</span>", (str)(text[i]))
                text = (list)(varibles.bsObj.findAll("div",{"class":"record-subtitle"}))
                for i in range(len(text)):
                    varibles.recordIncludedList[i] = re.findall("\">(.+?)</span",(str)(text[i]))
                    t = re.findall("\">(.+?)</a",(str)(text[i]))
                    #Source
                    varibles.recordSourceList[i] = t[0]
                    #Date
                    varibles.recordDateList[i] = t[1]
                    #Author(s)
                    varibles.recordAuthorList[i] = t[2:]
            #学位论文
            elif varibles.typeName == 'XW':
                varibles.recordCategoryList = ["学位论文"] * 10
                #Index term
                text = (list)(varibles.bsObj.findAll("div",{"class":"record-keyword"}))
                for i in range(len(text)):
                    #Index Term
                    varibles.recordIndexTermList[i] = re.findall("<span>(.+?)</span>", (str)(text[i]))
                text = (list)(varibles.bsObj.findAll("div",{"class":"record-subtitle"}))
                for i in (range(len(text))):
                    t = re.findall("/a>(.+?)</d",(str)(text[i]).replace('\n',''))
                    t = t[0].replace('\r','').strip().replace('\xa0','|').replace('（学位年度）','')
                    #Source
                    varibles.recordSourceList[i] = t[t.find("|") + 1:-5]
                    #Major
                    varibles.recordMajorList[i] = t[:t.find("|")]
                    #date
                    varibles.recordDateList[i] = t[-4:]
                    #Author
                    t = re.findall("\">(.+?)</a",(str)(text[i]))
                    varibles.recordAuthorList[i] = t[0]
            break
        except:
            print(time.strftime("%Y/%m/%d %H:%M:%S,") + 'search page error,pass.')
            #time.sleep(5)
            #getBsObj()
            break

def getIntro():
    #尝试10次
    for i in range(10):
        try:
            varibles.intro = re.findall("text\">(.+?)</d",(str)(varibles.bsObj.findAll("div",{"class":"row clear zh"})).replace('\n',''))[0].replace(r'"',r'\"')
            break
        except:
            print(time.strftime("%Y/%m/%d %H:%M:%S,") + 'paper page error,retry.')
            time.sleep(4)

def crawlSearchPage():
    print(time.strftime("%Y/%m/%d %H:%M:%S,"),end='')
    if varibles.typeName == 'XW':
        print('\nNow crawl Degree theses,',end='')
    else:
        print('\nNow crawl Periodical papers,',end='')
    #当前页码
    pageNum = 1
    #保存记录条数
    savedRecords = 0
    spendTime = 0
    saveCrawl(varibles.kw, spendTime , savedRecords)
    #此次爬取的开始时间
    startTime = (int)(time.time())
    quoted_kw = quote_plus(varibles.kw)
    searchUrlCreator(quoted_kw,1)
    getBsObj()
    getRecordAmount()
    print("found %d Rcds" % varibles.recordAmount)
    #每页有10条记录，由于网页原因，每次检索最多爬取100页
    for i in range(1,101):
        #当前页码大于页面总数时退出循环
        if pageNum > math.ceil(varibles.recordAmount / 10):
            break
        #爬取数量大于记录总数时退出循环
        if savedRecords > varibles.recordAmount:
            break
        searchUrlCreator(quoted_kw,i)
        print(varibles.Url)
        getBsObj()
        #Get data from search page.
        getUrl_Title_IndexTerm_Included_Source_Date_Author_Major()
        pageNum += 1
        for j in range(len(varibles.recordUrlList)):
            if varibles.recordUrlList[j] == '':
                break
            #varibles.Url = varibles.recordUrlList[j]
            #判断页面是否属于空页面
            #id = varibles.recordUrlList[j][varibles.recordUrlList[j].rfind(".cn") + 4:]
            #if bloomCheck(id) == False:
            if True:
                #getBsObj()
                #addIdToFilter(id)
                #Get data from paper page.
                #getIntro(j)
                saveRecord(j, varibles.kw)
                #计数
                if varibles.saveFlag == True:
                    savedRecords = savedRecords + 1
                    #还原写入成功标识
                    varibles.saveFlag = False
                #爬取数量大于记录总数时退出循环
                if savedRecords == varibles.recordAmount:
                    break
    #此次爬取的结束时间
    endTime = (int)(time.time())
    spendTime = endTime - startTime
    #保存此次爬取的信息
    updateCrawl(varibles.kw , spendTime , savedRecords)
    print("cost %ds,"% spendTime + "%d Rcds saved."% savedRecords)

def crawlPaperPage(num):
    
    se_total = "SELECT url from record WHERE intro is NULL;"
    
    with varibles.connection.cursor() as cursor:
        cursor.execute(se_total)
        total = cursor.rowcount
        amount = math.ceil(total / 6)
        se_url = "SELECT url from record WHERE intro is NULL LIMIT %d,%d;" % ((num - 1) * amount,amount)
        cursor.execute(se_url)
        urlList = cursor.fetchall()
    count = 1
    for s in urlList:
        varibles.Url = s['url']
        print(varibles.Url)
        getBsObj()
        getIntro()
        up_record = "UPDATE record SET intro = \"%s\" WHERE url = \"%s\";" % (varibles.intro,varibles.Url)
        with varibles.connection.cursor() as cursor:
            cursor.execute(up_record)
        varibles.connection.commit()
        print("%d/%d done." % (count,amount))
        count += 1

def urlHandler(url):
    #处理url请求，单次最长请求7200times
    for i in range(7200):
        html = None
        try:
            html = urlopen(url)
            if html is not None:
                break
        except URLError or HTTPError as e:
            print(time.strftime("%Y/%m/%d %H:%M:%S,") + (str)(e) + ",retry.")
            errorLog((str)(e),varibles.kw)
            continue
    return html

def getBsObj():
    #单次最长请求7200times
    for i in range(7200):
        try:
            html = urlHandler(varibles.Url)
            varibles.bsObj = BeautifulSoup(html,"lxml")
            break
        except HTTPException as e:
            print(time.strftime("%Y/%m/%d %H:%M:%S,") + (str)(e) + ",retry.")
            errorLog((str)(e))
            time.sleep(2)
            continue

def connectDB():
    try:
        varibles.connection = pymysql.connect(host = varibles.dbIPAddr,
                                     user = varibles.dbUser,
                                     password = varibles.dbPassword,
                                     db = 'wanfang',
                                     charset = 'utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        print(e)
        print("Connect DB failed,check it and retry,now exit.")
        sys.exit(0)

def disconnectDB():
    varibles.connection.close()

def readFile(fileName):
    try:
        file = open('./' + fileName , 'r')
        kwList = file.read()
    except FileNotFoundError:
        print("No such file \"%s\""% fileName + ",please check it and retry.")
        sys.exit(0)
    return kwList

def createTable():
    ct_record = "CREATE TABLE IF NOT EXISTS record(id CHAR(50),title VARCHAR(200),searchWord VARCHAR(100),category VARCHAR(20),source VARCHAR(50),date CHAR(30),major CHAR(30),url VARCHAR(100),intro MEDIUMTEXT,PRIMARY KEY (id));"
    ct_id_author = "CREATE TABLE IF NOT EXISTS id_author(id CHAR(50),author VARCHAR(50));"
    ct_id_included = "CREATE TABLE IF NOT EXISTS id_included(id CHAR(50),included VARCHAR(50));"
    ct_id_indexTerm = "CREATE TABLE IF NOT EXISTS id_indexTerm(id CHAR(50),indexTerm VARCHAR(50));"
    ct_crawlLog = "CREATE TABLE IF NOT EXISTS crawlLog(crawlTime INT,searchWord VARCHAR(100),savedAmount INT,spendTime INT);"
    ct_errorLog = "CREATE TABLE IF NOT EXISTS errorLog(errorTime INT,searchWord VARCHAR(100),errorName VARCHAR(50));"
    with varibles.connection.cursor() as cursor:
        cursor.execute(ct_record)
        cursor.execute(ct_id_author)
        cursor.execute(ct_id_indexTerm)
        cursor.execute(ct_id_included)
        cursor.execute(ct_crawlLog)
        cursor.execute(ct_errorLog)
    cursor.close()

def saveRecord(i,kw):
    id = varibles.recordUrlList[i][varibles.recordUrlList[i].rfind(".cn") + 4:] 
    sv_record = "INSERT INTO record(id,title,searchWord,category,source,date,major,url) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);"
    sv_id_author = "INSERT INTO id_author(id,author) VALUES(%s,%s);"
    sv_id_included = "INSERT INTO id_included(id,included) VALUES(%s,%s);"
    sv_id_indexTerm = "INSERT INTO id_indexTerm(id,indexTerm) VALUES(%s,%s);"
    with varibles.connection.cursor() as cursor:
        try:
            cursor.execute(sv_record,(id,varibles.recordTitleList[i],kw,varibles.recordCategoryList[i],varibles.recordSourceList[i],varibles.recordDateList[i],varibles.recordMajorList[i],varibles.recordUrlList[i]))
            varibles.saveFlag = True
        except:
            pass
        for j in range(0,len(varibles.recordAuthorList[i])):
            cursor.execute(sv_id_author,(id,varibles.recordAuthorList[i][j]))
        for j in range(0,len(varibles.recordIncludedList[i])):
            cursor.execute(sv_id_included,(id,varibles.recordIncludedList[i][j]))
        for j in range(0,len(varibles.recordIndexTermList[i])):
            cursor.execute(sv_id_indexTerm,(id,varibles.recordIndexTermList[i][j]))
    varibles.connection.commit()

def saveCrawl(kw, spendTime,savedRecords):
    sv_crawlLog = "INSERT INTO crawlLog(crawlTime,searchWord,savedAmount,spendTime) VALUES(%s,%s,%s,%s);"
    with varibles.connection.cursor() as cursor:
        cursor.execute(sv_crawlLog,((int)(time.time()),kw,savedRecords,spendTime))
    varibles.connection.commit()

def updateCrawl(kw,spendTime,savedRecords):
    up_crawlLog = "UPDATE crawlLog SET savedAmount=%s,spendTime=%s WHERE searchWord=%s;"
    with varibles.connection.cursor() as cursor:
        cursor.execute(up_crawlLog,(savedRecords,spendTime,kw))
    varibles.connection.commit()
    cursor.close()

def errorLog(errorName,kw):
    sv_errorLog = "INSERT INTO errorLog(errorTime,searchWord,errorName) VALUES(%s,%s,%s)"
    with varibles.connection.cursor() as cursor:
        cursor.execute(sv_errorLog,((int)(time.time()),kw,errorName))
    varibles.connection.commit()
    cursor.close()

def createBloomFilter():
    se_savedUrl = "SELECT id FROM record;"
    with varibles.connection.cursor() as cursor:
        cursor.execute(se_savedUrl)
        savedUrl = cursor.fetchall()
    varibles.f = BloomFilter(capacity = len(savedUrl) + varibles.keyWordsAmount * 1000, error_rate=0.0000001)
    for i in range(0,len(savedUrl)):
        varibles.f.add(savedUrl[i]['id'])

def bloomCheck(id):
    return (id in varibles.f)

def addIdToFilter(id):
    varibles.f.add(id)