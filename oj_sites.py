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
    re_list = collections.OrderedDict()
    re_list["AtCoderBeta"] = re.compile(r"https?://.*\.atcoder\.jp")
    re_list["AtCoder"] = re.compile(r"https?://.*\.atcoder\.jp")
    re_list["Codeforces"] = re.compile(r"http://codeforces\.com")
    re_list["Yukicoder"] = re.compile(r"http://yukicoder\.me")
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
        try:
            self.testcases = self.parse_page(self.page)
        except:
            warnings.warn(
                "Failed to load testcases, so create a blank sample file.",
                RuntimeWarning)
            self.testcases = []

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


class AtCoderBeta(ContestSite):
    url_format = "https://beta.atcoder.jp/contests/{contest}/tasks/{pnumber}"
    login_url = "https://beta.atcoder.jp/login"
    site_name = "AtCoder"

    def login(self):
        payload = {"username": self.username,
                   "password": self.password}
        url = self.login_url
        # get csrf-token
        r = self.s.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        rform = soup.find_all("form")[-1]
        tokens = rform.find_all("input", type="hidden")
        for token in tokens:
            payload[token.attrs["name"]] = token.attrs["value"]
        r = self.s.post(url, payload)
        if r.status_code != 200:
            warnings.warn("Login request returns status code {}".format(r.status_code),
                          RuntimeWarning)
        elif r.url == "https://beta.atcoder.jp/login":
            warnings.warn("Failed to login. Is username or password incorrect?".format(r.status_code),
                          RuntimeWarning)
        else:
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


class Yukicoder(ContestSite):
    url_format = "http://yukicoder.me/problems/no/{pnumber}"
    login_url = None
    site_name = "yukicoder"

    def parse_page(self, page):
        testcases = []
        soup = BeautifulSoup(page, "html.parser")
        samples = soup.find_all("div", class_="sample")
        for sample in samples:
            pres = sample.find_all("pre")
            pre_i = pres[0]
            pre_o = pres[1]
            str_i = pre_i.text + "\n"
            str_o = pre_o.text + "\n"
            testcases.append([str_i, str_o])
        return testcases
