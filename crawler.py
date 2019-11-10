"""
This module handles all Twitter crawling

Rate limit information:
    - Link: https://developer.twitter.com/en/docs/basics/rate-limiting
    - TLDR: 180 Requests every 15 minutes

"""
import os
import sys
import json
import tweepy

from time import sleep

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
            likes = tweet.favorite_count
            retweets = tweet.retweet_count
            tweet_id = tweet.id
            timestamp = tweet.created_at

            try: # Sometimes the tweet is a retweet
                text = tweet.retweeted_status.full_text
            except: # If it's not, then just add the normal tweet text
                text = tweet.full_text
            
            # Package the tweet
            twitter_result = {
                'keyword_id': keyword._id,
                'tweet_id': tweet_id,
                'text': text,
                'likes': likes,
                'retweets': retweets,
                'timestamp': timestamp,
            }

            twitter_results.append(twitter_result)
        print('Found {} results'.format(len(twitter_results)))
        return twitter_results
