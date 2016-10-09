# coding: utf-8
"""docstring"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
import sys
import re


re_testcase_comment = re.compile(r"/\* (.+) \*/")

def parse_testcase(qid):
    try:
        with open(qid + ".sample", "r") as f:
            testcase_txt = f.read()
    except IOError:
        print("File '{}' not found.".format(qid + ".sample"))
        sys.exit(1)
    test_list = []
    testcase_id = None
    for line in testcase_txt.split("\n"):
        m = re_testcase_comment.match(line)
        if m:
            testcase_id = m.group(1)
            test_list.append([testcase_id, ""])
        elif testcase_id is not None:
            test_list[-1][1] += line + "\n"
    # 末尾の改行を削除
    if testcase_id is not None:
        test_list[-1][1] = test_list[-1][1][:-1]
    return test_list


def add_testcase(qid, test_id, test_str, out_str):
    with open(qid + ".sample", "a") as f:
        f.write("/* Test {} */\n".format(test_id))
        f.write(test_str)
        f.write("/* Output {} */\n".format(test_id))
        f.write(out_str)
    print("Added test case {}.".format(test_id))
