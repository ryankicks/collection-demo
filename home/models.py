import os
import sys

from time import sleep
from datetime import date, datetime, timedelta

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from audit.models import AuditedModel, Access

class Collection(AuditedModel):
    
    name = models.CharField(max_length=100, null=False, blank=False)
    list_slug = models.CharField(max_length=100, null=False, blank=False)
    list_name = models.CharField(max_length=100, null=False, blank=False)
    collection_id = models.CharField(max_length=100, null=False, blank=False)
    collection_name = models.CharField(max_length=100, null=False, blank=False)
    retweet_count = models.PositiveIntegerField(null=True, blank=True, default=0)
    favorite_count = models.PositiveIntegerField(null=True, blank=True, default=0)
    engagement_count = models.PositiveIntegerField(null=True, blank=True, default=0) 
    block_words = models.CharField(max_length=2400, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    def new_url(self):
        return "/collection/new"

    def edit_url(self):
        if self.id:
            return "/collection/%s/edit" % self.id
        else:
            return "/collection/new"

    def delete_url(self):
        return "/collection/%s/delete" % self.id

    def list_url(self):
        return "/collection/list"

    def __unicode__(self):
        return "<Collection: %s, %s, %s, %s>" % (self.id, self.name, self.list_slug, self.collection_id)