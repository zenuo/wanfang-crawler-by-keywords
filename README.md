# crawler
> Get data from wanfang pages.

## 使用说明
## 一、在Mysql上建立用户和数据库
### 安装MariaDB的步骤请移步
```
https://github.com/yziyz/note/blob/master/CentOS_Install_MariaDB.md
```
### 以root用户登录mysql后，新建用户"crawler":
```
CREATE USER "crawler"@"YOUR_CLIENT_IP" IDENTIFIED BY "123456";
```
### 将数据库的所有权限赋给"crawler":
```
GRANT ALL PRIVILEGES ON *.* TO  "crawler"@"YOUR_CLIENT_IP";
```
YOUR_CLIENT_IP means the ip of your client to connect mysql server;
if you installed mysql on docker,and run crawler on host machine,you can run
```
sudo docker inspect CONTAINER_ID | grep \"Gateway\"
```
to check it.
### 退出；使用用户“crawler”登录后新建数据库"cnki":
```
CREATE DATABASE wanfang DEFAULT CHARACTER SET utf8mb4;
```
## 二、安装Python3和依赖模块
### 安装Python3的步骤请移步
```
https://github.com/yziyz/note/blob/master/CentOS_Install_Python3.md
```
### 安装PyMySQL,bitarray,BeautifulSoup4,lxml：
```
sudo pip3 install PyMySQL bitarray BeautifulSoup4 lxml requests
```
### 安装Python布隆过滤器
```
sudo yum install git
cd ~
git clone https://github.com/jaybaird/python-bloomfilter.git
cd python-bloomfilter
sudo python3 setup.py install
cd ~ & rm -rf python-bloomfilter
```
## 三、下载程序
在"crawler"文件夹下运行：
```
cd ~ & git clone https://github.com/yziyz/crawler.git
```
## 四、配置
### 数据库服务器IP
编辑varibles.py文件
```
vi ~/crawler/varibles.py
```
将dbIPAddr改为数据库服务器IP（默认localhost），例如改为192.168.1.2
```
dbIPAddr = '192.168.1.2'
```
保存更改并退出

### 关键词
在"crawler"文件夹下新建文本文件，例如新建1.txt：
```
vi ~/crawler/1.txt
```
每行填写一个关键词：
```
KeyWord1
KeyWord2
KeyWord3
```
保存更改并退出

## 五、运行

运行爬虫程序：
```
cd ~/crawler
python3 wanfang.py
```
提示:
```
Please input the keywords list file's name:
```
再输入关键词文本文件名"1.txt"，回车即可开始爬取:
```
Read file completed,  3 key word(s):
"KeyWord1" "KeyWord2" "KeyWord3"

Now crwal work start
```
爬取完成后结束。
