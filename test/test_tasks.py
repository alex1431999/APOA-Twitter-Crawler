import unittest
import os

from common.exceptions.parameters import InvalidParameterError, UnsupportedLanguageError
from common.mongo.controller import MongoController
from unittest.mock import Mock, patch
from bson import ObjectId

from mocks.mock_tweepy import TwitterAPIMock, TwitterAPIResult
from tasks import crawl_twitter_keyword

class TestTasks(unittest.TestCase):
    # Fixtures
    sample_user = 'sample user'
    sample_keyword_string = 'House'
    sample_keyword_language = 'en'

    def setUp(self):
        """
        Initialise the database
        """
        # Mocking
        self.mock_twitter_api()

        # Database
        self.mongo_controller = MongoController()
        self.sample_keyword = self.mongo_controller.add_keyword(self.sample_keyword_string, self.sample_keyword_language, self.sample_user, return_object=True,  cast=True)

    def tearDown(self):
        """
        Tear down the database
        """
        self.mongo_controller.client.drop_database(os.environ['MONGO_DATABASE_NAME'])
        
        # Mocks
        self.twitter_API_mock.stop()

    def mock_twitter_api(self):
        self.twitter_api_mock_object = TwitterAPIMock()
        self.twitter_API_mock = patch('tweepy.API')
        self.twitter_API_mock.start()
        self.twitter_API_mock.return_value = self.twitter_api_mock_object

    @patch('tweepy.Cursor')
    def test_crawl_twitter_keyword(self, tweepy_cursor_mock):
        """
        Test a full run and that it was successful
        """
        tweepy_cursor_mock.return_value.items.return_value = [TwitterAPIResult('some text')]

        result = crawl_twitter_keyword(self.sample_keyword.keyword_string, self.sample_keyword.language)
        self.assertTrue(result)

    def test_crawl_twitter_keyword_invalid_keyword(self):
        """
        Test for invalid keyword inputs
        """
        self.assertRaises(InvalidParameterError, crawl_twitter_keyword, None, self.sample_keyword.language)

    def test_crawl_twitter_keyword_unsupported_language(self):
        """
        Test for invalid keyword inputs
        """
        self.assertRaises(UnsupportedLanguageError, crawl_twitter_keyword, self.sample_keyword.keyword_string, None)
