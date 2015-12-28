import os
import logging
import httplib2
import datetime
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

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'secrets.json')

FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/youtube',
    redirect_uri='http://yt.rflorczak.eu/oauth2callback')

def index(request):
  return render(request, 'pltools/index.html')

@login_required
def my_videos(request):
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
    authorize_url = FLOW.step1_get_authorize_url()
    return HttpResponseRedirect(authorize_url)
  else:
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build("youtube", "v3", http=http)
    channels_response = service.channels().list(mine=True, part="contentDetails").execute()
    videos = []
    for channel in channels_response["items"]:
      uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
      print uploads_list_id
      vids_request = service.playlistItems().list(playlistId=uploads_list_id, part="snippet", maxResults=50)
      while vids_request:
        vids_response = vids_request.execute()
        for vid in vids_response["items"]:
          videos.append(vid["snippet"]["title"])

        vids_request = service.playlistItems().list_next(vids_request, vids_response)

    return render_to_response('pltools/welcome.html', {
                'videos': videos,
                })

def registered(request):
  return render_to_response('pltools/registered.html')

def logout_view(request):
  logout(request)
  return render(request, 'pltools/index.html')

@login_required
def auth_return(request):
  print request.REQUEST['state'], request.user
  if not xsrfutil.validate_token(settings.SECRET_KEY, str(request.REQUEST['state']),
                                 request.user):
    return  HttpResponseBadRequest()
  credential = FLOW.step2_exchange(request.REQUEST)
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  storage.put(credential)
  return HttpResponseRedirect("/")

#tools

@login_required
def reverse(request):

  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
    authorize_url = FLOW.step1_get_authorize_url()
    return HttpResponseRedirect(authorize_url)

  if request.method == "POST":
    playlist_id = parse_qs(urlparse(request.POST.get("playlist_link")).query)['list'][0]

    http = httplib2.Http()
    http = credential.authorize(http)
    service = build("youtube", "v3", http=http)
    videos = []
    vids_request = service.playlistItems().list(playlistId=playlist_id, part="contentDetails", maxResults=50)
    while vids_request:
      vids_response = vids_request.execute()
      for vid in vids_response["items"]:
        videos.append(vid["contentDetails"]["videoId"])
      vids_request = service.playlistItems().list_next(vids_request, vids_response)

    new_playlist = service.playlists().insert(
                        part="snippet,status",
                        body=dict(
                          snippet=dict(
                            title="Reversed %s" % playlist_id,
                            description=str(datetime.datetime.today())
                            ),
                          status=dict(
                            privacyStatus="private"
                          )
                        )
                      ).execute()
    new_playlist_id = new_playlist['id']

    for vid in videos:
      add_video_request = service.playlistItems().insert(
                            part='snippet',
                            body=dict(
                              snippet=dict(
                                playlistId=new_playlist_id,
                                resourceId=dict(
                                  kind='youtube#video',
                                  videoId=vid
                                ),
                                position=0
                              ) 
                            )
                          ).execute()


    return render(request, 'pltools/reverse.html', {'new_playlist_id': new_playlist_id})
  
  return render(request, 'pltools/reverse.html')

