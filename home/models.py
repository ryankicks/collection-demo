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

from home.utils import *

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
    include_retweets = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def process(self):
        
        added = []
        
        bw = None
        if self.block_words:
            bw = self.block_words.lower().split()
        
        api = Twitter.get_twitter(self.created_by)

        coll_tweet_ids = api.GetCollectionsEntries(self.collection_id)
        list_statuses = api.GetListTimeline(None, self.list_slug, owner_screen_name=self.created_by.username, include_rts=self.include_retweets)
        
        for s in list_statuses:
            
            if self.retweet_count and self.retweet_count > s.retweet_count:
                continue
                
            if self.favorite_count and self.favorite_count > s.favorite_count:
                continue
                
            if self.engagement_count and self.engagement_count > (s.retweet_count + s.favorite_count):
                continue
            
            if bw:
                tw = s.text.lower().split()
                intersection = set(bw).intersection(tw)
                if len(intersection) > 0:
                    continue
            
            if s.id not in coll_tweet_ids:
#                 print "Adding to %s: %s" % (self.collection_id, s.id)
                api.AddToCollection(self.collection_id, s.id)
                added.append(s.id)
                
        result = {}
        result["added"] = added
        
        return result

    def new_url(self):
        return "/collection/new"

    def edit_url(self):
        if self.id:
            return "/collection/%s/edit" % self.id
        else:
            return "/collection/new"

    def process_url(self):
        return "/collection/%s/process" % self.id

    def delete_url(self):
        return "/collection/%s/delete" % self.id

    def list_url(self):
        return "/collection/list"

    def __unicode__(self):
        return "<Collection: %s, %s, %s, %s>" % (self.id, self.name, self.list_slug, self.collection_id)