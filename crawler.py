"""
This module handles all Twitter crawling
"""
import os
import sys
import json
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

    def search_keyword(self, keyword_string, language, limit=sys.maxsize):
        """
        Search twitter for specific keyword and return just the text

        :param str keyword_string: The target keyword that should be searched for
        :param str language: The language that should be used for the search
        :param int limit: The amount of tweets you would like to have returned at most
        """
        if (language not in SUPPORTED_LANGUAGES):
            raise Exception('Unsupported language "{}"'.format(language))

        tweets = self.api.search(keyword_string, tweet_mode='extended', count=limit, lang=language, include_entities=True) # For now default to english
        twitter_results = []
        for tweet in tweets:
            likes = tweet.favorite_count
            retweets = tweet.retweet_count
            id = tweet.id
            try: # Sometimes the tweet is a retweet
                text = tweet.retweeted_status.full_text
                twitter_result = TwitterResult(id, keyword_stringm, language, text, likes=likes, retweets=retweets)
                twitter_results.append(twitter_result)
            except: # If it's not, then just add the normal tweet text
                text = tweet.full_text
                twitter_result = TwitterResult(id, keyword_string, language, text, likes=likes, retweets=retweets)
                twitter_results.append(twitter_result)
        return twitter_results
