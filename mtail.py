'''
Command line utility to tail the blapp.log mongo collection.

syntax::

    python mtail.py

Use Ctrl+C to exit.

'''
import sys
import datetime
import time
import pymongo

def mtail(db, collection, host='localhost', port=27017):
    '''
    Opens a tailable cursor on a capped collection and prints
    documents to the console as they are inserted.

    '''
    client = pymongo.MongoClient(host='localhost', port=27017)
    collection = client['blapp']['log']

    while True:
        try:
            cursor = collection.find(tailable=True)

            while cursor.alive:
                try:
                    record = cursor.next()
                    print format_record(record)
                except StopIteration:
                    # There is no new data yet, wait a little bit
                    time.sleep(1)
        except KeyboardInterrupt:
            print 'detected Ctrl+C. exiting.'
            sys.exit(0)
        except:
            pass

def format_record(record):
    '''
    Formats the log document into a human readable string

    '''
    return '{0} - {1} - {2}:{3} - {4}{5}{6}'.format(
        format_timestamp(record['created']),
        record['levelname'],
        record['name'],
        record['lineno'],
        record['msg'],
        '\n{0}'.format(record['exc_text']) if record['exc_text'] else '',
        '\n{0}'.format(record['exc_info']) if record.get('exc_info') else '')

def format_timestamp(timestamp):
    '''
    Formats a timestamp into a human readable string
    
    '''
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y:%m:%d %H:%M:%S.%f')

if __name__ == '__main__':
    mtail('blapp', 'log')