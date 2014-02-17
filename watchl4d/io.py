
from django.conf import settings
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from uuid import uuid4
import os

VALID_IMAGE_EXTS = ['jpg', 'jpeg', 'bmp', 'png', 'gif', 'jpe'] # This is ignored in image.ImageProcessor
VALID_AUDIO_EXTS = ['mp3', 'ogg', 'wav']
IMAGE_SUBDIR = 'images/'
AUDIO_SUBDIR = 'audio/'

class BaseFileInfo(object):
    '''
    Base class for gathering data about an 
    object that represents a file.
    
    '''
    @property
    def filename(self):
        raise NotImplementedError('This property must be implemented in a subclass!')
    
    @property
    def extension(self):
        return self.filename.rsplit('.', 1)[-1].lower()
    
    @property
    def media_subdir(self):
        if self.extension in VALID_IMAGE_EXTS:
            return IMAGE_SUBDIR
        elif self.extension in VALID_AUDIO_EXTS:
            return AUDIO_SUBDIR
        else:
            return ''
    
class MediaFileInfo(BaseFileInfo):
    '''
    Retrieves the following data for a relative file path:
    - file extension (without '.')
    - media sub directory the file belongs to
    - absolute file path
    
    Assumptions:
    The file can be found at settings.MEDIA_URL
    
    '''
    def __init__(self, relative_file_path):
        self._relative_file_path = relative_file_path
        
    @property
    def filename(self):
        return self._relative_file_path
                              
    @property
    def absolute_url(self):
        if not self._relative_file_path: return None
        return '{0}{1}'.format(settings.MEDIA_URL,
                               self._relative_file_path)

class UploadedFileInfo(BaseFileInfo):
    '''
    Generates/Retrieves the following data for an UploadedFile instance:
    - absolute upload directory
    - relative upload directory
    - absolute uploaded file path
    - relative uploaded file path
    - absolute uploaded file path (resized smaller version)
    - absolute upload url
    - file extension (without '.')
    - media sub directory the file belongs to
    - whether or not the file is valid for upload
    
    Assumptions:
    The file is to be uploaded to settings.MEDIA_ROOT

    '''
    def __init__(self, file):
        '''
        :param file: the uploaded file data
        :type file: UploadedFile
        
        '''
        self._file = file
        self._reset_id()
        self._bucket = None

    def _reset_id(self):
        self._uid = str(uuid4()).replace('-', '')
    
    @property
    def bucket(self):
        if not self._bucket:
            conn = S3Connection(settings.MEDIA_AWS_ID, 
                                settings.MEDIA_AWS_SECRET) 
            self._bucket = conn.get_bucket(settings.MEDIA_S3_BUCKET)
        return self._bucket
    
    @property
    def file(self):
        return self._file
    
    @property
    def filename(self):
        return self._file.name
    
    # convenience methods
    @property
    def is_mp3(self): return self.extension == 'mp3'
    @property
    def is_wav(self): return self.extension == 'wav'
    @property
    def is_ogg(self): return self.extension == 'ogg'

    @property
    def new_file_name(self):
        return '{0}.{1}'.format(self._uid, self.extension)
        
    @property
    def relative_upload_dir(self):
        new_file_name = self.new_file_name
        return '{0}{1}/{2}/{3}/'.format(self.media_subdir,
                                        new_file_name[:2],
                                        new_file_name[2:4],
                                        new_file_name[4:6])
 
    @property
    def absolute_upload_dir(self):
        return '{0}{1}'.format(settings.MEDIA_ROOT,
                               self.relative_upload_dir)
        
    @property
    def relative_upload_file(self):
        return '{0}{1}'.format(self.relative_upload_dir,
                               self.new_file_name)
        
    @property
    def absolute_upload_file(self):
        return '{0}{1}'.format(self.absolute_upload_dir,
                               self.new_file_name)
        
    @property
    def absolute_upload_small_file(self):
        return '{0}{1}_s.{2}'.format(self.absolute_upload_dir,
                                     self._uid,
                                     self.extension)
        
    @property
    def absolute_upload_url(self):
        return '{0}{1}{2}'.format(settings.MEDIA_URL,
                                  self.media_subdir,
                                  self.relative_upload_file)
  
    def is_valid(self):
        if self._file.size <= 0:
            return False, 'User cannot upload a file of size 0.'
        
        # 200MB * 1024(kb) * 1024(b) - wav files are huge >_> 3MB ogg < 6MB mp3 < 77MB wav - 3:30 minute song
        if self._file.size > (200 * 1024 * 1024):
            return False, 'User cannot upload a file over 200 MB.'
        
        if self.extension not in (VALID_IMAGE_EXTS + 
                                  VALID_AUDIO_EXTS):
            return False, '{0} files are not supported.'.format(self.extension)
        
        return True, ''

    def save_locally(self):
        # Make sure upload destination exists
        if not os.path.exists(self.absolute_upload_dir):
            os.makedirs(self.absolute_upload_dir)
            
        with open(self.absolute_upload_file, 'wb+') as dest:
            for chunk in self.file.chunks():
                dest.write(chunk)
    
    def save_s3(self):
        s3_path = '{0}/{1}'.format(settings.MEDIA_S3_PATH, self.relative_upload_file)
        if self.bucket:
            key = self.bucket.get_key(s3_path)
            if not key:
                key = Key(self.bucket)
                key.key = s3_path

            #headers = {'Cache-Control': 'public,max-age=604800',"Content-Type": 'image/{0}'.format(ext)}
            key.set_contents_from_file(self.file, policy='public-read')



        
