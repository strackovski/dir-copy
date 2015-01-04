#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Vladimir Strackovski vlado@nv3.org
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

"""
  backup setup tool
  ~~~~~~~~~~~~~~~~~~
    Simple backup tool
    Author: Vladimir Strackovski <vlado@nv3.org>
"""

__author__ = 'vstrackovski'

import json
import os
import sys


def prompt_user():
    origin_name = raw_input('A name for this backup: ')
    origin_dir = raw_input('Absolute path to directory to backup: ')
    backup_name = raw_input('Archive file name: ')
    s3_bucket = raw_input('Name of the S3 bucket for remote backup: ')
    new_cfg_dict = {'origin_name': origin_name, 'origin_dir': origin_dir, 'backup_name': backup_name, 's3_bucket': s3_bucket}

    return new_cfg_dict


def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

cfgList = []
if os.path.isfile('config.json'):
    try:
        cfgList = json.loads(open('config.json').read())
    except Exception:
        pass

configFile = open('config.json', 'w')
cfgList.append(prompt_user())

if query_yes_no('Add more origins?'):
    cfgList.append(prompt_user())

try:
    json.dump(cfgList, configFile, ensure_ascii=True)
except Exception:
    print 'Error dumping json data'

configFile.close()

# debug
with open('config.json') as data_file:
    config = json.load(data_file)

print config