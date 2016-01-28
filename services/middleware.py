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
            
from django.conf import settings
from django.http import HttpResponseRedirect

class SSLMiddleware(object):

    def process_request(self, request):
        if not any([settings.DEBUG, request.is_secure(), request.META.get("HTTP_X_FORWARDED_PROTO", "") == 'https']):
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace("http://", "https://")
            return HttpResponseRedirect(secure_url)