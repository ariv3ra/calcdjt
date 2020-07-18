import os, sys, datetime, json, tweepy
from tweepy import StreamListener
from tweepy import Stream
from pymongo import MongoClient

CONSUMER_KEY = None
CONSUMER_SECRET = None
ACCESS_KEY = None
ACCESS_SECRET = None
MONGO_URI = None
IMAGE_LIST = None

fpath = os.path.dirname(sys.argv[0])
IMAGE_DIR = os.path.abspath(fpath)+'/kia_imgs/'

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
    RESPONSE_TARGETS = data['RESPONSE_TARGETS']
except IOError as err:
    print("[error] {0}",err.message)

try:
    img_pathname = os.path.dirname(sys.argv[0])
    img_file = os.path.abspath(img_pathname)+'/kia_images.json'
    with open(img_file) as img_file:
        data = json.load(img_file)
    IMAGE_LIST = data
except IOError as err:
    print("[error] {0}",err.message)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

class StreamListener(tweepy.StreamListener):
    def generate_status_url(self, screen_name, tid):
        url = 'https://twitter.com/{0}/status/{1}'.format(screen_name, tid)
        return url
    def percent_response(self, screen_name, percentage, followers, status_url):
        emoji = u"\U0001F447" #pointdown finger
        MSG = '@{0}\n{1} of your {2} Followers Liked this Tweet:\n'.format(screen_name, percentage, followers) \
            + u"\U0001F447" + '\n{0}'.format(status_url)
        return MSG
    def human_format(self, num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        # add more suffixes if you need them
        return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'Q'][magnitude])    
    def percentage(self, part, whole):
        if whole == 0:
            return 0
        else:
            num = round(100 * float(part)/float(whole), 2)
            return "{0}%".format(num)

    def has_tweet(self, tid):
            client = MongoClient(MONGO_URI)
            db = client['djt']
            tweets = db.tweets
            twt = tweets.count_documents({'tid':tid,'processed':True})
            if twt > 0:
                return True
            else:
                return False

    def get_tweet(self, uid):
            client = MongoClient(MONGO_URI)
            db = client['djt']
            tweets = db.tweets
            twt = tweets.find({'processed':False,'uid':uid}).sort('created_at',1).limit(1)
            status_id=''
            for t in twt:
                status_id = t['tid']    
            
            print("Status Id: {0}".format(status_id))

            # Check if tweet exists in Twitter
            try:
                resp_tweet = api.get_status(status_id)
            except tweepy.TweepError as e:
                if e.api_code == 144:
                    # Flag the deleted tweet
                    self.update_tweet_processed(status_id)
                    # Get a new tweet
                    status_id = self.get_tweet(uid)
            return status_id

    # Query MongoDB for messages
    def get_message(self):
        client = MongoClient(MONGO_URI)
        db = client['djt']
        coll_messages = db.messages
        msgs = coll_messages.find({'processed':False}).sort('created_at', 1).limit(1)
        msg = {}
        for m in msgs:
            msg['_id'] = m['_id']
            msg['message'] = m['message']
        print("message: {0}".format(msg))
        return msg

    # Update the messages to True once processed
    def update_messages(self, obj_id):
        msg_id = obj_id
        client = MongoClient(MONGO_URI)
        db = client['djt']
        db.messages.find_one_and_update({'_id':msg_id}, {'$set':{'processed':True}})

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
            twt = tweets.insert_one({'tid':tweet_id, 'uid':user_id, 'screen_name':screen_name, \
                    'reply_to_id':reply_id, 'reply_name':reply_name, 'text':tweet_text, 'created_at':created_at, \
                    'processed':processed} )
            msg = "TID: {0}  UID: {1} Handle: {2} RepToID: {3} RepToName: {4} created_at: {5}"
            print(msg.format(tweet_id, user_id, screen_name, reply_id, reply_name, created_at))
    
    def update_tweet_processed(self, tid):
            client = MongoClient(MONGO_URI)
            db = client['djt']
            tweets = db.tweets
            twt = tweets.update_one({'tid':tid},{'$set':{'processed':True}});
            print("Tweet {0} Processed".format(tid))

    def get_media(self, tweet_message, image_list, image_dir):
        status = False
        img_name = ''
        for name in image_list:
            if name['name'] in tweet_message:
                print('Found Name: {0} | Image: {1}'.format(name['name'], name['img_name']))
                status = True
                img_name = name['img_name']
                break
        return {'found':status, 'img_name':img_name}

    def on_status(self, status):
        status_id = status.id_str
        user_id = status.user.id_str
        scr_name = status.user.screen_name
        
        # Check for tweets & replies from Targets
        if (user_id in TWITTER_TARGETS) and not hasattr(status, 'retweeted_status'):
            # if scr_name == "realDonaldTrump":
                # self.save_tweet(status)
            if scr_name == "whlogz":
                print("The account: {0} just tweeted".format(scr_name))
                # self.save_tweet(status)                
            # get & calculate percentage & reply to tweet
            if (user_id) in RESPONSE_TARGETS and not self.has_tweet(status_id):

                # get status details 
                twt_id = self.get_tweet(user_id)
                twt = api.get_status(twt_id)
                followers_count = twt.user.followers_count
                favorite_count = twt.favorite_count

                # # calculate percentage
                # perc_number = self.percentage(favorite_count, followers_count)
                # abrev_followers =self.human_format(followers_count)
                # # generate the status url
                # twt_url = self.generate_status_url(scr_name, twt_id)
                # resp = self.percent_response(scr_name, perc_number, abrev_followers, twt_url)
                # # reply to new tweet
                # api.update_status(resp,status_id)
                # # Update record as processed
                # self.update_tweet_processed(twt_id)

                #######################################################3
                # Response bot start
                # respond with message

                message = self.get_message()

                if message:
                    obj_id = message['_id']
                    msg = message['message']

                    # Tweet the message
                    resp_message = '@{0}\n{1}'.format(scr_name, msg)

                    # Check the length of tweet
                    if len(resp_message) <= 140:
                        image_name =  self.get_media(resp_message, IMAGE_LIST, IMAGE_DIR)
                        if image_name['found'] == True:
                            # Upload image
                            media = api.media_upload(IMAGE_DIR+image_name['img_name'])
                            # Post tweet with image
                            tweet = resp_message
                            post_result = api.update_status(status=tweet.encode('utf-8'), 
                                        in_reply_to_status_id=status_id, media_ids=[media.media_id])                    
                        else:
                            api.update_status(resp_message.encode('utf-8'), in_reply_to_status_id=status_id)
                    self.update_messages(obj_id)
        else:
            # It's a retweet do nothing
            if (user_id in TWITTER_TARGETS): 
                print('{0}-StatusID:{1} Retweet'.format(scr_name,status_id))

    def on_error(self, status_code):
        if status_code == 420:
            # print "Error: 420"
            return False

if __name__ == '__main__':
    # listener = StdOutListener()
    listener = StreamListener()
    twitterStream = Stream(auth, listener)
    twitterStream.filter(follow=TWITTER_TARGETS)
