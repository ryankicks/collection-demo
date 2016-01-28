from __future__ import with_statement

import os
import django

SETTINGS_FILE = "app.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_FILE)
django.setup()

PORT = os.environ.get('PORT', 9000)

from fabric.api import *
from home.models import *

# run server locally
@task
def start():
    local("python manage.py runserver 127.0.0.1:%s --traceback --settings=%s" % (PORT, SETTINGS_FILE))
    
@task
def process():

    (collection_count, tweet_count) = Collection.process_all()
    print "Processed %s collections, totaling %s tweets." % (collection_count, tweet_count)


