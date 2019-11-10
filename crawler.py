"""
This module handles all Twitter crawling

Rate limit information:
    - Link: https://developer.twitter.com/en/docs/basics/rate-limiting
    - TLDR: 180 Requests every 15 minutes

"""
import os
import sys
import json

from time import sleep

import tweepy
from common.config import SUPPORTED_LANGUAGES
from common.utils.read_json import read_json

class TwitterCrawler():
    """
    Interface to the Twitter API
    """
    def __init__(self):
        """
        Import credentials and connect to the Twitter API 
        """
        credentials_path = os.environ['TWITTER_APPLICATION_CREDENTIALS']
        credentials = read_json(credentials_path)

        auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
        auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])

        self.api = tweepy.API(auth)

    @staticmethod
    def tweet_to_dict(keyword, tweet):
        """
        Cast a twitter tweet response object to a dict

        :param Keyword keyword: The target keyword used to find the tweet
        :param Tweet tweet: The returned tweet object
        """
        try:
            text = tweet['text'] # By default take the truncated text
        except:
            text = '' # If all goes wrong, let it be an empty string

        # All the different weird ways twitter hides the full text
        if 'extended_tweet' in tweet:
            if 'full_text' in tweet['extended_tweet']:
                text = tweet['extended_tweet']['full_text']
        elif 'full_text' in tweet:
            text = tweet['full_text']
        elif 'retweeted_status' in tweet:
            if 'extended_tweet' in tweet['retweeted_status']:
                if 'full_text' in tweet['retweeted_status']['extended_tweet']:
                    text = tweet['retweeted_status']['extended_tweet']['full_text']

        likes = tweet['favorite_count']
        retweets = tweet['retweet_count']
        tweet_id = tweet['id']
        timestamp = tweet['created_at']
    
        # Package the tweet
        twitter_result = {
            'keyword_id': keyword._id,
            'tweet_id': tweet_id,
            'text': text,
            'likes': likes,
            'retweets': retweets,
            'timestamp': timestamp,
        }

        return twitter_result

    def search(self, keyword, back_off_time=1, limit=sys.maxsize):
        """
        Search twitter for specific keyword and return just the text

        :param Keyword keyword: The target keyword that should be searched for
        :param int back_off_time: The time the server shoudl sleep before trying to connect again
        :param int limit: The amount of tweets you would like to have returned at most
        """
        if (keyword.language not in SUPPORTED_LANGUAGES):
            raise Exception('Unsupported language "{}"'.format(keyword.language))

        print('Search request for {}'.format(keyword))

        try:
            tweets = self.api.search(keyword.keyword_string, tweet_mode='extended', count=limit, lang=keyword.language, include_entities=True)
        except: # Rate limit was triggered
            print('Rate limit exceeded, waiting {} seconds'.format(back_off_time))

            sleep(back_off_time) # Back off
            back_off_time *= 2 # We run an exponential back off time

            if (back_off_time > (60 * 60)):
                raise Exception('Back off limit has exceeded 60 minutes, there seems to be an issue with the API')

            self.search(keyword, back_off_time, limit) # Retry

        twitter_results = []
        for tweet in tweets:
            twitter_result = self.tweet_to_dict(keyword, json.loads(json.dumps(tweet._json)))

            twitter_results.append(twitter_result)
        print('Found {} results'.format(len(twitter_results)))
        return twitter_results

    def start_stream(self, keyword, mongo_controller):
        """
        Start a new stream watching tweets containing a target

        :param Keyword keyword: The target keyword
        :param MongoController mongo_controller: A db controller unit to save the incoming results
        """
        # Configure listener
        stream_listener = TwitterStreamListener(keyword, self.api, mongo_controller)
        stream = tweepy.Stream(auth=self.api.auth, listener=stream_listener, tweet_mode='extended')

        # Start streaming
        print('Start streaming content from {}'.format(keyword))
        stream.filter(track=[keyword.keyword_string], languages=[keyword.language], is_async=True)


class TwitterStreamListener(tweepy.StreamListener):
    """
    Listener which listenes to tweets being posted
    """
    def __init__(self, keyword, api, mongo_controller):
        """
        Initialise Listener

        :param Keyword keyword: The target keyword used for streaming
        :param API api: The twitter API object
        :param MongoController mongo_controller: The controller used to store incoming data
        """
        self.keyword = keyword
        self.api = api
        self.mongo_controller = mongo_controller

    def on_data(self, tweet):
        """
        React to incoming data
        """
        tweet = json.loads(tweet)

        # Cast the tweet
        twitter_result = TwitterCrawler.tweet_to_dict(self.keyword, tweet)

        # Save tweet in db
        self.mongo_controller.add_crawl_twitter(
            twitter_result['keyword_id'],
            twitter_result['tweet_id'],
            twitter_result['text'],
            twitter_result['likes'],
            twitter_result['retweets'],
            twitter_result['timestamp'],
        )

    def on_error(self, status_code):
        """
        React to errors
        """
        if status_code == 420: # Rate limit exceeded
            return True # Use back off strategy
