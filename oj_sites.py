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
import lxml.html


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
        self.get()
        self.testcases = self.parse_page()

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
        self.page = r.text

    def parse_page(self):
        testcases = []
        root = lxml.html.fromstring(self.page)
        h3s = [e for e in root.xpath("//section/h3")
               if e.text.startswith("入力例")]
        i_sections = [e.getparent() for e in h3s]
        for e in i_sections:
            input_str = e.find("pre").text.replace("\r\n", "\n")
            output_section = e.getparent().getnext().find("section")
            output_str = output_section.find("pre").text.replace("\r\n", "\n")
            testcases.append([input_str, output_str])
        return testcases
