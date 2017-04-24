import os, sys, datetime, json, tweepy
from tweepy import StreamListener
from tweepy import Stream
from pymongo import MongoClient

CONSUMER_KEY = None
CONSUMER_SECRET = None
ACCESS_KEY = None
ACCESS_SECRET = None
MONGO_URI = None

def percentage(part, whole):
    if whole == 0:
        return 0
    else:
        num = round(100 * float(part)/float(whole), 2)
        return "{0}%".format(num)
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

AUTH = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
AUTH.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(AUTH)

tweet = api.get_status(tid)
txt = tweet.text.encode('utf-8')
followers_count = tweet.user.followers_count
favorite_count = tweet.favorite_count
tweet_percentage = percentage(favorite_count,followers_count)

print 'Text: {0}  Device: {1} Followers: {2} Favs: {3} Percentage: {4}'.format(txt,tweet.source, \
    followers_count,favorite_count,tweet_percentage)






# client = MongoClient(MONGO_URI)
# db = client['djt']
# tweets = db.tweetstest
# user_id = tweet.user.id_str
# screen_name = tweet.user.screen_name
# tweet_id = tweet.id_str
# tstamp = datetime.datetime.fromtimestamp(float('1492899401647')/1000.0)
# tweet_text = tweet.text.encode('utf-8')
# twt = tweets.insert({'tid':tweet_id, 'uid':user_id, 'screen_name':screen_name, \
#         'text':tweet_text, 'tstamp':tstamp})

# msg = "TID:{0}  UID: {1} Handle: {2} TStamp: {3} MID: {4}"
# print msg.format(tweet_id, user_id, screen_name, str(tstamp), twt )

# post_tweet = api.update_status(status=txt+' expanded')
# print str(post_tweet)