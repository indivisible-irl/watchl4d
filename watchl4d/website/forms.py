from datetime import timedelta
from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils.timezone import now
from django.contrib.auth.hashers import check_password, make_password

from watchl4d.website.models import *
from watchl4d.session import Session
from watchl4d.util import Object

class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        # message - any public error or success message
        self.message = None
    
    @property
    def error_html(self):
        '''
        Intended to be used once form.is_valid() returns false
        '''
        msgs = [] if not self.message else [self.message]
        msgs.extend(['Invalid {0}. {1}'.format(k.title(), v) for k, v in self.errors.iteritems()])
        return '<br />'.join(msgs)

    @property
    def cleaned_object(self):
        '''
        Convenience so we don't have to use a dict
        '''
        return Object(self.cleaned_data)

class LoginForm(BaseForm):
    username = forms.CharField(min_length=1, max_length=50)
    password = forms.CharField(min_length=1, max_length=128)
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None
    
    def save(self, request):
        '''
        :returns: whether login was successful or not
        :rtype: bool

        '''
        post = self.cleaned_object
        try:
            self.user = User.objects.get(username=post.username)
        except User.DoesNotExist:
            self.message = 'Unknown Username'
            return False

        if not check_password(post.password, self.user.password):
            self.message = 'Invalid Login'
            return False

        # Initiate the session
        Session(request).begin(self.user)
        self.message = 'Login successful'
        return True

class RegisterForm(BaseForm):
    name = forms.CharField(max_length=50, label='Name / Alias')
    steam_id = forms.RegexField(max_length=25, regex='^STEAM_[0-9]:[0-9]:[0-9]+$')
    steam_profile = forms.CharField(max_length=200, required=False)
    username = forms.CharField(min_length=1, max_length=50)
    password = forms.CharField(min_length=1, max_length=128)
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None
    
    def save(self, request):
        post = self.cleaned_object
        users = User.objects.filter(username=post.username)

        if users.count():
            self.message = 'The Username you specified is already in use.'
            return False

        encrypted_password = make_password(post.password)
                
        self.user = User(
            username=post.username, 
            password=encrypted_password,
            name=post.name, 
            steam_id=post.steam_id, 
            steam_profile=post.steam_profile)
        self.user.save()
        
        # Initiate the session / auto-login
        Session(request).begin(self.user)
        self.message = 'Registration successful'
        return True

        
        