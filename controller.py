"""
Module to hanlde different scripts that the crawler can execute
"""

import bson

from common.mongo.controller import MongoController
from common.mongo.data_types.keyword import Keyword

from crawler import TwitterCrawler

class Controller():
    """
    Hanldes the different scripts and order of execution
    """
    def __init__(self):
        """
        Initialise the crawler
        """
        self.crawler = TwitterCrawler()
        self.mongo_controller = MongoController()

    def __save_tweet(self, twitter_result):
        """
        Save a twitter result to the MongoDb

        :param dict twitter_result: The result received packaged up
        """
        return self.mongo_controller.add_crawl_twitter(
            twitter_result['keyword_id'],
            twitter_result['tweet_id'],
            twitter_result['text'],
            twitter_result['likes'],
            twitter_result['retweets'],
            twitter_result['timestamp'],
        )

    def __save_tweets(self, twitter_results):
        for twitter_result in twitter_results:
            self.__save_tweet(twitter_result)

    def enable_streams(self, keywords):
        for keyword in keywords:
            self.crawler.start_stream(keyword, self.mongo_controller)

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

                keyword = Keyword.mongo_result_to_keyword(keyword_dict) # Cast the keyword to a Keyword object
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

                keyword = Keyword.mongo_result_to_keyword(keyword_dict) # Cast the keyword to a Keyword object
                twitter_results = self.crawler.search(keyword, limit=10) # Run the search
                self.__save_tweets(twitter_results) # Save all tweets to the DB
