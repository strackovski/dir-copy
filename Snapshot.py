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

__author__ = 'vstrackovski'

import os
import errno
import subprocess
import shutil
import time
import math
import boto
import sys
from filechunkio import FileChunkIO
from hurry.filesize import size
from boto.exception import S3ResponseError


class Snapshot:
    """
    Snapshot class

    This class provides methods to compress all contents
    (first-level children) of the source directory and
    compress all resulting archives to the master archive
    for easy transfer.

    Additionally this class provides methods to transfer
    the master snapshot to configured destinations. Only
    locally accessible (mountable) paths and Amazon
    S3 Buckets are supported as destinations.
    """

    def __init__(self, source, destinations):
        """
        Constructor

        Attributes:
            source          absolute path to directory to backup
            destinations    list of local and remote backup destinations
            source_root     parent directory of source
            source_name     name of source directory
            temp_dir_name   name of temporary directory
            temp_dir_path   absolute path to temporary directory
            master_file     absolute path to master file when created
        """
        self.time = str(int(time.time()))
        self.source = source
        self.source_root = os.path.abspath(os.path.join(source, os.pardir))
        self.source_name = os.path.basename(os.path.normpath(source))
        self.destinations = destinations
        self.temp_dir_name = self.source_name + '-' + self.time
        self.temp_dir_path = self.source_root + '/' + self.temp_dir_name
        self.master_file = None

    def make(self):
        """Make snapshot"""
        print "\n**** BACKUP PARAMETERS ****\n"
        print "Backup source path: " + self.source
        print "Backup name: " + self.source_name
        print "Backup destinations: " + str(self.destinations)
        print "Temporary directory path: " + self.temp_dir_path
        print "\n**** RUNNING BACKUP ****\n"

        self.log_events('info', 'Backup from ' + self.source + ' to ' + str(self.destinations) +
                                ' with temporary path at ' + self.temp_dir_path)
        self.log_events('info', 'Starting backup name ' + self.source_name + '-' + self.time)
        self.__make_temp_dir()
        self.__compress_source_dirs()
        self.__verify_source_archives()
        self.__make_snapshot()

    def transfer(self):
        """Transfer snapshot"""
        self.__transfer_snapshot_local()
        self.__transfer_snapshot_s3()
        self.__cleanup()

    def __cleanup(self):
        """Remove temporary files and directories"""
        os.remove(self.master_file)

    def __make_temp_dir(self):
        """Create temporary directory to local space"""
        os.mkdir(self.temp_dir_path)
        if not os.path.isdir(self.temp_dir_path):
            self.log_events('fatal', 'Unable to create temporary directory at ' + self.temp_dir_path)
            raise Exception('Unable to create temporary directory at ' + self.temp_dir_path + ', aborting.')

        return self.temp_dir_path

    def __compress_source_dirs(self):
        """Compress individual child directories in the source directory"""
        # CHDIR to source dir to avoid unnecessary path nesting
        os.chdir(self.source)
        pipe = subprocess.PIPE
        source_count = 0

        for item in os.walk('.').next()[1]:
            source_count += 1
            self.log_events('info', 'Archiving dir #' + str(source_count) + ': ' + item)
            print('Archiving dir #' + str(source_count) + ': ' + item + '...')
            pd = subprocess.Popen(
                [
                    '/usr/bin/zip',
                    '-r',
                    self.temp_dir_path + '/' + item,
                    item
                ], stdout=pipe, stderr=pipe
            )
            stdout, stderr = pd.communicate()
            print stdout

    def __make_snapshot(self):
        """Compress all archives to master archive and remove temporary"""
        # source_root is the parent dir of source
        # it acts as a temp dir for the master snapshot
        self.master_file = self.source_root + '/' + self.source_name + '-' + self.time + '-master.zip'
        self.log_events('info', 'Creating master archive')
        print "Creating master archive..."
        os.chdir(self.temp_dir_path)
        pipe = subprocess.PIPE
        pd = subprocess.Popen(
            [
                '/usr/bin/zip',
                '-r',
                self.source_root + '/' + self.source_name + '-' + self.time + '-master',
                '.'
            ], stdout=pipe, stderr=pipe
        )
        stdout, stderr = pd.communicate()
        print stdout
        print "Removing temporary directory..."
        self.log_events('info', 'Removing temporary directory')
        shutil.rmtree(self.temp_dir_path)
        print "Master archive created successfully!"
        self.log_events('info', 'Master archive created successfully!')

    def __verify_source_archives(self):
        """Compare sources to archives"""
        sources = []
        archives = []

        for x in os.walk(self.source).next()[1]:
            sources.append(x)
            if os.path.isfile(self.temp_dir_path + '/' + x + '.zip'):
                archives.append(x)

        if len(archives) != len(sources):
            print "WARNING: Some backups failed, check log file!"
            self.log_events('warning', 'Source to archive count mismatch, some directories are missing.')
            missing = self.diff(sources, archives)
            self.log_events('warning', 'The following archives are missing: ' + str(missing))
        else:
            print "All sources archived successfully!"
            self.log_events('info', 'All sources archived successfully!')

    def __transfer_snapshot_local(self):
        """Transfer master archive to local backup destinations"""
        for dest in self.destinations['local']:
            if not os.path.isdir(dest):
                try:
                    os.makedirs(dest)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise
            print "Transferring master archive to destination " + dest + "..."
            self.log_events('info', 'Transferring master archive to destination ' + dest)
            if self.master_file is not None:
                shutil.copy2(self.master_file, dest)

            if not os.path.isfile(dest + '/' + self.source_name + '-' + self.time + '-master.zip'):
                self.log_events('info', 'Error transferring master archive to destination ' + dest)
                raise Exception('Error transferring master archive to destination ' + dest)

            print "Transfer to "+dest+" completed successfully!"
            self.log_events('info', 'Transfer to '+dest+' completed successfully!')

    def __transfer_snapshot_s3(self):
        """Transfer master archive to remote backup destinations"""
        c = boto.connect_s3()
        for bucket in self.destinations['s3']:
            try:
                b = c.get_bucket(bucket)
                self.log_events('info', 'Found bucket ' + bucket)
                sys.stdout.write('Found bucket ' + bucket + ', ')
                total_bytes = 0
                for key in b:
                    total_bytes += key.size
                sys.stdout.write('currently there is ' + size(total_bytes) + ' in it.\n')
            except S3ResponseError, e:
                if e.status == 404:
                    self.log_events('error', 'Bucket ' + bucket + ' not found, creating now')
                    print 'Bucket ' + bucket + ' not found, creating now...'
                    b = c.create_bucket(bucket)

            if b.get_all_multipart_uploads():
                print "This bucket contains lost files, you should remove them."

            self.log_events('info', 'Initiating remote upload')
            print "Initiating remote upload..."
            source_size = os.stat(self.master_file).st_size
            mp = b.initiate_multipart_upload(os.path.basename(self.master_file))
            chunk_size = 52428800
            chunk_count = int(math.ceil(source_size / chunk_size))

            self.log_events('info', 'Uploading '+size(source_size)+' to bucket ' + bucket)
            print 'Uploading '+size(source_size)+' to bucket ' + bucket

            for i in range(chunk_count + 1):
                offset = chunk_size * i
                bytes = min(chunk_size, source_size - offset)
                with FileChunkIO(self.master_file, 'r', offset=offset, bytes=bytes) as fp:
                    mp.upload_part_from_file(fp, part_num=i + 1)

            mp.complete_upload()
            print 'Transfer to bucket '+bucket+' completed successfully!'
            self.log_events('info', 'Transfer to bucket '+bucket+' completed successfully!')

    def log_events(self, level, message):
        """Log all events to instance log file"""
        log_file = open(self.source_root + '/'+self.source_name+'-'+self.time+'.log', 'a')
        log_file.write('['+level+'] ' + str(int(time.time())) + ' ' + message + '\n')
        log_file.close()

    @staticmethod
    def diff(a, b):
        """Compute list difference, ignoring item order and repetition."""
        b = set(b)
        return [aa for aa in a if aa not in b]