from __future__ import with_statement

import os

from fabric.api import *
from fabric.contrib import django

SETTINGS_FILE = "app.settings"
django.settings_module(SETTINGS_FILE)

from home.models import *

PORT = os.environ.get('PORT', 9000)

# run server locally
def start():
    local("python manage.py runserver 127.0.0.1:%s --traceback --settings=%s" % (PORT, SETTINGS_FILE))
    
@task
def process():

    (collection_count, tweet_count) = Collection.process_all()
    print "Processed %s collections, totaling %s tweets." % (collection_count, tweet_count)


