import os, sys, datetime, json
from pymongo import MongoClient

'''
This app loads data from a file into mongodb 
'''

CONSUMER_KEY = None
CONSUMER_SECRET = None
ACCESS_KEY = None
ACCESS_SECRET = None
MONGO_URI = None

try:
    pathname = os.path.dirname(sys.argv[0])
    config_file = os.path.abspath(pathname)+'/config.json'
    with open(config_file) as data_file:
        data = json.load(data_file)
    # Salt Creds
    CONSUMER_KEY = data['CONSUMER_KEY']
    CONSUMER_SECRET = data['CONSUMER_SECRET']
    ACCESS_KEY = data['ACCESS_KEY']
    ACCESS_SECRET = data['ACCESS_SECRET']
    MONGO_URI = data['MONGO_URI']
    TWITTER_TARGETS = data['TWITTER_TARGETS']
except IOError as err:
    print "[error] "+err.message

tid = ''
uid = ''
sc = ''
maxid = ''


def get_statements(file_name):
    pathname = os.path.dirname(sys.argv[0])
    config_file = os.path.abspath(pathname)+'/{0}'.format(file_name)
    lst = []
    with open(config_file) as message_file:
        for m in message_file:
            if m.strip():
                msg = m.strip()
                lst.append(msg)
    return lst


def save_statements(messages):
    # Save messages from file to mongo
    client = MongoClient(MONGO_URI)
    db = client['djt']
    coll_messages = db.messages
    for m in messages:
        msg = { 'message':m,
                'processed':False,
                'created_at':datetime.datetime.utcnow()
        }
        coll_messages.insert(msg)
        print(msg)


def get_message():
    client = MongoClient(MONGO_URI)
    db = client['djt']
    coll_messages = db.messages
    msgs = coll_messages.find({'processed':False}).sort('created_at', 1).limit(1)
    msg = {}
    for m in msgs:
        msg['_id'] = m['_id']
        msg['message'] = m['message']
    return msg


def update_messages(obj_id):
    msg_id = obj_id
    client = MongoClient(MONGO_URI)
    db = client['djt']
    db.messages.find_one_and_update({'_id':msg_id}, {'$set':{'processed':True}})


save_statements(get_statements('data.txt'))

# print(get_message())
