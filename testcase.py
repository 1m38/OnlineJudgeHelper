# coding: utf-8
"""docstring"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
import sys
import re


class TestCase(object):
    re_testcase_mode = re.compile(r"/\* (.+) \*/")
    re_testcase_url = re.compile(r"^URL:(.+)$")

    def __init__(self, filepath, testcases=None, url=None):
        self.filepath = filepath
        if testcases is None:
            try:
                with open(filepath, "r") as f:
                    testcase_txt = f.read()
            except IOError as e:
                print("File '{}' can't open.".format(filename))
                raise e
            self.testcases, self.url = self.parse_testcase(testcase_txt)
        else:
            self.testcases = testcases
            self.url = url

    def save(self):
        testcase_str = self.format_testcase()
        with open(self.filepath, "w") as f:
            f.write(testcase_str)

    def parse_testcase(self, testcase_txt):
        test_list = []
        testcase_id = None
        tc = ["", ""]
        mode = None
        url = ""
        for line in testcase_txt.split("\n"):
            m = TestCase.re_testcase_mode.match(line)
            if m:
                if mode is not None and mode.startswith("Output"):
                    test_list.append(tc)
                    tc = ["", ""]
                mode = m.group(1)
                if mode.startswith("URL"):
                    url = TestCase.re_testcase_url.match(mode).group(1)
                    mode = None
            elif mode is not None:
                if mode.startswith("Test"):
                    tc[0] += line + "\n"
                elif mode.startswith("Output"):
                    tc[1] += line + "\n"
        # 末尾の改行を削除
        if mode is not None and mode.startswith("Output"):
            tc[1] = tc[1][:-1]
            test_list.append(tc)
        return test_list, url

    def add_testcase(self, test_str, out_str):
        self.testcases.append([test_str, out_str])

    def format_testcase(self):
        testcase_str = ""
        if self.url:
            testcase_str += "/* URL:{} */\n".format(url)
        for test_id in range(len(self.testcases)):
            testcase_str += "/* Test {} */\n".format(test_id)
            testcase_str += self.testcases[test_id][0]
            testcase_str += "/* Output {} */\n".format(test_id)
            testcase_str += self.testcases[test_id][1]
        return testcase_str
