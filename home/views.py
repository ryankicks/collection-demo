import base64

from django import forms
from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from social.apps.django_app.default.models import UserSocialAuth
import twitter

from home.models import Image 

class ImageForm(forms.Form):
    file = forms.FileField()

def login(request):
    context = {"request": request}
    return render_to_response('login.html', context, context_instance=RequestContext(request))

@login_required
def home(request):

    days = int(request.REQUEST.get("days", 7))
    retweet_count = float(request.REQUEST.get("retweet_count", .05))
    favorite_count = int(request.REQUEST.get("favorite_count", 0))    
    reply_to = int(request.REQUEST.get("reply_to", 2))
    retweets_to = int(request.REQUEST.get("retweets_to", 1))
    
    settings = {
        "days": days, 
        "retweet_count": retweet_count, 
        "favorite_count": favorite_count,
        "reply_to": reply_to,
        "retweets_to": retweets_to
    }

    results = None
    
    api = get_twitter(request.user)
    lists = api.GetLists(screen_name=request.user.username)
    list_id = request.REQUEST.get("list", None)
    list_slug = None
    
    if list_id:
        
        for l in lists:
            if l.id == list_id:
                list_slug = l.slug
    
        users = api.GetListMembers(list_id, list_slug)
        if users:
            users = [u.screen_name for u in users]
#         users = ['jbulava', 'joncipriano', 'rchoi', 'niall']
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
                    
                    # if retweet of another, than count accordingly
                    if (s.retweeted_status):
                        retweets_to = retweets_to + 1
                        
                    # otherwise, my tweet, so count metrics
                    else:
                        retweet_count = retweet_count + s.retweet_count
                        favorite_count = favorite_count + s.favorite_count
                        
                        if (s.in_reply_to_screen_name):
                            reply_to = reply_to + 1
                            
                # out of statuses: done
                if len(new_statuses) == 0:
                    break
        
                max_id = min([s.id for s in new_statuses]) - 1
                statuses = statuses + new_statuses
                
                # reached max: done
                if len(statuses) >= 200:
                    break
                
            results[u] = {
    #             "statuses" : statuses,
                "retweet_count" : retweet_count, 
                "favorite_count" : favorite_count, 
                "reply_to" : reply_to, 
                "retweets_to": retweets_to 
            }

    context = {"request": request, "settings": settings, "lists": lists, "results": results}
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