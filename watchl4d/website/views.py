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
from watchl4d.website.lib import get_streams

@require_GET
def watchl4d(request):
    return render(request, 'watchl4d.html')

@require_GET
def live(request):
    return HttpResponse(
        content=json.dumps(get_streams()),
        content_type='application/json')

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

