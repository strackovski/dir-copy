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
  backup
  ~~~~~~~
    Simple backup tool
    Author: Vladimir Strackovski <vlado@nv3.org>
"""

__author__ = 'vstrackovski'

import os
import math
import subprocess
import time
import boto
import sys
from filechunkio import FileChunkIO
from hurry.filesize import size
import json
from operator import itemgetter
import datetime

PIPE = subprocess.PIPE


def compress_children(origin_dir):
    os.chdir(origin_dir)
    snapshots_dir_name = origin_dir + '-snapshots'
    if not os.path.isdir('../' + snapshots_dir_name):
        os.mkdir(snapshots_dir_name)

    for current_dir in os.walk('.').next()[1]:
        sys.stdout.write('Backing up ' + current_dir + '...')
        pd = subprocess.Popen(['/usr/bin/zip', '-r', '../' + snapshots_dir_name + '/' + current_dir, current_dir], stdout=PIPE, stderr=PIPE)
        stdout, stderr = pd.communicate()
        sys.stdout.write('DONE')
        print ""


def create_master_snapshot(src_dir, dest_file):
    os.chdir(src_dir)
    snapshot_name = dest_file + str(int(time.time()))
    sys.stdout.write("Creating snapshot " + snapshot_name + "...")
    pd2 = subprocess.Popen(['/usr/bin/zip', '-r', '../' + snapshot_name, src_dir], stdout=PIPE, stderr=PIPE)
    stdout, stderr = pd2.communicate()
    sys.stdout.write('DONE')
    print ""
    return snapshot_name


def purge_s3(bucket, name):
    c = boto.connect_s3()
    b = c.get_bucket(bucket)

    snapshots = []
    for key in b:
        if name in str(key):
            #print str(key)

            first = str(key).index(name) + len(name)
            last = str(key).index('.zip')

            #print first
            #print last

            snapshots.append({'timestamp': str(key)[first:last], 'file': str(key)[str(key).index(',')+1:len(str(key))-1]})
            #print str(key)[first:last]

    #print snapshots
    print ""
    newlist = sorted(snapshots, key=itemgetter('timestamp'), reverse=False)

    #print newlist

    for time in snapshots:
        print datetime.datetime.fromtimestamp(int(time['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')


def upload_s3(bucket, source_path, backup_name):
    c = boto.connect_s3()
    b = c.get_bucket(bucket)

    total_bytes = 0
    for key in b:
        total_bytes += key.size

    print size(total_bytes)

    #if total_bytes >= 4900000000:

    if b.get_all_multipart_uploads():
        print "This bucket contains lost files..."

    print "Initiating remote upload..."
    source_size = os.stat(source_path).st_size
    mp = b.initiate_multipart_upload(os.path.basename(source_path))
    chunk_size = 52428800
    chunk_count = int(math.ceil(source_size / chunk_size))

    sys.stdout.write('Uploading backup ('+size(source_size)+') to S3 in ')
    sys.stdout.flush()

    for i in range(chunk_count + 1):
        sys.stdout.write(str(i+1) + ' chunk(s) of ' + size(chunk_size) + ': ')
        sys.stdout.flush()
        offset = chunk_size * i
        bytes = min(chunk_size, source_size - offset)
        with FileChunkIO(source_path, 'r', offset=offset, bytes=bytes) as fp:
            sys.stdout.write('.')
            sys.stdout.flush()
            mp.upload_part_from_file(fp, part_num=i + 1)

    print ' combining...'
    mp.complete_upload()
    print 'Upload to S3 complete.'


with open('config.json') as data_file:
    config = json.load(data_file)

for item in config:
    os.chdir(item['origin_dir'])
    #compress_children(item['origin_dir'])
    #current_snapshot = create_master_snapshot('../' + item['origin_dir'] + '-snapshots', item['backup_name'])
    #upload_s3(item['s3_bucket'], '../' + current_snapshot + '.zip', item['backup_name'])
    purge_s3(item['s3_bucket'], item['backup_name'])