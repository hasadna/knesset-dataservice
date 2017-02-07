#!/usr/bin/env python
"""
Basic CLI to create the knesset-data datapackages

Simple interface to the relevant classes that do the actual work
"""
from knesset_data.datapackages.root import RootDatapackage
import os
import logging
import sys
import argparse
import zipfile

parser = argparse.ArgumentParser(description='Make a datapackage containing all Knesset data')
parser.add_argument('--days', type=int, default=5, help='generate data for last DAYS days where relevant (default is last 5 days)')
parser.add_argument('--force', action="store_true", help='force to continue, ignoring errors / warnings')
parser.add_argument('--include', nargs="*", type=str, help="include only datapackages / resources that start with the given string/s")
parser.add_argument('--exclude', nargs="*", type=str, help="exclude datapackages / resources that start with the given string/s")
parser.add_argument('--committee-id', nargs="*", type=int, help="only make data for the given committee ids")
parser.add_argument('--debug', action="store_true", help="provide more information and debug details")
parser.add_argument('--http-proxy', type=str, help='url to SOCKS http proxy')
parser.add_argument('--zip', action="store_true", help="create the datapackage in a zip file")
parser.add_argument('--all-committees', action="store_true", help="committees resource: fetch all committees, including historical")
parser.add_argument('--main-committees', action="store_true", help="committees resource: fetch only the active main committees")
parser.add_argument('--member-id', nargs="*", type=int, help="members resource: fetch only the given member id/s")

args = parser.parse_args()

logLevel = logging.DEBUG if args.debug else logging.INFO
[logging.root.removeHandler(handler) for handler in tuple(logging.root.handlers)]
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("%(name)s:%(lineno)d\t%(levelname)s\t%(message)s"))
stdout_handler.setLevel(logLevel)
logging.root.addHandler(stdout_handler)
logging.root.setLevel(logLevel)
logger = logging.getLogger()

data_root = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
if not os.path.exists(data_root):
    os.mkdir(data_root)

datapackage_root = os.path.join(data_root, 'datapackage')

logger.info("Generating data for the last {} days".format(args.days))
logger.info("Datapackage will be written in directory {}".format(datapackage_root))

if not os.path.exists(datapackage_root):
    os.mkdir(datapackage_root)
elif len(os.listdir(datapackage_root)) > 0 and not args.force:
    raise Exception('datapackage directory must be empty')

file_handler = logging.FileHandler(os.path.join(datapackage_root, "datapackage.log"))
file_handler.setFormatter(logging.Formatter("%(name)s:%(lineno)d\t%(levelname)s\t%(message)s"))
file_handler.setLevel(logging.INFO)
logging.root.addHandler(file_handler)

proxies = {proxy_type: proxy_url for proxy_type, proxy_url in {
    'http': args.http_proxy
}.iteritems() if proxy_url}

if len(proxies) > 0:
    logger.info('using proxies: {}'.format(proxies))

RootDatapackage(datapackage_root).make(days=args.days,
                                       force=args.force,
                                       exclude=args.exclude,
                                       include=args.include,
                                       committee_ids=args.committee_id,
                                       debug=args.debug,
                                       proxies=proxies,
                                       member_ids=args.member_id)

if args.zip:
    logger.info('creating datapackage.zip')
    zipf = zipfile.ZipFile(os.path.join(data_root, "datapackage.zip"), 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(datapackage_root):
        for file in files:
            real_file = os.path.join(root, file)
            rel_file = real_file.replace(data_root, "")
            zipf.write(real_file, rel_file)
    zipf.close()

logger.info('GREAT SUCCESS!')
