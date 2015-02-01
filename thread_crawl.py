# -*- coding: utf-8 -*-
__author__ = 'xero-mac'

import hotboard
import pttCrawler
import analysis
import threading
import Queue
import os
import json
import time

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


def main():
    while True:
        try:
            # Crawling
            """
            print "Get hot board"
            boards = hotboard.hotboard()
            boards = boards[:5]
            for board in boards:
                boards_queue.put(board)

            threads = []
            num_of_thread = 5
            for i in range(num_of_thread):
                ct = threading.Thread(target=thread_crawl, args=("new",))
                threads.append(ct)
                ct.start()
            for thread in threads:
                thread.join()
            """

            """ Analysis """
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

            # modify dir
            old_path = os.path.join(work_path, "old")
            new_path = os.path.join(work_path, "new")
            bak_path = os.path.join(work_path, "old_" + '_'.join([x for x in time.ctime().split(' ') if x != ''][1:]))
            os.rename(old_path, bak_path)
            os.rename(new_path, old_path)

            break
        except Exception as e:
            print e.message
            break

if __name__ == "__main__":
    main()