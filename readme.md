# dir-copy

A simple tool that creates snapshots of folders and transfers them to local and remote (S3) locations.

It compresses all contents (first-level children) of the source directory and compresses all resulting archives to the master archive for easy transfer to preconfigured destinations. Only locally accessible (mountable) paths and Amazon S3 Buckets are supported as destinations.

To configure your copy just run setup.py or create a "backup.json" configuration file according to the provided scheme (see backup.json.example). The configuration parameters are displayed bellow:

  - source - absolute path to directory to backup
  - destinations - list of local and remote backup destinations
  - source_name - name of source directory

It is recommended to use the setup.py tool as it generates most of the parameters on the fly.

### Todo

Data retrieval and restore procedure

### Support and requirements

This software is tested on UNIX systems, specifically on several Linux distributions and OS X. It relies on the following components:

* Python 2.6+
* [zip] - zip tool for linux/osx systems
* [boto] - Python interface to Amazon Web Services
* [filechunkio] - multipart upload library for Python
* [aws-cli] - cli tools for interfacing with Amazon AWS

To upload backup snapshots to Amazon S3 buckets, you will need to [install and configure the aws-cli tools].

### Version
0.0.9

[zip]:http://www.cyberciti.biz/tips/how-can-i-zipping-and-unzipping-files-under-linux.html
[boto]:https://github.com/boto/boto
[filechunkio]:https://pypi.python.org/pypi/filechunkio
[aws-cli]:http://aws.amazon.com/cli/
[install and configure the aws-cli tools]:http://docs.aws.amazon.com/cli/latest/userguide/installing.html
