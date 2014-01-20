from __future__ import absolute_import

from json import dumps

from django.http import HttpResponse

class JsonResponse(HttpResponse):
    def __init__(self, success=True, message='', data=None, secret=''):
        '''
        :param data: extra data
        :type data: dict
        
        '''
        self._content = {}
        super(JsonResponse, self).__init__()
        self.content_type = 'application/json'
        self._update_content(**{'success': success,
                            'message': message,
                            'data': data,
                            'secret': secret})

    def _update_content(self, **kwargs):
        for k, v in kwargs.iteritems():
            self._content[k] = v
        self.content = dumps(self._content)
        
    @property
    def success(self):
        return self._content['success']
    @success.setter
    def success(self, value):
        self._update_content(success=value)
        
    @property
    def message(self):
        return self._content['message']
    @message.setter
    def message(self, value):
        self._update_content(message=value)
    
    @property
    def secret(self):
        '''
        @safety decorator populates this field with exception info
        that might not be useful/safe for users to see but helpful for debugging
        '''
        return self._content['secret']
    @secret.setter
    def secret(self, value):
        self._update_content(secret=value)
        
    @property
    def data(self):
        return self._content['data']
    @data.setter
    def data(self, value):
        self._update_content(data=value)
