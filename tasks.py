"""
This module defines all the Celery tasks which this crawler can execute.
It also runs all the setup required for celery to function.
"""
import os

from common.utils.logging import DEFAULT_LOGGER, LogTypes
from common.celery import queues
from celery import Celery

app = Celery('tasks',
    broker = os.environ['BROKER_URL']
)

from controller import Controller

controller = Controller()

@app.task(name='crawl-twitter-keyword', queue=queues['twitter'])
def crawl_twitter_keyword(keyword_string, language):
    """
    Crawl a single keyword Task

    :param str keyword_string: The target keyword string
    :param str language: The target language
    """
    DEFAULT_LOGGER.log('Received twitter keyword crawl request for {} ({})'.format(keyword_string, language), log_type=LogTypes.INFO.value)
    result = controller.run_single_keyword(keyword_string, language)

    return True if result else False
