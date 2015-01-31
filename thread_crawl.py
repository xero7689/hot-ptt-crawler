# -*- coding: utf-8 -*-
__author__ = 'xero-mac'

import hotboard
import pttCrawler
import threading
import Queue

boards = hotboard.hotboard()
boards = boards[:5]
boards_queue = Queue.Queue(maxsize=0)
for board in boards:
    boards_queue.put(board)


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
    threads = []
    num_of_thread = 5
    for i in range(num_of_thread):
        ct = threading.Thread(target=thread_crawl, args=("new",))
        threads.append(ct)
        ct.start()

if __name__ == "__main__":
    main()