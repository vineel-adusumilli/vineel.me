#!/usr/bin/env python

import os
import boto
from boto.s3.key import Key

DUMP_FILE = 'vineelme.dump'

# dump local db
os.system('pg_dump -Fc --no-acl --no-owner -h localhost -U vineelme vineelme > %s' % DUMP_FILE)

# upload to s3
conn = boto.connect_s3()
bucket = conn.get_bucket('vineel')
k = Key(bucket)
k.key = DUMP_FILE
k.set_contents_from_filename(DUMP_FILE)
url = k.generate_url(expires_in=3600)
print url

# sync to heroku
os.system('heroku pgbackups:restore --confirm vineel DATABASE "%s"'  % url)

# delete file
os.remove(DUMP_FILE)

