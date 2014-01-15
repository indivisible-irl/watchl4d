import json
import requests

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

CHANNEL_NAMES = [
'l4dstreamlined',
'prodigysim',
'estoopi',
'kissmeplox',
'zkagaming',
'ball3hi',
'sirplease',
'sirpleasesd',
'sidewaysbox',
'canadaroxgh',
'n1njaaa',
'haxormode',
'dectheone',
'kingkillatoy',
'jacob404',
'xsilverxi']

@require_GET
def watchl4d(request):
    return render(request, 'watchl4d.html')

@require_GET
def cup(request):
    return render(request, 'main.html', {'user': None})

@require_GET
def live(request):
    old_live_channel = cache.get('live')

    if old_live_channel:
        # Check that what was previously seen as "live", is still live
        old_live_channel = query_l4d_channel(old_live_channel['channel_name'])
    
    if old_live_channel:
        new_live_channel = old_live_channel
    else:
        for channel_name in CHANNEL_NAMES:
            new_live_channel = query_l4d_channel(channel_name)
            if new_live_channel:
                cache.set('live', new_live_channel)
                break

    if settings.DEBUG and not new_live_channel:
        new_live_channel = EXAMPLE_LIVE_CHANNEL

    return HttpResponse(
        content=json.dumps(new_live_channel),
        content_type='application/json')

def query_l4d_channel(channel_name):
    '''
    :param channel_name: Name/ID of a Twitch.tv channel
    :type channel_name: str

    :returns: If channel is live and broadcasting Left 4 Dead, 
        data for channel. Otherwise None.
    :rtype: dict or None

    '''
    try:
        response = requests.get('https://api.twitch.tv/kraken/streams/{0}'.format(channel_name))
        stream = response.json().get('stream', {})

        if 'left 4 dead' not in stream.get('game', '').lower():
            return None

        channel = stream['channel']

        return {
            'channel_name': channel_name,
            'title': channel['status'],
            'provided_by': channel['display_name'],
            'video_embed': VIDEO_EMBED.format(channel_name),
            'chat_embed': CHAT_EMBED.format(channel_name)
        }

    except:
        return None

# format with single argument: channel name
# chat height was originally 500
VIDEO_EMBED = '<object type="application/x-shockwave-flash" height="378" width="620" id="live_embed_player_flash" data="http://www.twitch.tv/widgets/live_embed_player.swf?channel={0}" bgcolor="#000000"><param name="allowFullScreen" value="true" /><param name="allowScriptAccess" value="always" /><param name="allowNetworking" value="all" /><param name="movie" value="http://www.twitch.tv/widgets/live_embed_player.swf" /><param name="flashvars" value="hostname=www.twitch.tv&channel={0}&auto_play=true&start_volume=25" /></object>'
CHAT_EMBED = '<iframe frameborder="0" scrolling="no" id="chat_embed" src="http://twitch.tv/chat/embed?channel={0}&amp;popout_chat=true" height="378" width="350"></iframe>'


EXAMPLE_LIVE_CHANNEL = {
    'channel_name': 'ball3hi',
    'title': 'Vertical Rise vs. Cynister // CCT2',
    'provided_by': 'Xbye',
    'video_embed': VIDEO_EMBED.format('ball3hi'),
    'chat_embed': CHAT_EMBED.format('ball3hi')
}

# EXAMPLE_LIVE_CHANNEL = {
#     "_links": {
#         "self":"https://api.twitch.tv/kraken/streams/epicgamingtelevision",
#         "channel":"https://api.twitch.tv/kraken/channels/epicgamingtelevision"
#         },
#     "stream": {
#         "_id":8130826720,
#         "game":"Left 4 Dead 2",
#         "viewers":8,
#         "preview": {
#             "small": "http://static-cdn.jtvnw.net/previews-ttv/live_user_epicgamingtelevision-80x50.jpg",
#             "medium":"http://static-cdn.jtvnw.net/previews-ttv/live_user_epicgamingtelevision-320x200.jpg",
#             "large":"http://static-cdn.jtvnw.net/previews-ttv/live_user_epicgamingtelevision-640x400.jpg",
#             "template":"http://static-cdn.jtvnw.net/previews-ttv/live_user_epicgamingtelevision-{width}x{height}.jpg"
#             },
#         "_links": {
#             "self":"https://api.twitch.tv/kraken/streams/epicgamingtelevision"
#             },
#         "channel": {
#             "mature":false,
#             "abuse_reported":null,
#             "status":"Left 4 Dead 2. Quad WEBCAM.",
#             "display_name":"EpicGamingTelevision",
#             "game":"Left 4 Dead 2",
#             "delay":0,
#             "_id":47574045,
#             "name":"epicgamingtelevision",
#             "created_at":"2013-08-14T06:27:54Z",
#             "updated_at":"2014-01-06T15:58:39Z",
#             "primary_team_name":null,
#             "primary_team_display_name":null,
#             "logo":"http://static-cdn.jtvnw.net/jtv_user_pictures/epicgamingtelevision-profile_image-5f29ad30fa991ea3-300x300.jpeg",
#             "banner":null,
#             "video_banner":"http://static-cdn.jtvnw.net/jtv_user_pictures/epicgamingtelevision-channel_offline_image-d007b5bde045e6f7-640x360.png",
#             "background":null,
#             "profile_banner":"http://static-cdn.jtvnw.net/jtv_user_pictures/epicgamingtelevision-profile_banner-98a9ce9f33d8d24f-480.png",
#             "profile_banner_background_color":null,
#             "url":"http://www.twitch.tv/epicgamingtelevision",
#             "views":77973,
#             "_links": {
#                 "self":"https://api.twitch.tv/kraken/channels/epicgamingtelevision",
#                 "follows":"https://api.twitch.tv/kraken/channels/epicgamingtelevision/follows",
#                 "commercial":"https://api.twitch.tv/kraken/channels/epicgamingtelevision/commercial",
#                 "stream_key":"https://api.twitch.tv/kraken/channels/epicgamingtelevision/stream_key",
#                 "chat":"https://api.twitch.tv/kraken/chat/epicgamingtelevision",
#                 "features":"https://api.twitch.tv/kraken/channels/epicgamingtelevision/features",
#                 "subscriptions":"https://api.twitch.tv/kraken/channels/epicgamingtelevision/subscriptions",
#                 "editors":"https://api.twitch.tv/kraken/channels/epicgamingtelevision/editors",
#                 "teams":"https://api.twitch.tv/kraken/channels/epicgamingtelevision/teams",
#                 "videos":"https://api.twitch.tv/kraken/channels/epicgamingtelevision/videos"
#                 }
#             }
#         }
#     }

# "mspyte"
#     VIDEO:
#     <object type="application/x-shockwave-flash" height="378" width="620" id="live_embed_player_flash" data="http://www.twitch.tv/widgets/live_embed_player.swf?channel=msspyte" bgcolor="#000000"><param name="allowFullScreen" value="true" /><param name="allowScriptAccess" value="always" /><param name="allowNetworking" value="all" /><param name="movie" value="http://www.twitch.tv/widgets/live_embed_player.swf" /><param name="flashvars" value="hostname=www.twitch.tv&channel=msspyte&auto_play=true&start_volume=25" /></object><a href="http://www.twitch.tv//msspyte" class="trk" style="padding:2px 0px 4px; display:block; width:345px; font-weight:normal; font-size:10px; text-decoration:underline; text-align:center;">Watch live video from MsSpyte on www.twitch.tv</a>
#     CHAT:
#     <iframe frameborder="0" scrolling="no" id="chat_embed" src="http://twitch.tv/chat/embed?channel=msspyte&amp;popout_chat=true" height="500" width="350"></iframe>