
from tweepy import StreamListener
from tweepy import Stream
import tweepy
import json, jira

CONSUMER_KEY=None
CONSUMER_SECRET=None
ACCESS_KEY=None
ACCESS_SECRET=None

try:
    with open('config.json') as data_file:    
        data = json.load(data_file)
    # Salt Creds
    CONSUMER_KEY = data['CONSUMER_KEY']
    CONSUMER_SECRET = data['CONSUMER_SECRET']
    ACCESS_KEY = data['ACCESS_KEY']
    ACCESS_SECRET = data['ACCESS_SECRET']
except IOError as e:
      print "[error] "+e.message


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

class StdOutListener(StreamListener):

    def on_data(self, data):
        # process stream data here
        print(data)

    def on_error(self, status):
        print(status)

# class StreamListener(tweepy.StreamListener):
    
#     def on_status(self, status):
        
#         print status
#         print "ID:{0}  Text: {1} Followers: {2}".format(status.id, status.text.encode('utf-8'), status.user.followers_count)
        
#     def on_error(self, status_code):
#         if status_code == 420:
#             print("Error: 420")
#             return False

if __name__ == '__main__':
    listener = StdOutListener()
    # listener = StreamListener()
    twitterStream = Stream(auth, listener)
    twitterStream.filter(follow=['345041995'])
    #twitterStream.filter(follow=['18382184'])

