from inspect import stack

import logging
from time import mktime
import pytz
from datetime import *
from calendar import timegm

# from django.http import HttpResponse, HttpResponseRedirect, HttpResponseRedirectBase
from django.conf import settings
from django.utils import timezone

from social.apps.django_app.default.models import UserSocialAuth

import twitter
from twitter import *

EPOCH = 1970
_EPOCH_ORD = date(EPOCH, 1, 1).toordinal()

class Tz:
    
    # assumes a date, unless you pass date_format, and then assumes it needs to be parsed
    @staticmethod
    def convert_to_utc(naive, date_format=None, user_tz=None):
    
        if date_format:
            naive = datetime.strptime (naive, date_format) 
        
        # if not specified, default to user context
        if not user_tz:
            user_tz = timezone.get_current_timezone()
        
        local_dt = user_tz.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        
        return utc_dt
    
    @staticmethod
    def convert_to_local(dt, user_tz=None):
    
        # if not specified, default to user context
        if not user_tz:
            user_tz = timezone.get_current_timezone()
        
        local_dt = dt.astimezone(user_tz)
        
        return local_dt

class Logger():

    @staticmethod
    def info(str):
        LOGGER.info(str)

    @staticmethod
    def exception(str):
        LOGGER.exception(str)
    
class Twitter:
    
    @staticmethod
    def get_twitter(user):
    
        from django.conf import settings
    
        consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY  
        consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET 
        access_token_key = settings.TWITTER_ACCESS_TOKEN 
        access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET 
    
        usa = UserSocialAuth.objects.get(user=user, provider='twitter')
        if usa:
            access_token = usa.extra_data['access_token']
            if access_token:
                access_token_key = access_token['oauth_token']
                access_token_secret = access_token['oauth_token_secret']
    
        if not access_token_key or not access_token_secret:
            raise Exception('No user for twitter API call')
    
        api = twitter.Api(
            base_url='https://api.twitter.com/1.1',
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token_key,
            access_token_secret=access_token_secret)
    
        return api
    
    @staticmethod
    def get_access_tokens(user):
        usa = UserSocialAuth.objects.get(user=user, provider='twitter')
        access_token = usa.extra_data['access_token']
        return access_token
