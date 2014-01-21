import logging
import datetime
from pymongo import MongoClient

class MongoHandler(logging.Handler):
    def __init__(self, db, collection, 
        host='localhost', port=27017, level=logging.NOTSET):
        '''
        :param db: Database to log to
        :type db: str
        :param collection: Collection to log to
        :type collection str

        '''
        super(MongoHandler, self).__init__(level=level)

        client = MongoClient(host=host, port=port)
        self.collection = client[db][collection]

        self.formatter = MongoFormatter()

    def emit(self, record):
        self.collection.insert(self.format(record))

class MongoFormatter(logging.Formatter):
    def format(self, record):
        data = record.__dict__.copy()

        msg = record.msg % record.args if record.args else record.msg

        data.update(
            time=datetime.datetime.utcnow(),
            args=tuple(unicode(arg) for arg in record.args))

        try:
            data['exc_info'] = self.formatException(data['exc_info'])
        except:
            pass

        return data