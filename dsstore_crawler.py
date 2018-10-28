#!/bin/env python3
from ds_store import DSStore # pip3 install ds_store
import requests
import logging
import sys
"""
.DS_Store crawler

Author: Chimi <MindTheBox>
License: Don't sue me

About:
    Crawls directories looking for .DS_Store files that leak information
    about other directories and files that might not be easy to
    find otherwise.

    This will write the DS_Store files to the directory that the script is
    ran in. Be wary if you are going to be crawling a large amount of
    DS_Store files.
"""

logging.basicConfig(level=logging.INFO)

if len(sys.argv) < 2:
    logging.error("Usage: %s <http://target/>" % (sys.argv[0]))
    exit(-1)


url = sys.argv[1]
if url[-1] != "/":
    url += "/"


def download_store(u):
    logging.debug('Downloading from url: %s' % (u))
    r = requests.get("%s.DS_Store" % (u))
    if r.status_code != 200:
        logging.debug('Non 200 response, no DS_Store')
        return None
    filename = '%sDS_Store' % (u.lstrip(url).replace('/', '_'))
    with open(filename, 'wb') as f:
        f.write(r.content)
    logging.debug('Saved file to %s' % (filename))
    return filename


def get_dirs(s):
    logging.debug('Getting data from ds_store %s' % (s))
    store = DSStore.open(s)
    ds = []
    fs = []
    for b in store:
        if b.code == b'Iloc':
            if b.filename not in ds:
                fs.append(b.filename)
        if b.code == b'vSrn':
            if b.filename in fs:
                fs.remove(b.filename)
            ds.append(b.filename)
    logging.debug("Found %d files and %d directories" % (len(fs), len(ds)))
    return ds, fs


scoured_dirs = []
directories = ['']
filenames = []
while len(directories) != len(scoured_dirs):
    for d in directories:
        if d in scoured_dirs:
            continue
        new_dir = "%s%s" % (url, d)
        scoured_dirs.append(d)
        store = download_store(new_dir)
        if store != None:
            new_dirs, new_files = get_dirs(store)
            for nd in new_dirs:
                directories.append("%s%s/" % (d, nd))
            for f in new_files:
                filenames.append("%s%s" % (d, f))


logging.info("Directories:")
for d in directories:
    logging.info("%s%s" % (url, d))


logging.info("Files:")
for f in filenames:
    logging.info("%s%s" % (url, f))

