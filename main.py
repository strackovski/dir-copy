import os
import json
import time
import subprocess

__author__ = 'ndolinar'


def compress_dir(path, dest):
    os.chdir(path)
    dir_name = os.path.basename(os.path.normpath(path)) + '-' + str(int(time.time()))
    PIPE = subprocess.PIPE

    if not os.path.isdir(dest):
        os.mkdir(dest)

    if not os.path.isdir(dest + '/' + dir_name):
        os.mkdir(dest + '/' + dir_name)

    for dir in os.walk('.').next()[1]:
        pd = subprocess.Popen(
            [
                '/usr/bin/zip',
                '-r',
                dest + '/' + dir,
                dir
            ], stdout=PIPE, stderr=PIPE
        )

        stdout, stderr = pd.communicate()
        print stdout

    print os.getcwd()

with open('config2.json') as data_file:
    configs = json.load(data_file)

# check source
# create target dir
# compress
for config in configs:
    # print config['destinations']['local']

    for item in config['destinations']['local']:
        compress_dir(config['source'], item)
