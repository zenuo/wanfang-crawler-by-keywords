from methods import connectDB,disconnectDB,createTable,readFile,createBloomFilter,crawlSearchPage
import varibles

if __name__ == '__main__':
    connectDB()
    createTable()
    print("Please input the keywords list file's name:")
    #提示输入关键词文件路径
    fileName = input()
    #打开文件并将其转为list
    kwList = readFile(fileName).splitlines()
    #文件中关键词总数
    varibles.keyWordsAmount = len(kwList)
    #createBloomFilter()
    #打印关键词
    print("Found %d"% varibles.keyWordsAmount + " key word(s):")
    print("--------------------------------------------------------------------------")
    for i in range(len(kwList)):
        print("\"%s\" " % kwList[i],end="")
        if i == len(kwList) - 1:
            print("\n--------------------------------------------------------------------------")
    print("Now crawl work start")
    #开始爬取
    for s in kwList:
        print("Keyword is \"%s\""% s)
        varibles.kw = s
        varibles.typeName = 'QK'
        crawlSearchPage()
        varibles.typeName = 'XW'
        crawlSearchPage()
    disconnectDB()
    #结束爬取，提示
    print("%d crawl work done."% len(kwList))
