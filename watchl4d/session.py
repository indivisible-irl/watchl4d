from watchl4d.website.models import User

class Session(object):
    def __init__(self, request):
        self._user = None
        self._request = request
        
    def begin(self, user):
        '''
        Initializes a session
        
        :param user: The user corresponding to the current session
        :type user: common.models.User
        
        '''
        self.end()
        self.is_authenticated = True
        self.user_id = user.id
        self.username = user.username
        
    def end(self):
        self._request.session.flush()

    def _get(self, key, default):
        return self._request.session.get(key, default)

    def _set(self, key, value):
        self._request.session[key] = value

    @property
    def user(self):
        if self._user is not None:
            return self._user
        if not self.is_authenticated:
            return None
        self._user = User.objects.get(id=self.user_id)
        return self._user
        
    @property
    def is_authenticated(self): return self._get('is_authenticated', False)
    @is_authenticated.setter
    def is_authenticated(self, value): self._set('is_authenticated', value)
        
    @property
    def user_id(self): return self._get('user_id', None)
    @user_id.setter
    def user_id(self, value): self._set('user_id', value)

    @property
    def username(self): return self._get('username', None)
    @username.setter
    def username(self, value): self._set('username', value)
