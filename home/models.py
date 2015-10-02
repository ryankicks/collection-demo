import os
import sys
import re

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
        ignored = []
        
        bw = None
        if self.block_words:
            bw = self.block_words.lower().split()
        
        api = Twitter.get_twitter(self.created_by)

        coll_tweet_ids = api.GetCollectionsEntries(self.collection_id)
        list_statuses = api.GetListTimeline(None, self.list_slug, owner_screen_name=self.created_by.username, include_rts=self.include_retweets)
        
        for s in list_statuses:
            
            if self.retweet_count and self.retweet_count > s.retweet_count:
                ignored.append(s.id)
                continue
                
            if self.favorite_count and self.favorite_count > s.favorite_count:
                ignored.append(s.id)
                continue
                
            if self.engagement_count and self.engagement_count > (s.retweet_count + s.favorite_count):
                ignored.append(s.id)
                continue

            if s.retweeted_status:
                ignored.append(s.id)
                continue
            
            if bw:
                tw = re.findall(r"[\w']+", s.text.lower()) 
                intersection = set(bw).intersection(tw)
                
                if len(intersection) > 0:
                    ignored.append(s.id)
                    continue
            
            if s.id not in coll_tweet_ids:
#                 print "Adding to %s: %s" % (self.collection_id, s.id)
                response = api.AddToCollection(self.collection_id, s.id)
                added.append(s.id)
                
        result = {}
        result["list_slug"] = self.list_slug
        result["collection_id"] = self.collection_id
        result["added"] = added
        result["ignored"] = ignored
        
        return result

    @staticmethod
    def process_all():
            
        collection_count = 0
        tweet_count = 0
        
        collections = Collection.objects.filter(Q(deleted=False)).order_by('-created_time')

        for c in collections:
            
            result = c.process()
            
            tweet_count = tweet_count + len(result["added"]) 
            collection_count = collection_count + 1
            
        return (collection_count, tweet_count)


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