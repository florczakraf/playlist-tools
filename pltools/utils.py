import datetime
import re

def get_videos_ids(service, playlist_id):
  ids = []
  vids_request = service.playlistItems().list(playlistId=playlist_id, part="contentDetails", maxResults=50)
  while vids_request:
    vids_response = vids_request.execute()
    for vid in vids_response["items"]:
      ids.append(vid["contentDetails"]["videoId"])
    vids_request = service.playlistItems().list_next(vids_request, vids_response)
  return ids

def create_playlist(service, title, description=str(datetime.datetime.today()), privacy='unlisted'):
  new_playlist = service.playlists().insert(
                   part='snippet,status',
                   body=dict(
                     snippet=dict(
                       title=title,
                         description=description
                     ),
                     status=dict(
                       privacyStatus=privacy
                     )
                   )
                 ).execute()
  return new_playlist['id']

def add_to_playlist(service, playlist_id, video_id, position=0):
  add_video_response = service.playlistItems().insert(
                        part='snippet',
                        body=dict(
                          snippet=dict(
                            playlistId=playlist_id,
                            resourceId=dict(
                              kind='youtube#video',
                              videoId=video_id
                            ),
                            position=position
                          ) 
                        )
                      ).execute()
  return add_video_response

def get_channel_videos_ids(service, link):
  print "dupa"

  try:
    channel = re.search('\/channel\/(\w+)\/?', link).group(1)
  except:
    pass

  try:
    user = re.search('\/user\/(\w+)\/?', link).group(1)
  except:
    pass

  if channel:
    channels_response = service.channels().list(id=channel, part="contentDetails", maxResults=1).execute()
    print "got channel"
    uploads_playlist_id = ''
    for channel in channels_response['items']:
      uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
    #uploads_playlist_id = channels_reposnse['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    print uploads_playlist_id
    return get_videos_ids(service, uploads_playlist_id)
  elif user:
    channels_response = service.channels().list(forUsername=user, part="contentDetails", maxResults=1).execute()
    print "got user"
    uploads_playlist_id = channels_reposnse['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return get_videos_ids(service, uploads_playlist_id)
  else:
    raise Exception("Invalid channel link.")


