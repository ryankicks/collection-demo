import os
import sys
import time
import json
import pytz
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

class UserProfile(models.Model):

    user = models.OneToOneField(User, related_name="profile")
    timezone = models.CharField(max_length=100,null=True,blank=True)
    curator_auth_token = models.CharField(max_length=40,null=True,blank=True)
    twitter_id = models.CharField(max_length=25,null=True,blank=True)
    twitter_access_token = models.CharField(max_length=75,null=True,blank=True)
    twitter_access_token_secret = models.CharField(max_length=75,null=True,blank=True)
    
    def get_timezone(self):
      	return pytz.timezone(self.timezone)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])