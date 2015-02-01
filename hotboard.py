# -*- coding: utf-8 -*-

import urllib2
import re
import json
import os
from bs4 import BeautifulSoup
from collections import OrderedDict

save_path = os.path.join(os.path.curdir, "new")

def hotboard():
    url = "https://www.ptt.cc/hotboard.html"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    board = []
    flag = 0
    popular = []
    output = OrderedDict()
    p = re.compile(r'<.*?>')

    for lind in soup.find_all('td', {'width':'120'}):
        temp = p.sub('', lind.renderContents().strip())
        if flag % 2 == 0:
            board.append(temp)
        flag += 1

    for lind in soup.find_all('td', {'width': '100'}):
        temp = p.sub('', lind.renderContents().strip())
        popular.append(temp[9:16])

    for i in range(0,len(board)-1):
        output[board[i]] = (i + 1, popular[i])

    data_string = json.dumps(output)

    fn = os.path.join(save_path, "hotboard.json")
    f = open(fn, 'w')
    f.write(data_string)
    f.close()

    return board