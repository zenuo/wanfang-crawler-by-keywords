#数据库相关变量
dbIPAddr = '127.0.0.1'
dbUser = 'crawler'
dbPassword = '123456a'

#爬取过程全局变量
keyWordsAmount = 0
recordAmount = 0
recordUrlList = [''] * 10
recordTitleList = [''] * 10
recordAuthorList = [''] * 10
recordSourceList = [''] * 10
recordDateList = [''] * 10
recordCategoryList = [''] * 10
recordIncludedList = [''] * 10
recordIndexTermList = [''] * 10
recordMajorList = [''] * 10
intro = ''
bsObj = None
f = None
connection = None
errorFlag = None
saveFlag = False
kw = ''
Url = ''
typeName = ''