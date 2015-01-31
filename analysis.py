# -*- coding: utf-8 -*-
__author__ = 'xero-mac'
""" Analysis the Ptt json file
"""

import os
import json

new_dir = 'new'
old_dir = 'old'

board_meta_data = "hotboard.json"

work_path = os.path.curdir
new_path = os.path.join(work_path, new_dir)
old_path = os.path.join(work_path, old_dir)

comment_threshold = 20


def num_of_article(board_name):
    nd = os.listdir(os.path.join(new_path, board_name))
    od = os.listdir(os.path.join(old_path, board_name))

    noa_dev = len(nd) - len(od)
    return board_name, noa_dev



def popular():
    """ Find and Rank the Popular Board
    """
    new_board = []
    rank_up = []
    old = open(os.path.join(old_path, board_meta_data))
    new = open(os.path.join(new_path, board_meta_data))

    # old data loading
    oldjson = json.loads(old.read())
    oldkey = oldjson.keys()
    oldvalue = oldjson.values()

    # new data loading
    newjson = json.loads(new.read())
    newkey = newjson.keys()
    newvalue = newjson.values()

    for i in range(0, len(newkey)-1):
        if newkey[i] in oldkey:
            for j in range(0, len(oldkey)-1):
                if oldkey[j] == newkey[i]:
                    if newvalue[i] < oldvalue[j]:
                        # rank up board
                        rank_up.append(newkey[i])
        else:
            # new hot board
            new_board.append(newkey[i])

    return rank_up, new_board


def compare_comment():
    """This is a generator which compare the pushes between new article and old article, and yield the file name if it's
    deviation is larger than threshold.
    """
    fsa = find_same_article()
    while True:
        try:
            nfp, ofp = fsa.next()
            tmpnf = open(nfp, 'r')
            tmpof = open(ofp, 'r')
            nfjs = json.load(tmpnf)
            ofjs = json.load(tmpof)

            pushdev = nfjs['pushes'] - ofjs['pushes']

            if pushdev > comment_threshold:
                yield nfp, pushdev
        except Exception as e:
            print e
            break
        finally:
            tmpnf.close()
            tmpof.close()


def find_same_dir():
    """This is a generator of same dirs which exists both new dir and old dir.
    output (tuple): (new_dir, old_dir)
    """
    new_dirs = os.listdir(new_path)
    old_dirs = os.listdir(old_path)

    for nd in new_dirs:
        for od in old_dirs:
            if nd == od:
                if not os.path.isfile(os.path.join(new_path, nd)):
                    yield (os.path.join(new_path, nd), os.path.join(old_path, od))


def find_same_article():
    sd = find_same_dir()
    while True:
        try:
            np, op = sd.next()
            nfs = os.listdir(np)
            ofs = os.listdir(op)

            for nf in nfs:
                for of in ofs:
                    if nf == of:
                        yield (os.path.join(np, nf), os.path.join(op, of))
        except Exception as e:
            print e
            break


def main():
    rk, nb = num_of_article("LoL")
    print rk
    print nb

if __name__ == "__main__":
    main()