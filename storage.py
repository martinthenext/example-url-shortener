"""

Storage backend for URL shortener. Implemented with MongoDB. Run as a script to set up the storage
before running the server.

>> setup()
>> url_code = store_url('http://davtyan.org')
>> url_code
'a'
>> get_url(url_code)
'http://davtyan.org'

"""
from pymongo import MongoClient, ReturnDocument, HASHED
import settings
from datetime import datetime, timedelta
from urlcodes import get_url_code, get_url_id
import sys


def setup():
    """ Set up MongoDB to work with the storage. WARNING this removes all data

    This operation creates a Hashed index on _id field of URL collection
    to ensure, when sharded, document writes are distributed evenly among shards

    """
    client = MongoClient(settings.DB_SERVER, settings.DB_PORT)
    
    counter_collection = client[settings.DB][settings.COUNTER_COLLECTION]
    counter_collection.delete_many({})
    counter_collection.insert_one({'_id': 'url_count', 'count': 0})

    url_collection = client[settings.DB][settings.URL_COLLECTION]
    url_collection.delete_many({})
    
    url_collection.ensure_index([('_id', HASHED)])


def get_new_id(client):
    """ Increase the url counter and return a new unused ID

    Arguments:
        client: an instance of MongoClient to avoid reconnecting to DB
    """
    counter_collection = client[settings.DB][settings.COUNTER_COLLECTION]
    new_counter_val = counter_collection.find_one_and_update(
        {'_id': 'url_count'},
        {'$inc': {'count': 1}},
        return_document=ReturnDocument.AFTER
    )
    new_id = new_counter_val['count']
    return new_id
    

def store_url(url):
    """ Store a given URL and return a URL code for it

    """
    client = MongoClient(settings.DB_SERVER, settings.DB_PORT)
    new_id = get_new_id(client)

    url_collection = client[settings.DB][settings.URL_COLLECTION]
    url_collection.insert_one({
        '_id': new_id,
        'url': url,
        'last_visited': datetime.utcnow()
    })
    
    url_code = get_url_code(new_id)
    return url_code


def get_url(url_code):
    """ Retrieve a URL given a URL code

    """
    url_id = get_url_id(url_code)

    client = MongoClient(settings.DB_SERVER, settings.DB_PORT)
    url_collection = client[settings.DB][settings.URL_COLLECTION]
    
    url_doc = url_collection.find_one_and_update(
        {'_id': url_id},
        {'$set': {'last_visited': datetime.utcnow()}},
    )
    if url_doc is None:
        return None
    
    url = url_doc['url']
    return url


def cleanup():
    """ Remove all URLs stored that have not been visited for long

    """
    client = MongoClient(settings.DB_SERVER, settings.DB_PORT)
    url_collection = client[settings.DB][settings.URL_COLLECTION]

    cutoff_time = datetime.utcnow() - timedelta(days=settings.MAX_DAYS_TO_STORE)
    url_collection.delete_many({'last_visited': {'$lt': cutoff_time}})


if __name__ == '__main__':
    get_url('abc')
    commands = {
        'setup': setup,
        'cleanup': cleanup,
    }
    if len(sys.argv) == 2:
        _, command = sys.argv
        if command in commands:
            commands[command]()
        else:
            print('Unkown command')
    else:
        print('Available commands: {}'.format(', '.join(commands.keys())))

