import base64
import copy
import pytz
from time import *

from django import forms
from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import condition
from django.views.decorators.csrf import csrf_exempt

from social.apps.django_app.default.models import UserSocialAuth

from home.utils import *

import twitter
from twitter import *

def login(request):
    context = {"request": request}
    return render_to_response('login.html', context, context_instance=RequestContext(request))

@login_required
def home(request):

    # definition of all scorable categories and their point value
    categories = {
        "tweet_count": float(request.REQUEST.get("tweet_count", 0)),
        "retweet_count": float(request.REQUEST.get("retweet_count", .05)), 
        "favorite_count": float(request.REQUEST.get("favorite_count", 0)),
        "reply_to": float(request.REQUEST.get("reply_to", 2)),
        "retweets_of": float(request.REQUEST.get("retweets_of", 1))
    }

    # copy of categories + days setting for configuration    
    settings = copy.deepcopy(categories)
    settings["days"] = int(request.REQUEST.get("days", 7))
    settings["refresh"] = int(request.REQUEST.get("refresh", 0))
    settings["refresh_default"] = 5 * 60 * 1000 

    # determine start/end dates
    end_date = request.REQUEST.get("end_date", None)
    if end_date: 
        end_date = Tz.convert_to_utc(end_date, date_format="%Y-%m-%d %H:%M")
    else:
        end_date = datetime.now(pytz.utc)
    
    start_date = request.REQUEST.get("start_date", None)
    if start_date:
        start_date = Tz.convert_to_utc(start_date, date_format="%Y-%m-%d %H:%M")
    else:
        start_date = end_date - timedelta(days=settings["days"])
        
    settings["start_date"] = start_date 
    settings["end_date"] = end_date 
    
    # calculate seconds for better performance
    end_date_seconds = Tz.convert_to_seconds(end_date)
    start_date_seconds = Tz.convert_to_seconds(start_date)
        
    api = get_twitter(request.user)
    list = None
    lists = None
    list_exclude = None
    lists_exclude = None
    users = None
    results = None
    chart = None
 
    list_id = int(request.REQUEST.get("list", 0))

    list_exclude_id = request.REQUEST.get("list_exclude", 0)
    if list_exclude_id:
        list_exclude_id = int(list_exclude_id)
    else:
        list_exclude_id = None
    
    if list_id:

        list = api.GetList(list_id, None)
        users = api.GetListMembers(list.id, list.slug)

        users_exclude = []
        if list_exclude_id:        
            list_exclude = api.GetList(list_exclude_id, None)
            users_exclude = api.GetListMembers(list_exclude.id, list_exclude.slug)
            users_exclude = [u.screen_name for u in users_exclude]
  
        results = {}
         
        for u in users:
              
            statuses = []
              
            max_id = 0
            retweet_count = 0
            favorite_count = 0
      
            reply_to = 0
            retweets_of = 0
              
            while True:
                  
                # get latest page
                new_statuses = api.GetUserTimeline(screen_name=u.screen_name, count=200, max_id=max_id)
                  
                for s in new_statuses:
                      
                    if s.created_at_in_seconds > end_date_seconds:
                        
                        continue
                      
                    if s.created_at_in_seconds < start_date_seconds:
                          
                        # break out of while loop
                        new_statuses = []
                        break;
                    
#                     print s.created_at_in_seconds, Tz.convert_to_seconds(start_date), Tz.convert_to_seconds(end_date), s.id, s.text, s.retweet_count, s.favorite_count

                    # if retweet of another, than count accordingly
                    if s.retweeted_status and s.user.screen_name not in users_exclude:
                        retweets_of = retweets_of + 1
                          
                    # otherwise, my tweet, so count metrics
                    else:
                        retweet_count = retweet_count + s.retweet_count
                        favorite_count = favorite_count + s.favorite_count
                          
                        if s.in_reply_to_screen_name and s.in_reply_to_screen_name not in users_exclude:
                            reply_to = reply_to + 1
                              
                    statuses.append(s)
                              
                # out of statuses: done
                if len(new_statuses) == 0:
                    break
          
                max_id = min([s.id for s in new_statuses]) - 1
                  
                # reached max: done
                if len(statuses) >= 3200:
                    break
                  
            # engagements and scoring for each category
            results[u.screen_name] = {
                "statuses" : statuses,
                "count" : {
                    "tweet_count" : len(statuses),
                    "retweet_count" : retweet_count, 
                    "favorite_count" : favorite_count, 
                    "reply_to" : reply_to, 
                    "retweets_of": retweets_of,
                },
                "points" : {
                    "tweet_count" : settings["tweet_count"] * len(statuses),
                    "retweet_count" : settings["retweet_count"] * retweet_count, 
                    "favorite_count" : settings["favorite_count"] * favorite_count, 
                    "reply_to" : settings["reply_to"] * reply_to, 
                    "retweets_of": settings["retweets_of"] * retweets_of,
                    "total": 0 + settings["tweet_count"] * len(statuses) + settings["retweet_count"] * retweet_count + settings["favorite_count"] * favorite_count + settings["reply_to"] * reply_to + settings["retweets_of"] * retweets_of
                },            
            }
            
        # c3 chart data for points by category (and total)
        chart = {
             "columns": [
                [c] + [results[u.screen_name]["points"][c] for u in users] for c in categories 
             ],
             "groups" : [
                [c for c in categories]
             ],
        }

    # lists for leaderboard generation
    if not list or list.user.screen_name == request.user.username:
        
        lists = api.GetLists(screen_name=request.user.username)
    
        if not lists:
            
            list_temp = List()
            list_temp.id = ""
            list_temp.name = "-- Please create a list --"
            lists = [list_temp]

    context = {
       "request": request, 
       "settings": settings,
       "users": users, 
       "list": list, 
       "lists": lists, 
       "list_exclude": list_exclude, 
       "lists_exclude": lists, 
       "results": results, 
       "chart" : chart
    }
    return render_to_response('home.html', context, context_instance=RequestContext(request))

@login_required
@csrf_exempt
def settings (request):
    
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