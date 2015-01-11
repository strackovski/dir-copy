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
from crontab import CronTab


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def ask(question, options):
    """
    Simple select-option question helper

        question    The question to ask
        options     List of options to present as choices
    """
    if not isinstance(options, list):
        raise Exception('Invalid parameter options, expected dict')

    if len(options) < 1:
        raise Exception('Empty options list?')

    print question.capitalize()
    for v in options:
        print '[' + str(options.index(v)) + ']: ' + str(v).capitalize()

    uinput = raw_input('Select an option from the list above: ')
    while not is_int(uinput) or int(uinput) > len(options)-1:
        uinput = raw_input('Input should be an integer between 0 and ' + str(len(options)-1) + ':')

    return int(uinput)


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

    if __query_yes_no('Would you like to schedule this job using crontab?'):
        cron = CronTab()
        virt_py = os.path.dirname(os.path.realpath(__file__)) + '/nvbenv/bin/python '
        job = cron.new(command=virt_py + os.path.dirname(os.path.realpath(__file__)) + '/backup.py')

        day_of_month = '*'
        day_of_week = '*'
        month = '*'
        cron_strf = '{} {} {} {} {}'

        if __query_yes_no('Would you like this task to repeat?'):
            # Define repetition interval
            interval = ask('how would you like to repeat this backup task?', ['daily', 'weekly', 'monthly'])
            if interval == 0:
                pass
            elif interval == 1:
                dow = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
                day_of_week = ask('enter day of week', dow)
                print 'Chosen: ' + dow[day_of_week].capitalize()
            elif interval == 2:
                day_of_month = raw_input('Enter day of month [1-31]: ')
                while not is_int(day_of_month) or (int(day_of_month) > 31 or int(day_of_month) < 1):
                    day_of_month = raw_input('Enter day_of_month correctly! [1-31]: ')
        else:
            # Define the exact time of backup execution
            month = raw_input('Enter month of year [1-12]: ')
            while not is_int(month) or (int(month) > 12 or int(month) < 1):
                month = raw_input('Enter month_of_year correctly! [1-12]: ')

            day_of_month = raw_input('Enter day of month [1-31]: ')
            while not is_int(day_of_month) or (int(day_of_month) > 31 or int(day_of_month) < 1):
                day_of_month = raw_input('Enter day_of_month correctly! [1-31]: ')

        # Define hours and minutes (common to both scheduled and not)
        hours = raw_input('Enter hours [0-23]: ')
        while not is_int(hours) or (int(hours) > 23 or int(hours) < 0):
            hours = raw_input('Enter hours correctly! [0-23]: ')

        minutes = raw_input('Enter minutes [0-59]: ')
        while not is_int(minutes) or (int(minutes) > 59 or int(minutes) < 0):
            minutes = raw_input('Enter minutes correctly! [0-59]: ')

        # Construct a cron timing string
        cron_string = cron_strf.format(
            str(minutes),
            str(hours),
            str(day_of_month),
            str(month),
            str(day_of_week)
        )
        config['cron'] = cron_string
        job.setall(cron_string)
        cron.write()

    if __query_yes_no('Would you like to add local backup destination(s)?'):
        local = raw_input('Absolute path to local destination directory (will be created if non-existent): ')
        while not len(local) > 0 or not os.path.isabs(local):
            local = raw_input('Enter at lease one local destination directory (will be created if non-existent): ')
        local_destinations.append(local)

        while __query_yes_no("Add another local destination?", "no"):
            local = raw_input('Path to destination (will be created if non-existent): ')
            while not len(local) > 0 or not os.path.isabs(local):
                local = raw_input('Directory path must be absolute: ')
            local_destinations.append(local)

    if __query_yes_no('Would you like to add an S3 bucket as remote destination?'):
        s3_bucket = raw_input('S3 Bucket name (will be created if non-existent): ').lower()
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