import unittest
import os

from common.exceptions.parameters import InvalidParameterError, UnsupportedLanguageError
from common.mongo.controller import MongoController
from bson import ObjectId

from tasks import crawl_twitter_keyword

class TestTasks(unittest.TestCase):
    # Fixtures
    sample_user = 'sample user'
    sample_keyword_string = 'House'
    sample_keyword_language = 'en'

    # Setup
    validated = False

    def setUp(self):
        """
        Initialise the database
        """
        self.mongo_controller = MongoController()
        self.sample_keyword = self.mongo_controller.add_keyword(self.sample_keyword_string, self.sample_keyword_language, self.sample_user, return_object=True,  cast=True)
        
        if not self.validated: # Only run this once
            self.__ensure_keyword_validity()
            self.validated = True

    def tearDown(self):
        """
        Tear down the database
        """
        self.mongo_controller.client.drop_database(os.environ['MONGO_DATABASE_NAME'])

    def __ensure_keyword_validity(self):
        """
        Make sure that the sample keyword produces valid results
        """
        result = crawl_twitter_keyword(self.sample_keyword_string, self.sample_keyword_language)
        if result:
            return True
        else: # If twitter didn't return any results use a different keyword
            self.sample_keyword_string = 'Garden'
            self.sample_keyword_language = 'en'
            self.sample_keyword = self.mongo_controller.add_keyword(self.sample_keyword_string, self.sample_keyword_language, self.sample_user, return_object=True,  cast=True)
            return False

    def test_crawl_twitter_keyword(self):
        """
        Test a full run and that it was successful
        """
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
