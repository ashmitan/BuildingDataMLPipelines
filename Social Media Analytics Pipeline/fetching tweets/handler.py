import os
import json
import s3uploader
import tweepy as tw
import urllib.parse
from datetime import date, datetime


class TweetCollector:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.api = self.authorize(consumer_key, consumer_secret, access_token, access_token_secret)

    def authorize(self, con_key, con_secret, acc_token, acc_token_secret):
        auth = tw.OAuthHandler(con_key, con_secret)
        auth.set_access_token(acc_token, acc_token_secret)
        api = tw.API(auth, wait_on_rate_limit=True)
        return api

    def scrapper(self, search_words, lang="en", limit=None):
        twitter_feeds = []
        # api = authorize(consumer_key, consumer_secret,access_token, access_token_secret)
        for tweet in tw.Cursor(self.api.search, q=search_words, lang=lang).items(limit):
            #   print (tweet.created_at, tweet.text)
            dict_ = {'id': tweet.id_str,
                     'screenname': tweet.user.screen_name,
                     'username': tweet.user.name,
                     'created_at': tweet.created_at,
                     'text': tweet.text.encode('utf-8').decode('utf-8'),
                     'location': tweet.user.location.encode('utf-8').decode('utf-8'),
                     'coordinates': tweet.coordinates
                     }
            twitter_feeds.append(dict_)

        return twitter_feeds

    # input your credentials here


consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
bucket_name = "info7374-twitter-analytics"


def main(event, context):
    tc = TweetCollector(consumer_key, consumer_secret, access_token, access_token_secret)
    comp_list = ["coronavirus", "coronavirusoutbreak","coronavirusinis"]
    for search_query in comp_list:
        twitter_feeds = tc.scrapper(search_query, "en", 500)
        # to_json = json.dumps(twitter_feeds,indent=4, sort_keys=True, default=str)
        object_name = search_query + "/" + "tweet.json"
        output_obj_path = os.path.join("Raw/", object_name)
        print(output_obj_path)
        flag = s3uploader.put_object(bucket_name, output_obj_path,
                                     json.dumps(twitter_feeds, indent=4, sort_keys=True, default=str))
        if (flag == True):
            print("inserted")


if __name__ == '__main__':
    print("Getting twitter data")
    main("", "")
