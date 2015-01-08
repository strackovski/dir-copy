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
Backup configuration tool
~~~~~~~~~~~~~~~~~~
Author: Vladimir Strackovski <vlado@nv3.org>
"""

__author__ = 'vstrackovski'

import json
import os
import sys


def configure():
    """
    Prompt user for backup configuration parameters
    """

    print "Welcome to backup setup!\n"
    print "You can configure this tool to backup multiple sources"
    print "to multiple local locations and S3 buckets. Please provide"
    print "the required information to get going!\n"

    source = raw_input("Absolute path to backup source directory: ")
    while not os.path.isdir(source) or not os.path.isabs(source):
        print "Invalid source: directory " + source + " not found."
        source = raw_input("Absolute path to backup source directory: ")
    source_name = os.path.basename(os.path.normpath(source))
    config = {}
    destinations = {}
    local_destinations = []
    s3_buckets = []
    config['source'] = source
    config['source_name'] = source_name

    if __query_yes_no('Would you like to add local backup destination(s)?'):
        local = raw_input('Absolute path to local destination directory (will be created if non-existent): ')
        while not len(local) > 0 or not os.path.isabs(local):
            local = raw_input('Enter at lease one local destination directory (will be created if non-existent): ')
        local_destinations.append(local)

        while __query_yes_no("Add another local destination?", "no"):
            local = raw_input('Path to destination (will be created if non-existent): ')
            while not len(local) > 0 or not os.path.isabs(local):
                local = raw_input('Directory path must be absolute (will be created if non-existent): ')
            local_destinations.append(local)

    if __query_yes_no('Would you like to add S3 bucket(s) as remote destination(s)?'):
        s3_bucket = raw_input('S3 Bucket name (will be created if non-existent): ').lower()
        while not len(s3_bucket) > 0:
            s3_bucket = raw_input('S3 Bucket name can\'t be empty: ').lower()
        s3_buckets.append(s3_bucket)

        while __query_yes_no("Add another bucket?", "no"):
            s3_bucket = raw_input("Bucket name: ").lower()
            while not len(s3_bucket) > 0:
                s3_bucket = raw_input('S3 Bucket name can\'t be empty: ').lower()
            s3_buckets.append(s3_bucket)

    destinations['local'] = local_destinations
    destinations['s3'] = s3_buckets
    config['destinations'] = destinations

    return config


def __query_yes_no(question, default="yes"):
    """
    Simple yes/no question helper

    Attributes:
        question    The question to ask the user
        default     The default answer (yes/no)
    """
    valid = {"yes": True, "y": True,
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


configs = []
config = configure()
configs.append(config)
while __query_yes_no("Add another backup configuration?", "no"):
    configs.append(configure())

configFile = open('backup.json', 'w')
json.dump(configs, configFile, ensure_ascii=True)
print "Configuration saved to backup.json"