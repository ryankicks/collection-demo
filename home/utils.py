from inspect import stack

import logging
from time import mktime
import pytz
from datetime import *
from calendar import timegm

# from django.http import HttpResponse, HttpResponseRedirect, HttpResponseRedirectBase
from django.conf import settings
from django.utils import timezone

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
    
    @staticmethod
    def convert_to_seconds(dt_utc):
        
        return mktime(dt_utc.timetuple())
    