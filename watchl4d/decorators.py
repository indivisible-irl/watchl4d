
import logging
from django.conf import settings
from watchl4d.session import Session
from watchl4d.util import RequestObject

log = logging.getLogger(__name__)

class ViewError(Exception): pass

def require_authentication(func):
    def deco(*args, **kwargs):
        request = args[0]
        if not Session(request).is_authenticated:
            raise ViewError('You must be logged in to do that!')
        return func(*args, **kwargs)
    return deco

def require_match(request_key, session_key):
    '''
    Verifies that a value in the request's GET or POST
    matches a value in the request's session.
    
    Only works with integer values.
    
    If the session value is an iterable, 'in' is used.
    If the session value is not iterable, '==' is used.
    
    :param post_key: The key in the POST
    :type post_key: String
    :param session_key: The key in the session
    :type session_key: String
    
    '''
    def deco(func):
        func_name = func.__name__
        def dec(*args, **kwargs):
            request = args[0]
            request_val = int(getattr(RequestObject(request), request_key))
            session_val = getattr(Session(request), session_key)

            if hasattr(session_val, '__iter__'):
                match = request_val in session_val
            else:
                match = request_val == session_val

            if not match:
                log.debug('require_match decorator attempted to match request '
                          '{0}={1} with session {2}={3}.'
                          .format(request_key, request_val, 
                                  session_key, session_val))
                raise ViewError('Invalid input to {0} webservice.'
                                     .format(func_name))

            return func(*args, **kwargs)
        return dec
    return deco

def safety(response_type):
    def deco(func):
        def dec(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
            except ViewError as e:
                log.exception('')
                return response_type(success=False,
                                     message=e.message)
            except Exception as e:
                log.exception('')
                return response_type(success=False,
                                     message=('Something went wrong D: Please '
                                              'be patient and try again.'),
                                     secret=repr(e))

            if not isinstance(response, response_type):
                response = response_type()

            return response
        return dec
    return deco