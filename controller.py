"""
Module to hanlde different scripts that the crawler can execute
"""
import os
import sys
import bson

from datetime import datetime

from common.mongo.controller import MongoController
from common.mongo.data_types.keyword import Keyword
from common.celery import queues

from crawler import TwitterCrawler
from tasks import app

class Controller():
    """
    Hanldes the different scripts and order of execution
    """
    def __init__(self):
        """
        Initialise the crawler
        """
        if 'TWEET_LIMIT_REQUEST_EACH' in os.environ:
            self.limit_requests = int(os.environ['TWEET_LIMIT_REQUEST_EACH'])
        else:
            self.limit_requests = sys.maxsize

        self.crawler = TwitterCrawler()
        self.mongo_controller = MongoController()

    def __save_tweet(self, twitter_result):
        """
        Save a twitter result to the MongoDb

        :param dict twitter_result: The result received packaged up
        """
        timestamp = twitter_result['timestamp']

        # Remove +0000 from timestamp
        timestamp_split = timestamp.split(' ')
        timestamp = ''
        for piece in timestamp_split:
            if piece[0] is not '+':
                timestamp += piece + ' '

        # Remove trailing space
        timestamp = timestamp[:-1]

        # Cast to iso format
        timestamp = datetime.strptime(timestamp, "%a %b %d %H:%M:%S %Y").isoformat()

        crawl = self.mongo_controller.add_crawl_twitter(
            twitter_result['keyword_id'],
            twitter_result['tweet_id'],
            twitter_result['text'],
            twitter_result['likes'],
            twitter_result['retweets'],
            timestamp,
            return_object=True,
            cast=False,
        )

        app.send_task('process-crawl', kwargs={ 'crawl_dict': crawl }, queue=queues['processor'])

        return crawl

    def __save_tweets(self, twitter_results):
        """
        Save all tweets

        :param list<dict> twitter_results: The to be saved twitter results
        """
        crawls = [self.__save_tweet(twitter_result) for twitter_result in twitter_results]
        return crawls

    def enable_streams(self, keywords):
        """
        Start a new stream for each of the keywords

        :param list<Keyword> keywords: The target keywords
        """
        for keyword in keywords:
            self.crawler.start_stream(keyword, self.mongo_controller)

    def run_single_keyword(self, keyword_string, language):
        """
        Execute a search request for a single target

        :param str keyword_string: Target keyword string
        :param str language: Target language
        """
        keyword = self.mongo_controller.get_keyword(keyword_string, language, cast=True)
        twitter_results = self.crawler.search(keyword, limit=self.limit_requests)
        return self.__save_tweets(twitter_results)

    def run_streaming(self):
        """
        Get all keywords and enable streaming for each of them
        """
        # Get a cursor of all the keywords in the databse
        keyword_cursor = self.mongo_controller.get_keyword_batch_cursor()

        # Go over each batch
        for batch in keyword_cursor:

            # Go over each keyword in the batch
            for keyword_dict in bson.decode_all(batch):

                keyword = Keyword.from_dict(keyword_dict) # Cast the keyword to a Keyword object
                self.enable_streams([keyword])

    def run_full(self):
        """
        Get all keywords and run a crawl over them
        """
        # Get a cursor of all the keywords in the databse
        keyword_cursor = self.mongo_controller.get_keyword_batch_cursor()

        # Go over each batch
        for batch in keyword_cursor:

            # Go over each keyword in the batch
            for keyword_dict in bson.decode_all(batch):

                keyword = Keyword.from_dict(keyword_dict) # Cast the keyword to a Keyword object
                twitter_results = self.crawler.search(keyword, limit=self.limit_requests) # Run the search
                self.__save_tweets(twitter_results) # Save all tweets to the DB
