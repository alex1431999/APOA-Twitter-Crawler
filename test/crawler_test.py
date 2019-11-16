import unittest
import json

from datetime import datetime
from unittest.mock import Mock, patch
from tweepy import API

from common.mongo.data_types.keyword import Keyword
from crawler import TwitterCrawler

class TwitterAPIMock():
    """
    This class is a mock version of the
    API object that is returned after logging
    into the Twitter API
    """
    def __init__(self):
        self.search_result = [TwitterAPIResult('some text')]

    def search(self):
        """
        This function is a place holder that can be mocked
        within the testing
        """
        pass

class TwitterAPIResult():
    """
    This class simulates what a basic
    Twitter search api result looks like
    """
    def __init__(self, text):
        self.full_text = text
        self.favorite_count = 1
        self.retweet_count = 1
        self.id = 0
        self.created_at = datetime.now()

    @property
    def _json(self):
        """
        Mock version of _json function
        """
        return { 
            'full_text': self.full_text,
            'favorite_count': self.favorite_count,
            'retweet_count': self.retweet_count,
            'id': self.id,
            'created_at': self.created_at.strftime("%d:%m:%y"),
        }

class TestGoogleCloudLanguageProcessor(unittest.TestCase):
    """
    Testing Setup
    """
    def setUp(self):
        # Mocking
        self.twitter_api_mock_object = TwitterAPIMock()
        self.mock_twitter_api()
        
        # Crawler
        self.crawler = TwitterCrawler()
        

    def mock_twitter_api(self):
        self.twitter_API_mock = patch('tweepy.API')
        self.twitter_API_mock.start()
        self.twitter_API_mock.return_value = self.twitter_api_mock_object

    def test_construction(self):
        crawler = TwitterCrawler()
        self.assertIsNotNone(crawler)

    def test_api_connection(self):
        api = self.crawler.api
        self.assertIsNotNone(api) # api is mocked

    def test_search(self):
        self.crawler.api.search.return_value = [TwitterAPIResult('some text')] # Mock the result from searching

        twitter_results = self.crawler.search(Keyword(0, 'some text', 'en'))
        self.assertEqual(len(twitter_results), 1, 'Only one element should have been returned')
        self.assertEqual(twitter_results[0]['text'], 'some text', 'The text returned should match the mocking text')

