import os, sys, datetime, json, tweepy, re
from tweepy import StreamListener
from tweepy import Stream
from pymongo import MongoClient
from textblob import TextBlob

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

AUTH = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
AUTH.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(AUTH)

def clean_tweet(tweet):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def has_tweet(tid):
    client = MongoClient(MONGO_URI)
    db = client['djt']
    tweets = db.tweets
    twt = tweets.find({'tid':tid,'processed':True})
    if twt.count()>0:
        return True
    else:
        return False

def test_sentitment(txt):
    for t in txt:
        analysis = TextBlob(t)
        print 'text: {0} - Polarity: {1}'.format(t,analysis.sentiment.polarity)

def get_tweet(uid):
    client = MongoClient(MONGO_URI)
    db = client['djt']
    tweets = db.tweets
    twt = tweets.find({'processed':False,'uid':uid}).sort('created_at',1).limit(1)
    status_id=''
    for t in twt:
        status_id = t['tid']

    # Check if tweet exists in Twitter
    try:
        resp_tweet = api.get_status(status_id)
    except tweepy.TweepError as e:
        if e.message[0]['code'] == 144:
            # Flag the deleted tweet
            update_tweet_processed(status_id)
            # Get a new tweet
            status_id = get_tweet(uid)
    return status_id

def get_saved_tweet(uid):
    client = MongoClient(MONGO_URI)
    db = client['djt']
    tweets = db.tweets
    twt = tweets.find({'processed':False,'uid':uid}).sort('created_at',1).limit(1)
    status_id=''
    for t in twt:
        status_id = t['tid']
        txt = clean_tweet(t['text'])
    return {'tid':status_id, 'text':txt}

def save_tweet(status): 
    client = MongoClient(MONGO_URI)
    db = client['djt']
    tweets = db.tweets
    user_id = status.user.id_str
    screen_name = status.user.screen_name
    tweet_id = status.id_str
    created_at = status.created_at
    reply_id = status.in_reply_to_status_id_str if status.in_reply_to_status_id_str else ''
    reply_name = status.in_reply_to_screen_name if status.in_reply_to_screen_name else ''
    tweet_text = status.text.encode('utf-8')
    processed = False
    twt = tweets.insert({'tid':tweet_id, 'uid':user_id, 'screen_name':screen_name, \
            'reply_to_id':reply_id, 'reply_name':reply_name, 'text':tweet_text, 'created_at':created_at, \
            'processed':processed} )
    msg = "TID: {0}  UID: {1} Handle: {2} RepToID: {3} RepToName: {4} created_at: {5}"
    print msg.format(tweet_id, user_id, screen_name, reply_id, reply_name, created_at)    

def get_older_status_maxid(sn,max_id):
    stuff = api.user_timeline(screen_name = sn, max_id = max_id, count = 200, include_rts = False)
    for s in stuff:
        save_tweet(s)

def get_older_status(sn):
    stuff = api.user_timeline(screen_name = sn, count = 50, include_rts = False)
    for s in stuff:
        save_tweet(s)
def get_status(status_id):
    stuff = api.get_status(status_id)
    print stuff.source
 
def update_tweet_processed(tid):
    client = MongoClient(MONGO_URI)
    db = client['djt']
    tweets = db.tweets
    twt = tweets.update_one({'tid':tid},{'$set':{'processed':True}});
    print "Tweet {0} Processed".format(tid)        

def percent_response(screen_name, percentage, followers, status_url):
    emoji = u"\U0001F447"
    MSG = '@{0}\n{1} of your {2} Followers Liked this Tweet:\n'.format(screen_name, percentage, followers) \
        + u"\U0001F447" + '\n{0}'.format(status_url)
    return MSG

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

msg = get_message()
print(msg['message'])
# get_older_status('<twitter_handle>')

# get_status('879680876501766144112')
# print get_tweet('25073877')
# statements = [
#     'Trump is an asshole.',
#     'Etienne is a loving boy',
#     'Kristin is a great wife',
#     'Country is not doing so well these days because Trump is being arrogant',
#     'My favorite desert is apple pie'
# ]

# test_sentitment(statements)