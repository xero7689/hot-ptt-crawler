#-*-coding:UTF-8 -*-

import urllib2,re,string,json
from bs4 import BeautifulSoup
from collections import OrderedDict
import pttCrawler
import threading


def hotboard():
    url = "https://www.ptt.cc/hotboard.html"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    board = []
    flag = 0;
    popular = []
    output = OrderedDict()
    p = re.compile(r'<.*?>')

    # 版名(finish)
    for lind in soup.find_all('td', {'width':'120'}):
        temp = p.sub('', lind.renderContents().strip())
        if (flag % 2 == 0):
            board.append(temp)
        flag = flag + 1;

    # 人氣(finish)
    for lind in soup.find_all('td',{'width':'100'}):
        temp = p.sub('',lind.renderContents().strip())
        popular.append(temp[9:16])


    # print popular 檢查用函數
    # print board

    # 輸出json
    for i in range(0,len(board)-1):
        output[board[i]]=(i + 1, popular[i])
        # (版名：(排名：人氣))
        # print board[i]

    data_string = json.dumps(output)

    # print data_string

    # 輸出檔案
    f = open('hotboard.json', 'w')
    f.write(data_string)
    f.close()

    # Call pttCrawler
    return board