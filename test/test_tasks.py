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

    # Database config
    db_name = 'twitter_test_task'

    # Setup
    validated = False

    def setUp(self):
        """
        Initialise the database
        """
        if not self.validated: # Only run this once
            self.__ensure_keyword_validity()
            self.validated = True

        self.mongo_controller = MongoController(db_name=self.db_name)
        self.sample_keyword = self.mongo_controller.add_keyword(self.sample_keyword_string, self.sample_keyword_language, self.sample_user, return_object=True,  cast=True)

    def tearDown(self):
        """
        Tear down the database
        """
        self.mongo_controller.client.drop_database(self.db_name)

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
