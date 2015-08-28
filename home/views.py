import base64
import copy
from time import *

from django import forms
from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from social.apps.django_app.default.models import UserSocialAuth
import twitter
from twitter import *

from home.models import Image

class ImageForm(forms.Form):
    file = forms.FileField()

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
        "retweets_to": float(request.REQUEST.get("retweets_to", 1))
    }

    # copy of categories + days setting for configuration    
    settings = copy.deepcopy(categories)
    settings["days"] = int(request.REQUEST.get("days", 7)) 

    # num days to look back for scoring
    lookback_date = int(time()) - settings["days"] * 24 * 60 * 60

    api = get_twitter(request.user)
    list = None
    users = None
    results = None
    chart = None
 
    list_id = int(request.REQUEST.get("list", 0))
    if list_id:
         
        list = api.GetList(list_id, None)
        users = api.GetListMembers(list.id, list.slug)
  
        results = {}
         
        for u in users:
              
            statuses = []
              
            max_id = 0
            retweet_count = 0
            favorite_count = 0
      
            reply_to = 0
            retweets_to = 0
              
            while True:
                  
                # get latest page
                new_statuses = api.GetUserTimeline(screen_name=u, count=200, max_id=max_id)
                  
                for s in new_statuses:
                      
                    if s.created_at_in_seconds < lookback_date:
                          
                        # break out of while loop
                        new_statuses = []
                        break;
                      
                    # if retweet of another, than count accordingly
                    if (s.retweeted_status):
                        retweets_to = retweets_to + 1
                          
                    # otherwise, my tweet, so count metrics
                    else:
                        retweet_count = retweet_count + s.retweet_count
                        favorite_count = favorite_count + s.favorite_count
                          
                        if (s.in_reply_to_screen_name):
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
                    "retweets_to": retweets_to,
                },
                "points" : {
                    "tweet_count" : settings["tweet_count"] * len(statuses),
                    "retweet_count" : settings["retweet_count"] * retweet_count, 
                    "favorite_count" : settings["favorite_count"] * favorite_count, 
                    "reply_to" : settings["reply_to"] * reply_to, 
                    "retweets_to": settings["retweets_to"] * retweets_to,
                    "total": 0 + settings["tweet_count"] * len(statuses) + settings["retweet_count"] * retweet_count + settings["favorite_count"] * favorite_count + settings["reply_to"] * reply_to + settings["retweets_to"] * retweets_to
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
    lists = api.GetLists(screen_name=request.user.username)

    context = {"request": request, "settings": settings, "users": users, "list": list, "lists": lists, "results": results, "chart" : chart}
    return render_to_response('home.html', context, context_instance=RequestContext(request))

from django.contrib.auth import logout as auth_logout
def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')

def get_twitter(user):

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