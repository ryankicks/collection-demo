import base64
import copy
import pytz
import json
import datetime
from time import *

from django import forms
from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import condition
from django.views.decorators.csrf import csrf_exempt

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from social.apps.django_app.default.models import UserSocialAuth

from home.utils import *
from home.models import *

DATE_FORMAT = "%Y-%m-%d %H:%M"

def login(request):
    context = {"request": request}
    return render_to_response('login.html', context, context_instance=RequestContext(request))

@login_required
# @user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='/')
def collection_list(request):
    
    collections = None

    filter = Q(deleted=False)
    if not request.user.is_superuser:
        filter = filter&Q(created_by=request.user)

    collections = Collection.objects.filter(filter).order_by('-created_time')
    
    context = {"request": request, "collections": collections}
    return render_to_response('collection_list.html', context, context_instance=RequestContext(request))

@login_required
@csrf_exempt
# @user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='/')
def collection_edit(request, id=None):
    
    coll = None
    
    id = request.REQUEST.get("id", id)
    if id:
        coll = Collection.objects.get(pk=id)
    else:
        coll = Collection()
    
    if request.method == 'POST':
        
        coll.name = request.REQUEST.get("name", "")
        coll.list_slug = request.REQUEST.get("list_slug", None)
        coll.list_name = request.REQUEST.get("list_name", None)
        coll.collection_id = request.REQUEST.get("collection_id", None)
        coll.collection_name = request.REQUEST.get("collection_name", None) 
        coll.retweet_count = int(request.REQUEST.get("retweet_count", 0)) 
        coll.favorite_count = int(request.REQUEST.get("favorite_count", 0)) 
        coll.engagement_count = int(request.REQUEST.get("engagement_count", 0)) 
        coll.block_words = request.REQUEST.get("block_words", "")
        coll.include_retweets = request.REQUEST.get("include_retweets", False)
        coll.start_date = Tz.convert_to_utc(request.REQUEST.get("start_date", None), date_format="%Y-%m-%d %H:%M")

    api = Twitter.get_twitter(request.user)
 
    lists = []
    collections = []
    
    if not settings.OFFLINE:
        lists = api.GetLists(screen_name=request.user.username)
 
    if not settings.OFFLINE:
        collections = api.GetCollections(screen_name=request.user.username)

    if request.method == 'POST':

        if id:
            coll.id = id
        
        for l in lists:
            if l.slug == coll.list_slug:
                coll.list_name = l.name
            
        for c in collections:
            if c.id == coll.collection_id:
                coll.collection_name = c.name
             
        coll.save()
        
        return redirect('/collection/list')

    context = {
       "request": request, 
       "settings": settings,
       "coll": coll,
       "lists": lists, 
       "collections": collections, 
    }
    return render_to_response('collection_edit.html', context, context_instance=RequestContext(request))

@login_required
@csrf_exempt
# @user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='/')
def collection_delete(request, id=None):

    id = request.REQUEST.get("id", id)
    if id:
        coll = Collection.objects.get(pk=id)
        coll.deleted = True
        coll.save()

    return redirect('/collection/list')

@login_required
@csrf_exempt
# @user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='/')
def collection_process(request, id=None):

    response_data = {}

    id = request.REQUEST.get("id", id)
    if id:
        coll = Collection.objects.get(pk=id)
        result = coll.process()

    response_data['result'] = result
    
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required
@csrf_exempt
def settings_page (request):
    
    from timezones import zones

    user = request.user
    access_tokens = Twitter.get_access_tokens(user)
    success_msg = ""

    if request.method == 'POST':

        profile = user.profile
        
        profile.twitter_id = access_tokens.get('user_id', None)
        profile.twitter_access_token = access_tokens.get('oauth_token', None)
        profile.twitter_access_token_secret = access_tokens.get('oauth_token_secret', None)
        profile.save()

        profile.timezone = request.REQUEST.get("timezone", None)
        profile.save()
        
        success_msg = "Saved."
        
    tz_list = []
    for tz_offset, tz_name, tz_formatted in zones.get_timezones(only_us=False):
        tz_list.append([tz_name, tz_formatted])

    context = {
       "request": request, 
        'timezones': tz_list,
        'twitter_id': user.profile.twitter_id,
        'twitter_access_tokens': access_tokens
    }
    
    if success_msg:
        context["message"] = success_msg

    return render_to_response('settings.html', context, context_instance=RequestContext(request))

from django.contrib.auth import logout as auth_logout
def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')

