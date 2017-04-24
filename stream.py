import os, sys, datetime, json, tweepy
from tweepy import StreamListener
from tweepy import Stream
from pymongo import MongoClient

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
    # Service Creds
    CONSUMER_KEY = data['CONSUMER_KEY']
    CONSUMER_SECRET = data['CONSUMER_SECRET']
    ACCESS_KEY = data['ACCESS_KEY']
    ACCESS_SECRET = data['ACCESS_SECRET']
    MONGO_URI = data['MONGO_URI']
    TWITTER_TARGETS = data['TWITTER_TARGETS']
except IOError as err:
    print "[error] "+err.message

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

class StreamListener(tweepy.StreamListener):
    def save_tweet(self, status):
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

    def on_status(self, status):
        # Check for tweets & replies from Targets
        if (status.user.id_str in TWITTER_TARGETS) and not hasattr(status, 'retweeted_status'):
            self.save_tweet(status)
    def on_error(self, status_code):
        if status_code == 420:
            # print "Error: 420"
            return False

if __name__ == '__main__':
    # listener = StdOutListener()
    listener = StreamListener()
    twitterStream = Stream(auth, listener)
    twitterStream.filter(follow=TWITTER_TARGETS)
