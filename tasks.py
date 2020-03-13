"""
This module defines all the Celery tasks which this crawler can execute.
It also runs all the setup required for celery to function.
"""
import os

from common.exceptions.parameters import InvalidParameterError, UnsupportedLanguageError
from common.utils.logging import DEFAULT_LOGGER, LogTypes
from common.config import SUPPORTED_LANGUAGES
from common.celery import queues
from celery import Celery

app = Celery('tasks',
    broker = os.environ['BROKER_URL']
)

from controller import Controller

@app.task(name='crawl-twitter-keyword', queue=queues['twitter'])
def crawl_twitter_keyword(keyword_string, language):
    """
    Crawl a single keyword Task

    :param str keyword_string: The target keyword string
    :param str language: The target language
    """
    # Validation
    if keyword_string is None or keyword_string == '': raise InvalidParameterError(keyword_string)
    if language not in SUPPORTED_LANGUAGES: raise UnsupportedLanguageError(language)

    controller = Controller()
    DEFAULT_LOGGER.log('Received twitter keyword crawl request for {} ({})'.format(keyword_string, language), log_type=LogTypes.INFO.value)
    results = controller.run_single_keyword(keyword_string, language)

    return [result.to_json() for result in results]
