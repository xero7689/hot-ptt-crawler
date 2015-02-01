# -*- coding: utf-8 -*-
""" A Python Ptt Article Crawler
"""
import os
import urllib
import urllib2
import time
import json
import datetime
from bs4 import BeautifulSoup
import logging


class PttCrawler():
    """
    Given parameters are the board name, and dead line.
    The output is a json file which contains the
    """
    def __init__(self, board, days=1, save_dir=None):
        """
        Args
        """
        # Url Setting
        self.site = "https://www.ptt.cc"
        self.title = "bbs"
        self.board = board
        self.start_url = "{}/{}/{}/{}".format(self.site, self.title, self.board, "index.html")

        # Fetch days
        self.days = days

        # Debug Logger Setting
        logging.basicConfig(filename="pttCrawler.log", level=logging.DEBUG)
        self.logger = logging.getLogger()

        # Url Request Setting
        self.opener = self.create_opener()
        self.delay = 0.2

        # Data Path Setting
        self.working_path = os.path.dirname(os.path.abspath(__file__))

        if save_dir:
            save_path = os.path.join(self.working_path, save_dir)
            if not os.path.isdir(save_path):
                os.mkdir(save_path)
        else:
            save_path = self.working_path
        self.save_path = os.path.join(save_path, self.board)
        self.makedir()

    def run(self):
        # Update init
        url = self.start_url
        end_date = self.get_end_date(self.days)

        # update loop
        while True:
            soup = self.get_soup(url)
            max_date = self.get_post(soup)
            url = self.get_prev_link(soup)

            # Time to break, may have a bug.
            if end_date > max_date:
                break

    def create_opener(self):
        cookies = urllib2.HTTPCookieProcessor()
        opener = urllib2.build_opener(cookies)
        data_encoded = urllib.urlencode({"from": "/{}/{}/{}".format(self.title, self.board, "/index.html"), "yes": "yes"})
        opener.open("https://www.ptt.cc/ask/over18", data_encoded)
        return opener

    def get_soup(self, url):
        while True:
            try:
                source_page = self.opener.open(url)
                break
            except urllib2.URLError:
                self.logger.debug("Operation time out.")
                time.sleep(self.delay)
        return BeautifulSoup(source_page)

    def get_post(self, soup):
        """Get Posts from a soup object, and return a dictionary of these posts.
        """
        tmp_posts = soup.body.find_all('div', class_='r-ent')
        tmp_posts.reverse()

        max_date = None

        for tmpPost in tmp_posts:
            try:
                href = tmpPost.a['href']
                hl = href.split("/")

                article = self.get_article(href)

                # Dump to json
                fn = os.path.join(self.save_path, hl[3] + ".json")
                with open(fn, 'w') as f:
                    json.dump(article, f)

                print article['date'] + "-" + article['title']

                """Date analysis
                Transform string of date into datetime module format, which can be used to compare.
                """
                try:
                    dl = article['date'].split(" ")
                    adl = []

                    # Sometimes the element u'' will exist in the list and cause bug.
                    # , so I use this for loop to clean such element.
                    for t in dl:
                        if t != u'':
                            adl.append(t)
                    d = "{}/{}/{}".format(adl[2], adl[1], adl[4])
                    strp_date = datetime.datetime.strptime(d, "%d/%b/%Y")

                    if max_date == None:
                        max_date = strp_date
                    elif strp_date > max_date:
                        max_date = strp_date
                except Exception as e:
                    print(e.message)
                    break
            except UnboundLocalError as ule:
                self.logger.debug(ule.message)
                continue
            except IndexError as ie:
                self.logger.debug(ie.message)
                continue
            except TypeError as te:
                self.logger.debug(te.message)
                continue
        return max_date

    def get_article(self, href):
        # Deal Article
            article_url = "{}{}".format(self.site, href)
            article_soup = self.get_soup(article_url)
            content = article_soup.find("div", {"id": "main-content"})
            meta_value = content.find_all('span', class_='article-meta-value')

            article_author = meta_value[0].string
            article_title = meta_value[2].string
            article_date = meta_value[3].string

            pushes = len(content.find_all('div', class_="push"))

            article = dict()
            article['title'] = article_title
            article['author'] = article_author
            article['date'] = article_date
            article['pushes'] = pushes
            return article

    def get_prev_link(self, soup):
        button_group = soup.body.find_all('a', class_='btn wide')
        for btn in button_group:
            if u"上頁" in btn.string:
                return self.site + btn['href']

    def get_cur_date(self):
        """ Format current python date to Ptt date
        """
        if time.localtime().tm_mday in [day for day in range(1,10)]:
            return str(time.localtime().tm_mon) + '/' + '0' + str(time.localtime().tm_mday)
        else:
            return str(time.localtime().tm_mon) + '/' + str(time.localtime().tm_mday)

    def get_end_date(self, endDays):
        cur = datetime.datetime.now()
        return cur - datetime.timedelta(endDays)

    def makedir(self):
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)

if __name__ == "__main__":
    crawl = PttCrawler("Gossiping", 2)