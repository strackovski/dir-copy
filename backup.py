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
Simple backup tool
~~~~~~~~~~~~~~~~~~
Author: Vladimir Strackovski <vlado@nv3.org>
"""

import os
import sys
import json
from Snapshot import Snapshot

__author__ = 'vstrackovski'

if not os.path.isfile('backup.json'):
    message = "Configuration is expected to be stored in backup.json, but no such file was found!\n"
    message += "Please run the setup tool (setup.py) to configure your backup instance."
    sys.exit('ERROR: ' + message)

with open('backup.json') as data_file:
    configs = json.load(data_file)

for config in configs:
    snapshot = Snapshot(config['source'], config['destinations'])
    snapshot.make()
    snapshot.transfer()