from django.db.models import (Model, CharField, PositiveSmallIntegerField, DateTimeField,
                              ForeignKey, OneToOneField, ManyToManyField, BooleanField, 
                              SET_NULL)

MAX_FILE_PATH_LENGTH = 200

class Team(Model):
    class Meta: 
        db_table = 'team'
        ordering = ['-score', '-resist', '-signup_date']
    name = CharField(max_length=50)
    active = BooleanField(default=True)
    score = PositiveSmallIntegerField(default=0)
    resist = PositiveSmallIntegerField(default=0)
    signup_date = DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.name

    def serialize(self):
        return {
            'name': self.name,
            'active': self.active,
            'members': None
        }

    def serialize_related(self):
        serialized = self.serialize()
        serialized['members'] = [member.serialize() for member in self.members.all()]
        return serialized
        
class TeamMember(Model):
    class Meta: 
        db_table = 'team_member'
        ordering = ['name']
    name = CharField(max_length=50)
    steam_id = CharField(max_length=25, unique=False)
    steam_profile = CharField(max_length=200, blank=True)
    team = ForeignKey(Team, related_name='members', null=True, blank=True)
    
    @property
    def full_steam_profile(self):
        return self.steam_profile if self.steam_profile.startswith('http://') else 'http://{0}'.format(self.steam_profile)

    def __unicode__(self):
        return self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'steam_id': self.steam_id,
            'steam_profile': self.steam_profile,
        }

class User(Model):
    class Meta: 
        db_table = 'user'
        ordering = ['name']
    username = CharField(max_length=50)
    password = CharField(max_length=128)
    name = CharField(max_length=50)
    steam_id = CharField(max_length=25, unique=False)
    steam_profile = CharField(max_length=200, blank=True)
    team = OneToOneField(Team, related_name='captain', null=True, blank=True, on_delete=SET_NULL)

    @property
    def full_steam_profile(self):
        return self.steam_profile if self.steam_profile.startswith('http://') else 'http://{0}'.format(self.steam_profile)
    
    def __unicode__(self):
        return self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'steam_id': self.steam_id,
            'steam_profile': self.steam_profile,
            'team': None
        }

    def serialize_related(self):
        serialized = self.serialize()
        serialized['team'] = self.team.serialize_related() if self.team else None
        return serialized

class Map(Model):
    class Meta: 
        db_table = 'map'
        ordering = ['name']
    name = CharField(max_length=50)

    def serialize(self):
        return {'name': self.name}
    
    def __unicode__(self):
        return self.name

class Round(Model):
    class Meta: 
        db_table = 'round'
        ordering = ['number', '-create_date']
    number = PositiveSmallIntegerField(default=0)
    map = ForeignKey(Map, related_name='rounds', null=True, blank=True)
    create_date = DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            'id': self.id,
            'number': self.number,
            'map': None,
            'pairings': [],
            'posts': [],
            'standings': []
        }

    def serialize_related(self):
        serialized = self.serialize()
        serialized['map'] = self.map.serialize()
        serialized['pairings'] = [p.serialize_related() for p in self.pairings.all()]
        serialized['posts'] = [p.serialize_related() for p in self.posts.all()]
        
        standings = []
        for p in self.pairings.all():
            standings.append({'name': p.team1.name, 'score': p.score1, 'resist': p.resist1})
            standings.append({'name': p.team2.name, 'score': p.score2, 'resist': p.resist2})

        def team_cmp(x, y):
            if x['score'] > y['score']: return -1
            if x['score'] < y['score']: return 1
            if x['resist'] > y['resist']: return -1
            if x['resist'] < y['resist']: return 1
            return 0

        standings = sorted(standings, cmp=team_cmp)
        previous_score = None
        previous_resist = None
        previous_place = None
        inc = 1
        for i, standing in enumerate(standings):
            if previous_score is None or previous_resist is None or previous_place is None:
                standing['place'] = 1
                previous_score = standing['score']
                previous_resist = standing['resist']
                previous_place = 1
            elif previous_score == standing['score']:
                # Scores are the same
                if previous_resist == standing['resist']:
                    # Resist is the same
                    standing['place'] = previous_place
                    inc += 1
                else:
                    standing['place'] = previous_place + inc
                    previous_resist = standing['resist']
                    previous_place += inc
            else:
                # Scores are different
                standing['place'] = previous_place + inc
                previous_score = standing['score']
                previous_resist = standing['resist']
                previous_place += inc
                inc = 1

        serialized['standings'] = standings
        return serialized

    def __unicode__(self):
        if self.map:
            return '{0} {1}: {2}'.format(self.__class__.__name__, self.number, self.map.name)
        else:
            return '{0} {1}'.format(self.__class__.__name__, self.number)

class Pairing(Model):
    class Meta: 
        db_table = 'pairing'
        ordering = ['-create_date']
    team1 = ForeignKey(Team, related_name='pairings_as_home_team', blank=True, null=True)
    team2 = ForeignKey(Team, related_name='pairings_as_challenger', blank=True, null=True)
    score1 = PositiveSmallIntegerField()
    score2 = PositiveSmallIntegerField()
    resist1 = PositiveSmallIntegerField()
    resist2 = PositiveSmallIntegerField() 
    round = ForeignKey(Round, related_name='pairings')
    create_date = DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            'team1': None,
            'team2': None,
            'score1': self.score1,
            'score2': self.score2,
            'resist1': self.resist1,
            'resist2': self.resist2
        }

    def serialize_related(self):
        serialized = self.serialize()
        serialized['team1'] = self.team1.serialize()
        serialized['team2'] = self.team2.serialize()
        return serialized
    
    def __unicode__(self):
        return '{0}: {1}({2}|{3}) vs {4}({5}|{6}), Round {7}'.format(self.__class__.__name__,
            self.team1.name,
            self.score1,
            self.resist1,
            self.team2.name,
            self.score2,
            self.resist2,
            self.round.number)

# NOT USED
class Standing(Model):
    class Meta:
        db_table='standing'
        ordering = ['-score', '-resist', '-priority']
    team = ForeignKey(Team, related_name='standings')
    round = ForeignKey(Round, related_name='standings')
    score = PositiveSmallIntegerField()
    resist = PositiveSmallIntegerField()
    priority = PositiveSmallIntegerField(default=0)
    
    def __unicode__(self):
        return '{0} for {1}, score: {1}, resist: {2}'.format(self.__class__.__name__,
            self.team.name, 
            self.score, 
            self.resist)

class Post(Model):
    class Meta:
        db_table = 'post'
        ordering = ['-create_date']
    user = ForeignKey(User, related_name='posts')
    round = ForeignKey(Round, related_name='posts')
    text= CharField(max_length=1000)
    file = CharField(max_length=MAX_FILE_PATH_LENGTH, blank=True, null=True)
    file_name = CharField(max_length=MAX_FILE_PATH_LENGTH, blank=True, null=True)
    create_date = DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            'create_date': self.create_date.strftime('%m-%d-%Y %I:%M %p'),
            'text': self.text,
            'file_name': self.file_name,
            'is_image': self.is_image,
            'file': self.file,
            'user': None
        }

    def serialize_related(self):
        serialized = self.serialize()
        serialized['user'] = self.user.serialize()
        return serialized

    @property
    def is_image(self):
        if not all([self.file, self.file_name]):
            return False
        ext = self.file_name.split('.')[-1].lower()
        return ext in ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'png']

    def __unicode__(self):
        return '{0} by {1} on round {2} ({3}) {4}'.format(self.__class__.__name__, 
            self.user.name, 
            self.round.number, 
            self.text,
            self.create_date)



