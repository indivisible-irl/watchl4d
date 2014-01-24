import json
import requests

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from watchl4d.util import *
from watchl4d.session import Session
from watchl4d.website.forms import *
from watchl4d.json import JsonResponse
from watchl4d.decorators import safety, require_authentication
from watchl4d.website.models import *

CHANNEL_NAMES = [
'l4dstreamlined',
'zkagaming',
'ball3hi',
'prodigysim',
'selinalol',
'sidewaysbox',
'icy_inferno',
'sirplease',
'sirpleasesd',
'dawkins154',
'kissmeplox',
'croxlox',
'alexi21',
'canadaroxgh',
'n1njaaa',
'haxormode',
'dectheone',
'flybyop',
'kingkillatoy',
'jacob404',
'xsilverxi',
'luunsky',
'ikaikaikamusume']

@require_GET
def watchl4d(request):
    return render(request, 'watchl4d.html')

@require_GET
def cup(request):
    generate_backbone_templates(request, 
                                settings.TEMPLATE_DIRS[0], 
                                settings.BACKBONE_TEMPLATE_FILE)
    session = Session(request)
    user = json.dumps(User.objects.get(id=session.user_id).serialize_related()) if session.is_authenticated else None

    teams = Team.objects.select_related('members', 'captain').filter(active=True)
    paired_teams = []
    for team in teams:
        if not paired_teams or paired_teams[-1][1] is not None:
            paired_teams.append((team, None))
        else:
            paired_teams[-1] = (paired_teams[-1][0], team)

    return render(request, 'main.html', 
        {'user': user, 
        'teams': teams, 
        'paired_teams': paired_teams})

@require_POST
@safety(JsonResponse)
def login(request):
    form = LoginForm(request.POST)
    if not form.is_valid():
        return JsonResponse(success=False, message=form.error_html)
    if not form.save(request):
        return JsonResponse(success=False, message=form.message)
    return JsonResponse(success=True, 
                        message=form.message,
                        data=form.user.serialize_related())

@safety(JsonResponse)
def logout(request):
    Session(request).end()
    return JsonResponse()

@require_POST
@safety(JsonResponse)
def register(request):
    form = RegisterForm(request.POST)
    if not form.is_valid():
        return JsonResponse(success=False, message=form.error_html)
    if not form.save(request):
        return JsonResponse(success=False, message=form.message)
    return JsonResponse(success=True, 
                        message=form.message,
                        data=form.user.serialize_related())

@require_POST
@safety(JsonResponse)
@require_authentication
def team(request):
    ''' 
    POST ['team_name', 'team_active', 'name[0-5]' , 'steam_id[0-5]', steam_profile[0-5]
    '''
    if not signups_open():
        return JsonResponse(success=False, message='Team editing is disabled while tournament is live.')
    
    session = Session(request)

    post = RequestObject(request)
    
    # Build the Context to make some sense of the form submitted
    ctx = {'team_name': post.team_name,
           'team':[]}
    for i in xrange(6):
        ctx['team'].append({'name': getattr(post, 'name{0}'.format(i)),
                            'steam_id': getattr(post, 'steam_id{0}'.format(i)),
                            'steam_profile': getattr(post, 'steam_profile{0}'.format(i)),
                            'id': getattr(post, 'id{0}'.format(i))})
    
    # Request Validation
    msg = assert_required(post.team_name, 'Team Name')
    for i, member in enumerate(ctx['team']):
        if i == 0:
            msg += assert_required(member['name'], 'Player 1\'s Name (you)')
            msg += assert_required_syntax_steam_id(member['steam_id'], 'Player 1\'s Steam ID (yours)')
        elif member['name'].strip():
            msg += assert_required_syntax_steam_id(member['steam_id'], 'Player {0}\'s Steam ID'.format(i+1))

    # Data Validation
    user = User.objects.select_related('team__members').get(id=session.user_id)
    if user.team and user.team.name != post.team_name:
        # player changed his team name, verify name isn't already taken
        try:
            other_team = Team.objects.get(name=post.team_name)
        except Team.DoesNotExist:
            pass
        else:
            msg += ('There already exists a team with the name \'{0}\'. <br />'
                    .format(post.team_name))
            # return render(request, 'team.html', ctx)

    if msg:
        return JsonResponse(success=False, message=msg)

    # Data actions
    team = user.team if user.team else Team()
    team.name = post.team_name
    team.active = post.team_active == 'true'
    team.save()
    
    # It's easier and safer to just clear out all members and resubmit them
    for member in team.members.all():
        member.delete()
    for i in xrange(1, 6):
        member = ctx['team'][i]
        if member['name']:
            m = TeamMember(name=member['name'],
                           steam_id=member['steam_id'],
                           steam_profile=member['steam_profile'],
                           team=team)
            m.save()

    user.name = post.name0
    user.steam_id = post.steam_id0
    user.steam_profile = post.steam_profile0
    user.team = team
    user.save()
    
    # Update Session
    # session.player_name = post.name0
  
    return JsonResponse(
        success=True, 
        message="Your team has been saved!", 
        data=json.dumps(User.objects.get(id=session.user_id).serialize_related()) if session.is_authenticated else None)

@require_POST
@safety(JsonResponse)
@require_authentication
def deleteteam(request):
    if not signups_open():
        return JsonResponse(success=False, message='Team editing is disabled while tournament is live.')
    
    session = Session(request)

    try:
        team = Team.objects.get(captain=session.user_id)
        team.delete()
    except Team.DoesNotExist:
        pass

    return JsonResponse(
        success=True, 
        message='Your team was successfully deleted.',
        data=json.dumps(User.objects.get(id=session.user_id).serialize_related()) if session.is_authenticated else None)


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

    # if settings.DEBUG and not new_live_channel:
    #     new_live_channel = EXAMPLE_LIVE_CHANNEL

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
