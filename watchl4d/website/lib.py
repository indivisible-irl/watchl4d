import requests
import datetime
import copy
from django.core.cache import cache

#Square721 Cn BT


# These are listed in priority
CHANNELS = [
{'name': 'joeguertin', 'provider': 'twitch'},
{'name': 'cabisan04', 'provider': 'twitch'},
{'name': 'yesmrpresident', 'provider': 'twitch'},
{'name': 'estoopi', 'provider': 'twitch'},
{'name': 'babycakez_', 'provider': 'twitch'},
{'name': 'dexterity_', 'provider': 'twitch'},
{'name': 'usandy', 'provider': 'twitch'},
{'name': 'wrugb', 'provider': 'twitch'},
{'name': 'pwgtv', 'provider': 'twitch'},
{'name': 'l4dstreamlined', 'provider': 'twitch'},
{'name': 'zkagaming', 'provider': 'twitch'},
{'name': 'ball3hi', 'provider': 'twitch'},
{'name': 'prodigysim', 'provider': 'twitch'},
{'name': 'selinalol', 'provider': 'twitch'},
{'name': 'sidewaysbox', 'provider': 'twitch'},
{'name': 'icy_inferno', 'provider': 'twitch'},
{'name': 'dawkins154', 'provider': 'twitch'},
{'name': 'kissmeplox', 'provider': 'twitch'},
{'name': 'croxlox', 'provider': 'twitch'},
{'name': 'alexi21', 'provider': 'twitch'},
{'name': 'canadaroxgh', 'provider': 'twitch'},
{'name': 'n1njaaa', 'provider': 'twitch'},
{'name': 'haxormode', 'provider': 'twitch'},
{'name': 'dectheone', 'provider': 'twitch'},
{'name': 'flybyop', 'provider': 'twitch'},
{'name': 'kingkillatoy', 'provider': 'twitch'},
{'name': 'saywordz', 'provider': 'twitch'},
{'name': 'jacob404', 'provider': 'twitch'},
{'name': 'xsilverxi', 'provider': 'twitch'},
{'name': 'ikaikaikamusume', 'provider': 'twitch'},
{'name': 'crox', 'provider': 'hitbox'},
{'name': 'left4dead', 'provider': 'hitbox'},
{'name': '3bx', 'provider': 'hitbox'},
{'name': 'fanatictv', 'provider': 'hitbox'}]

class QueuedStreamQuery(object):
    def __init__(self):
        self._data = None
        self.cache_key = 'streams'
        self.in_process_cache_key = '{0}:inprocess'.format(self.cache_key)
        self.expiration_cache_key = '{0}:expiration'.format(self.cache_key)

    def run(self):
        if not self.has_data:
            if not self.in_process:
                return self.process()
            return self.run_cheap_query()
        
        if self.has_expired_data:
            if not self.in_process:
                return self.process()

        return self.data

    @property
    def data(self):
        if not self._data:
            self._data = cache.get(self.cache_key)
        return self._data

    @property
    def has_data(self):
        return self.data is not None

    @property
    def in_process(self):
        return cache.get(self.in_process_cache_key)

    def run_expensive_query(self):
        streams = [query_l4d_channel(channel) for channel in CHANNELS]
        streams.sort(key=lambda x: x['channel_name'])
        return streams

    def run_cheap_query(self):
        streams = []
        for channel in CHANNELS:
            streams.append(copy.copy(EMPTY_CHANNEL))
            streams[-1]['channel_name'] = channel['name']
        return streams

    @property
    def has_expired_data(self):
        expiration = cache.get(self.expiration_cache_key)
        return expiration and expiration < datetime.datetime.now()

    def process(self):
        # First, set flag telling other processes not to process anything.
        # This is set to expire after 1 minute in case the process hangs for any reason
        # things will reset after 1 minute.
        cache.set(self.in_process_cache_key, True, 60)

        # We store stream for a minute but our refresh rate will be much faster
        data = self.run_expensive_query()
        cache.set(self.cache_key, data, 60)

        # Cache the expiration of this new data
        # This tells when we ACTUALLY refresh the data (every 15 seconds)
        expiration = datetime.datetime.now() + datetime.timedelta(seconds=15)
        cache.set(self.expiration_cache_key, expiration, 120)

        # Delete data telling other processes that the query is in process
        cache.delete(self.in_process_cache_key)

        return data

def get_streams():
    streams = cache.get('streams')
    if not streams:
        streams = [query_l4d_channel(channel) for channel in CHANNELS]
        streams.sort(key=lambda x: x['channel_name'])
        cache.set('streams', streams, 60)
    return streams

def query_l4d_channel(channel):
    '''
    :param channel: channel data to assist query
    :type channel: dict structured as {'name': <str>, 'provider': <str>}

    '''
    if channel['provider'] == 'twitch':
        return query_l4d_twitch_channel(channel['name'])
    else:
        return query_l4d_hitbox_channel(channel['name'])

EMPTY_CHANNEL = {
    'live': False,
    'channel_name': '',
    'channel_provider': '',
    'title': '',
    'provided_by': '',
    'viewers': 0,
    'video_embed': '',
    'chat_embed': ''
}

def query_l4d_twitch_channel(channel_name):
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

        assert 'left 4 dead' in stream.get('game', '').lower()

        channel = stream['channel']

        live = True
        title = channel['status']
        provided_by = channel['display_name']
        viewers = stream['viewers']

    except:
        live = False
        title = ''
        provided_by = channel_name
        viewers = 0

    return {
        'live': live,
        'channel_name': channel_name,
        'channel_provider': 'twitch.tv',
        'title': title,
        'provided_by': provided_by,
        'viewers': viewers,
        'video_embed': TWITCH_VIDEO_EMBED.format(channel_name),
        'chat_embed': TWITCH_CHAT_EMBED.format(channel_name)
    }


# Video widths are kept consistent regardless of source
# Video heights are based on original width/height ratio
# Chat widths are kepy consistent regardless of source
# Chat height matches video height

# format with single argument: channel name
# video width/height ratio = 1.64
# chat height was originally 500
TWITCH_VIDEO_EMBED = '<object type="application/x-shockwave-flash" height="378" width="620" id="live_embed_player_flash" data="http://www.twitch.tv/widgets/live_embed_player.swf?channel={0}" bgcolor="#000000"><param name="allowFullScreen" value="true" /><param name="allowScriptAccess" value="always" /><param name="allowNetworking" value="all" /><param name="movie" value="http://www.twitch.tv/widgets/live_embed_player.swf" /><param name="flashvars" value="hostname=www.twitch.tv&channel={0}&auto_play=true&start_volume=25" /></object>'
TWITCH_CHAT_EMBED = '<iframe frameborder="0" scrolling="no" id="chat_embed" src="http://twitch.tv/chat/embed?channel={0}&amp;popout_chat=true" height="378" width="350"></iframe>'

# video width and height was originall 640x360 (1.7)
# new width = 620 -> new height = 365
# autoplay was guessed :D
HITBOX_VIDEO_EMBED = '<iframe width="620" height="365" src="http://hitbox.tv/#!/embed/{0}?autoplay=true" frameborder="0" allowfullscreen></iframe>'
# chat width and height was originally 360x640
HITBOX_CHAT_EMBED = '<iframe width="350" height="365" src="http://www.hitbox.tv/embedchat/{0}" frameborder="0" allowfullscreen></iframe>'

def query_l4d_hitbox_channel(channel_name):
    '''
    :param channel_name: Name/ID of a Hitbox.tv channel
    :type channel_name: str

    :returns: If channel is live and broadcasting Left 4 Dead, 
        data for channel. Otherwise None.
    :rtype: dict or None

    '''
    try:
        response = requests.get('http://api.hitbox.tv/media/live/{0}'.format(channel_name))

        channel = response.json().get('livestream', [{}])[0]
        
        assert int(channel.get('media_is_live', '0'))
        assert 'left 4 dead' in channel.get('category_name', '').lower()

        live = True
        title = channel['media_status']
        provided_by = channel['media_display_name']
        viewers = channel['media_views']

    except:
        live = False
        title = ''
        provided_by = channel_name
        viewers = 0
    
    return {
        'live': live,
        'channel_name': channel_name,
        'channel_provider': 'hitbox.tv',
        'title': title,
        'provided_by': provided_by,
        'viewers': viewers,
        'video_embed': HITBOX_VIDEO_EMBED.format(channel_name),
        'chat_embed': HITBOX_CHAT_EMBED.format(channel_name)
    }

# {"request":
#     {"this":"\/media\/live\/3yb"},
# "media_type":"live",
# "livestream":[
#     {"media_user_name":"3yb",
#     "media_id":"90887",
#     "media_file":"3yb",
#     "media_user_id":"301012",
#     "media_profiles":null,
#     "media_type_id":"1",
#     "media_is_live":"0",
#     "media_live_delay":"0",
#     "media_featured":null,
#     "media_date_added":"2014-01-24 03:32:04",
#     "media_live_since":"2014-01-24 07:13:25",
#     "media_transcoding":null,
#     "media_chat_enabled":"1",
#     "media_name":"3yb",
#     "media_display_name":"3yb",
#     "media_status":"Natural Selection 2 Public Game",
#     "media_title":"","media_description":"Yes",
#     "media_tags":"","media_duration":"0.0000",
#     "media_bg_image":null,
#     "media_views":"2",
#     "media_views_daily":"0",
#     "media_views_weekly":"0",
#     "media_views_monthly":"0","tn_id":null,"tn_media_id":null,"tn_media_file":null,"tn_large":null,"tn_mid":null,"tn_small":null,
#     "tn_selected":null,
#     "category_id":"890",
#     "category_name":"Animal Crossing: New Leaf",
#     "category_name_short":null,
#     "category_seo_key":"animal-crossing-new-leaf",
#     "category_viewers":"2",
#     "category_logo_small":null,
#     "category_logo_large":"",
#     "team_name":null,
#     "media_start_in_sec":"0",
#     "media_description_md":"Yes<\/p>\n",
#     "media_duration_format":"00:00:00",
#     "media_time_ago":"13 hours ago",
#     "media_thumbnail":"\/static\/img\/live\/3yb_mid_000.jpg",
#     "channel":{
#         "followers":"9",
#         "user_id":"301012",
#         "user_name":"3yb",
#         "user_status":"1",
#         "user_logo":"\/static\/img\/channel\/3yb_52e1d67312dff_large.jpg",
#         "user_logo_small":"\/static\/img\/channel\/3yb_52e1d67312dff_small.jpg",
#         "livestream_count":"1",
#         "channel_link":"http:\/\/hitbox.tv\/3yb"}}]}


EXAMPLE_LIVE_CHANNEL = {
    'channel_name': 'ball3hi',
    'title': 'Vertical Rise vs. Cynister // CCT2',
    'provided_by': 'Xbye',
    'video_embed': TWITCH_VIDEO_EMBED.format('ball3hi'),
    'chat_embed': TWITCH_CHAT_EMBED.format('ball3hi')
}