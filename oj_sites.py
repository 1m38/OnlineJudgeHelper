# coding: utf-8
"""docstring"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
import os
import sys
import codecs
import re
import collections
import requests
import parse
from bs4 import BeautifulSoup


def detect_site(url):
    re_list = {
        "AtCoder": re.compile(r"http://.*\.atcoder\.jp")
    }
    for sitename, pattern in re_list.items():
        if pattern.match(url):
            return sitename


class AtCoder(object):
    url_format = "http://{contest}.contest.atcoder.jp/tasks/{pnumber}"
    login_url = "https://{contest}.contest.atcoder.jp/login"
    def __init__(self, url, config):
        self.url = url
        self.contest, self.pnumber = self.parse_url()
        self.username = config["sites"]["AtCoder"]["username"]
        self.password = config["sites"]["AtCoder"]["password"]
        self.s = requests.Session()
        self.login()
        self.page = self.get()
        self.testcases = self.parse_page(self.page)

    def result(self):
        return self.contest, self.pnumber, self.testcases

    def parse_url(self):
        r = parse.parse(AtCoder.url_format, self.url)
        return r["contest"], r["pnumber"]

    def login(self):
        payload = {"name": self.username,
                   "password": self.password}
        url = AtCoder.login_url.format(contest=self.contest)
        self.s.post(url, payload)

    def get(self):
        r = self.s.get(self.url)
        return r.text

    def parse_page(self, page):
        testcases = []
        soup = BeautifulSoup(page, "html.parser")
        task = soup.find("div", {"id": "task-statement"})
        task_ja = task.find("span", {"class": "lang-ja"})
        if not task_ja:
            task_ja = task
        pres = task_ja.findAll("pre")
        n_pres = len(pres)
        for i in range(1, n_pres, 2):
            input_str = pres[i].text.replace("\r\n", "\n").strip() + "\n"
            output_str = pres[i+1].text.replace("\r\n", "\n").strip() + "\n"
            testcases.append([input_str, output_str])
        return testcases
