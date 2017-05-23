from methods import crawlPaperPage,connectDB,disconnectDB

if __name__ == '__main__':
    connectDB()
    start = (int)(input('Input the sequence number of you run:\n'))
    crawlPaperPage(start)
    disconnectDB()