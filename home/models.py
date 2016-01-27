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
    start_date = models.DateTimeField(default=datetime.today, blank=True) 

    def process(self):
        
        added = []
        ignored = []
        
        bw = None
        if self.block_words:
            bw = self.block_words.lower().split()
        
        api = Twitter.get_twitter(self.created_by)

        list_statuses = None
        if self.list_slug == self.created_by.username:
            list_statuses = api.GetUserTimeline(screen_name=self.created_by.username, include_rts=True, count=25)
        elif self.list_slug and self.created_by.username:
            list_statuses = api.GetListTimeline(None, self.list_slug, owner_screen_name=self.created_by.username, include_rts=False, count=25)
        else:
            print "Insufficient info for GetListTimeline: slug=%s, owner_screen_name=%s" % (self.list_slug, self.created_by.username)
            return None

        if not list_statuses or len(list_statuses) == 0:
            print "No tweets returned for GetListTimeline: slug=%s, owner_screen_name=%s" % (self.list_slug, self.created_by.username)
            return None
            
        if not self.collection_id or self.collection_id == 'new':
            print "No collection specified: %s" % (self.collection_id)
            return None
            
        print "Processing list (slug=%s, owner_screen_name=%s) and collection (%s)" % (self.list_slug, self.created_by.username, self.collection_id)

        coll_tweet_ids = api.GetCollectionsEntries(self.collection_id, count=25)
        
        # print "list tweet count: %s" % len(list_statuses)
        # print "collection tweet count: %s" % len(coll_tweet_ids)
        
        start_date = None
        if (self.start_date):
            start_date = int(self.start_date.strftime("%s"))
        
        for s in list_statuses:
            
            if start_date and start_date > int(s.created_at_in_seconds):
                # print "\tfilter start_date (%s %s)" % (self.start_date, s.created_at) 
                ignored.append(s.id)
                continue
            
            if self.retweet_count and self.retweet_count > s.retweet_count:
                # print "\tfilter retweet_count (%s %s)" % (self.retweet_count, s.retweet_count)
                ignored.append(s.id)
                continue
                
            if self.favorite_count and self.favorite_count > s.favorite_count:
                # print "\tfilter favorite_count (%s %s)" % (self.favorite_count, s.favorite_count)
                ignored.append(s.id)
                continue
                
            if self.engagement_count and self.engagement_count > (s.retweet_count + s.favorite_count):
                # print "\tfilter engagement_count (%s %s)" % (self.engagement_count, (s.retweet_count + s.favorite_count))
                ignored.append(s.id)
                continue

            if s.retweeted_status:
                # print "\tfilter retweet"
                ignored.append(s.id)
                continue
            
            if bw:
                tw = re.findall(r"[\w']+", s.text.lower()) 
                intersection = set(bw).intersection(tw)
                
                if len(intersection) > 0:
                    # print "\tfilter block words (%s)" % s.text
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
            
            if result:
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
