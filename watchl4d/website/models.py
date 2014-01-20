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
        serialized['members'] = [member.serialize() for member in self.members]

class TeamMember(Model):
    class Meta: 
        db_table = 'team_member'
        ordering = ['name']
    name = CharField(max_length=50)
    steam_id = CharField(max_length=25, unique=False)
    steam_profile = CharField(max_length=200, blank=True)
    team = ForeignKey(Team, related_name='members', null=True, blank=True)
    
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
        serialized['team'] = self.team.serialize() if self.team else None


class Map(Model):
    class Meta: 
        db_table = 'map'
        ordering = ['name']
    name = CharField(max_length=50)
    image = CharField(max_length=MAX_FILE_PATH_LENGTH)
    download = CharField(max_length=MAX_FILE_PATH_LENGTH)
    
    def __unicode__(self):
        return self.name

class Round(Model):
    class Meta: 
        db_table = 'round'
        ordering = ['number', '-create_date']
    number = PositiveSmallIntegerField(default=0)
    map = ForeignKey(Map, related_name='rounds', null=True, blank=True)
    create_date = DateTimeField(auto_now_add=True)

    def __unicode__(self):
        if self.map:
            return '{0} {1}: {2}'.format(self.__class__.__name__, self.number, self.map.name)
        else:
            return '{0} {1}'.format(self.__class__.__name__, self.number)

class Pairing(Model):
    class Meta: 
        db_table = 'pairing'
    team1 = ForeignKey(Team, related_name='pairings_as_home_team', blank=True, null=True)
    team2 = ForeignKey(Team, related_name='pairings_as_challenger', blank=True, null=True)
    score1 = PositiveSmallIntegerField()
    score2 = PositiveSmallIntegerField()
    resist1 = PositiveSmallIntegerField()
    resist2 = PositiveSmallIntegerField() 
    round = ForeignKey(Round, related_name='pairings')
    
    def __unicode__(self):
        return '{0}: {1} vs {2}, Round {3}'.format(self.__class__.__name__,
            self.team1.name,
            self.team2.name,
            self.round.number)

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
    image = CharField(max_length=MAX_FILE_PATH_LENGTH, blank=True, null=True)
    create_date = DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{0} by {1} on round {2} {3}'.format(self.__class__.__name__, 
            self.user.name, 
            self.round.number, 
            self.create_date)



