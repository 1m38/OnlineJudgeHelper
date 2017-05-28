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
import warnings


def detect_site(url):
    re_list = {
        "AtCoder": re.compile(r"http://.*\.atcoder\.jp"),
        "Codeforces": re.compile(r"http://codeforces\.com")
    }
    for sitename, pattern in re_list.items():
        if pattern.match(url):
            return sitename


class ContestSite(object):
    url_format = None
    login_url = None
    site_name = None

    def __init__(self, url, config):
        if self.site_name is None:
            raise NotImplementedError
        self.url = url
        self.contest, self.pnumber = self.parse_url()
        if self.contest is None:
            self.contest = self.site_name
        self.s = requests.Session()
        if self.login_url is not None:
            self._login(config)
        self.page = self.get()
        self.testcases = self.parse_page(self.page)

    def result(self):
        return self.contest, self.pnumber, self.testcases

    def parse_url(self):
        if self.url_format is None:
            raise NotImplementedError
        r = parse.parse(self.url_format, self.url)
        contest = r["contest"] if "contest" in r.named.keys() else None
        pnumber = r["pnumber"] if "pnumber" in r.named.keys() else None
        return contest, pnumber

    def _login(self, config):
        if self.site_name not in config["sites"]:
            warnings.warn(
                "User credential for contest site {} not in config.json".format(self.site_name),
                RuntimeWarning)
            return
        else:
            self.username = config["sites"][self.site_name]["username"]
            self.password = config["sites"][self.site_name]["password"]
        try:
            login_status = self.login()
            if not login_status:
                raise RuntimeWarning("Failed to login")
        except:
            warnings.warn("Failed to login", RuntimeWarning)

    def login(self):
        raise NotImplementedError

    def get(self):
        r = self.s.get(self.url)
        return r.text

    def parse_page(self, page):
        """parse task page"""
        """return: testcases [[input_str, output_str], ...]"""
        raise NotImplementedError


class AtCoder(ContestSite):
    url_format = "http://{contest}.contest.atcoder.jp/tasks/{pnumber}"
    login_url = "https://{contest}.contest.atcoder.jp/login"
    site_name = "AtCoder"

    def login(self):
        payload = {"name": self.username,
                   "password": self.password}
        url = self.login_url.format(contest=self.contest)
        r = self.s.post(url, payload)
        if r.status_code != 200:
            warnings.warn("Login request returns status code {}".format(r.status_code),
                          RuntimeWarning)
        else:
            if "X-ImoJudge-SimpleAuth" in r.headers and \
               r.headers["X-ImoJudge-SimpleAuth"] == "Passed":
                return True
        return False

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


class Codeforces(ContestSite):
    url_format = "http://codeforces.com/contest/{contest}/problem/{pnumber}"
    # login_url = "http://codeforces.com/enter"
    login_url = None
    site_name = "Codeforces"

    def parse_page(self, page):
        testcases = []
        soup = BeautifulSoup(page, "html.parser")
        sample_test = soup.select("div.sample-test")[0]
        inputs = sample_test.find_all("div", class_="input")
        outputs = sample_test.find_all("div", class_="output")
        for i, o in zip(inputs, outputs):
            pre_i = i.find("pre")
            pre_o = o.find("pre")
            for br in pre_i.find_all("br"):
                br.replace_with("\n")
            for br in pre_o.find_all("br"):
                br.replace_with("\n")
            str_i = pre_i.text
            str_o = pre_o.text
            testcases.append([str_i, str_o])
        return testcases
