import os
from stat import *
import time

from boto.s3.connection import S3Connection
from boto.s3.key import Key

if __name__ == '__main__':
    conn = S3Connection('AKIAIEC6OR7MFH3RA3HQ', 
                '6hJOANO2GnqQpfFmyh9TPpHAUM2rn9QCAZ8y6LIf')
    bucket = conn.get_bucket('watchl4d')
    #bucket.set_acl('public-read')

    static_root = '/srv/www/watchl4d/watchl4d/website/static'

    for root, dirs, files in os.walk(static_root):
        for filename in files:
            if not filename.endswith('.py') and not filename.endswith('.xcf'):
                filename = '{0}/{1}'.format(root, filename)
                print 'Uploading {0}...'.format(filename)
    
                # There is no '/static' folder in my bucket
                key_filename = filename[len(static_root) + 1:]
                
                key = bucket.get_key(key_filename)
                if key is None:
                    key = Key(bucket)
                    key.key = key_filename

                key.set_contents_from_filename(filename)
                key.set_acl('public-read')
                
    
    print 'All S3 Uploads Completed'    
