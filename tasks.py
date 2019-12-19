"""
This module defines all the Celery tasks which this crawler can execute.
It also runs all the setup required for celery to function.
"""
import os

from celery import Celery
from common.utils.logging import DEFAULT_LOGGER, LogTypes

app = Celery('tasks',
    broker = os.environ['BROKER_URL']
)

from controller import Controller

controller = Controller()

@app.task(name='crawl-twitter-keyword')
def crawl_twitter_keyword(keyword_string, language):
    """
    Crawl a single keyword Task

    :param str keyword_string: The target keyword string
    :param str language: The target language
    """
    DEFAULT_LOGGER.log('Received twitter keyword crawl request for {} ({})'.format(keyword_string, language), log_type=LogTypes.INFO.value)
    controller.run_single_keyword(keyword_string, language)
