import os
import logging
import httplib2

from apiclient.discovery import build
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from pltools.models import CredentialsModel
from playlist_tools import settings
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from django.conf.urls import *

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'secrets.json')

FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/youtube',
    redirect_uri='http://yt.rflorczak.eu/oauth2callback')


@login_required
def index(request):
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

