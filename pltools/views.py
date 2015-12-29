import os
import logging
import httplib2
import random
from urlparse import parse_qs, urlparse
from apiclient.discovery import build
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from pltools.models import CredentialsModel
from django.template import RequestContext
from playlist_tools import settings
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from django.conf.urls import *
from django.contrib.auth import logout
from pltools.utils import *

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'secrets.json')

FLOW = flow_from_clientsecrets(
  CLIENT_SECRETS,
  scope='https://www.googleapis.com/auth/youtube',
  redirect_uri='http://yt.rflorczak.eu/oauth2callback')

def index(request):
  return render(request, 'pltools/index.html')

def registered(request):
  return render(request, 'pltools/registered.html')

def logout_view(request):
  logout(request)
  return render(request, 'pltools/index.html')

@login_required
def auth_return(request):
  if not xsrfutil.validate_token(settings.SECRET_KEY, str(request.REQUEST['state']),
                                 request.user):
    return  HttpResponseBadRequest()
  credential = FLOW.step2_exchange(request.REQUEST)
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  storage.put(credential)
  return HttpResponseRedirect(request.session['return_to'])

#tools

@login_required
def reverse(request):
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
    authorize_url = FLOW.step1_get_authorize_url()
    request.session['return_to'] = request.path
    return HttpResponseRedirect(authorize_url)

  if request.method == "POST":
    playlist_link = request.POST.get("playlist_link")

    try:
      playlist_id = parse_qs(urlparse(playlist_link).query)['list'][0]
    except:
      return render(request, 'pltools/reverse.html', {'error': 'There was an error while parsing your link. Please double-check it.', 'playlist_link': playlist_link})
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build("youtube", "v3", http=http)
    videos = get_videos_ids(service, playlist_id)
    new_playlist_id = create_playlist(service, 'Reversed %s' % playlist_id)

    for vid_id in videos:
      add_to_playlist(service, new_playlist_id, vid_id)

    return render(request, 'pltools/reverse.html', {'new_playlist_id': new_playlist_id})
  
  return render(request, 'pltools/reverse.html')

@login_required
def channel(request):
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
    authorize_url = FLOW.step1_get_authorize_url()

    request.session['return_to'] = request.path
    return HttpResponseRedirect(authorize_url)

  if request.method == "POST":
    channel_link = str(request.POST.get("channel_link"))
    
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build("youtube", "v3", http=http)
    new_playlist_id = None
    try:
      new_playlist_id = get_channel_playlist(service, channel_link)
    except:
      return render(request, 'pltools/channel.html', 
                     {'error': 'There was an error while parsing your link. Please double-check it.', 
                      'channel_link': channel_link})

    return render(request, 'pltools/channel.html', {'new_playlist_id': new_playlist_id})
  
  return render(request, 'pltools/channel.html')

@login_required
def randomize(request):
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
    authorize_url = FLOW.step1_get_authorize_url()
    request.session['return_to'] = request.path
    return HttpResponseRedirect(authorize_url)

  if request.method == "POST":
    playlist_link = request.POST.get("playlist_link")

    try:
      playlist_id = parse_qs(urlparse(playlist_link).query)['list'][0]
    except:
      return render(request, 'pltools/randomize.html', 
               {'error': 'There was an error while parsing your link. Please double-check it.',
                'playlist_link': playlist_link})
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build("youtube", "v3", http=http)
    videos = get_videos_ids(service, playlist_id)
    random.shuffle(videos)
    new_playlist_id = create_playlist(service, 'Randomized %s' % playlist_id)

    for vid_id in videos:
      add_to_playlist(service, new_playlist_id, vid_id)

    return render(request, 'pltools/randomize.html', {'new_playlist_id': new_playlist_id})
  
  return render(request, 'pltools/randomize.html')
