import os
import StringIO
import cProfile

from datetime import datetime
import pytz

from django.shortcuts import *

from django.utils import timezone

class TimezoneMiddleware(object):
    
    def process_request(self, request):
        
        if request.user.is_authenticated():
            tzname = request.user.profile.timezone
            
            if tzname:
                timezone.activate(pytz.timezone(tzname))
            else:
                if "/settings" not in request.path and "/admin" not in request.path and "/static" not in request.path:
                    return redirect('/settings')
            