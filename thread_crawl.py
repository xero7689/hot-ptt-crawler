# -*- coding: utf-8 -*-
__author__ = 'xero-mac'

import hotboard
import pttCrawler
import analysis
import threading
import Queue
import os
import time
import urllib2
import json
import shutil

boards_queue = Queue.Queue(maxsize=0)
work_path = os.path.curdir
output_path = os.path.join(work_path, 'www')


def thread_crawl(save_dir=None):
    while not boards_queue.empty():
        try:
            bn = boards_queue.get()
            boards_queue.task_done()
            print "{}: ".format(bn)
            print threading.current_thread()
            crawler = pttCrawler.PttCrawler(bn, 2, save_dir)
            crawler.run()
        except Exception as e:
            print e.message


def pushMessage():
    GCM_SERVER = "https://android.googleapis.com/gcm/send"
    output_data = json.loads(open("./www/output.json","r").read())
    if len(output_data["board"])==0 and len(output_data["article"])==0:
        return None
    # output report html file
    with open("./www/module.html") as f:
                mod = f.read()
    hot_board = ""
    if len(output_data["board"]) != 0:
        board_list = ""
        for b in output_data["board"]:
            board_list += u'<li><a href="https://www.ptt.cc/bbs/%s/index.html">%s</a></li>' % (b, b)
        hot_board = mod % (u"熱門討論版", board_list)

    hot_article = ""
    if len(output_data["article"]) != 0:
        article_list = ""
        for a in output_data["article"]:
            article_list += u'<li><a href="https://www.ptt.cc/bbs%s">%s</a></li>' % (a["url"][5:], a["title"])
        hot_article = mod % (u"熱門文章", article_list)

    with open("./www/index-form.html", "r") as f:
        form = f.read()
    with open("./www/index.html","w") as f:
        f.write(form % (hot_board.encode("utf-8"), hot_article.encode("utf-8")))
    # push message to user
    regId = [i.replace("\n", "") for i in open("id.txt", "r")]
    print regId
    json_data = {"data": {"msg": "http://140.127.208.93:8080/"}, "registration_ids": regId}
    data = json.dumps(json_data)
    headers = {'Content-Type': 'application/json',
    'Authorization': "key=AIzaSyAMZpkMhkF_k1clAbrK5ovDjy6fPBZTwyw"}
    req = urllib2.Request(GCM_SERVER, data, headers)
    res = urllib2.urlopen(req)
    response = json.loads(res.read())


def main():
    while True:
        try:
            # Crawling
            print "Get hot board"
            boards = hotboard.hotboard()
            boards = boards[:5]
            for board in boards:
                boards_queue.put(board)

            # Thread Crawling
            threads = []
            num_of_thread = 5
            for i in range(num_of_thread):
                ct = threading.Thread(target=thread_crawl, args=("new",))
                threads.append(ct)
                ct.start()
            for thread in threads:
                thread.join()


            # Analysis
            up_rank_board, new_board = analysis.popular()
            print up_rank_board
            print new_board

            # Article deviation of up_rank_board
            rslt_l = []
            for board in up_rank_board:
                try:
                    rslt =  analysis.num_of_article(board)
                    if rslt is not ():
                        rslt_l.append(rslt[0])
                except Exception as e:
                    print e.message

            # Get popular comments from each board
            pcl = []
            pc = analysis.popular_comment()
            while True:
                try:
                    file_path, push_dev = pc.next()
                    jf = open(file_path, 'r')
                    jl = json.load(jf)
                    pop_dict = dict()
                    url = file_path.split('.')
                    url.remove("json")
                    u = ".".join(url)
                    pop_dict['title'] = jl['title']
                    pop_dict['url'] = u
                    pcl.append(pop_dict)
                except StopIteration as si:
                    print si.message
                    break

            # Output
            output_dict = dict()
            output_dict['board'] = rslt_l
            output_dict['article'] = pcl
            fn = os.path.join(output_path, "output.json")
            print output_dict
            if not os.path.isdir(output_path):
                os.mkdir(output_path)
            with open(fn, "w") as f:
                json.dump(output_dict, f)

            # Send to android user
            pushMessage()

            # backup old dir
            backup_name = '_'.join([x for x in time.ctime().split(' ') if x != ''][1:])

            old_path = os.path.join(work_path, "old")
            new_path = os.path.join(work_path, "new")
            bak_path = os.path.join(work_path, "old_" + backup_name)
            os.rename(old_path, bak_path)
            os.rename(new_path, old_path)

            # backup index.html
            index_bak_path = os.path.join(output_path, "index_bak")
            index_bak_fn = os.path.join(index_bak_path, "index_" + backup_name)
            index_path = os.path.join(output_path, "index.html")
            if not os.path.isdir(index_bak_path):
                os.mkdir(index_bak_path)
            if os.path.isfile(index_path):
                shutil.copy(index_path, index_bak_fn)

        except Exception as e:
            print e.message
            # break

if __name__ == "__main__":
    main()