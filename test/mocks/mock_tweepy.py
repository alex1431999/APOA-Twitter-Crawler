from datetime import datetime

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
            'created_at': self.created_at.strftime('%a %b %d %H:%M:%S %Y'),
        }
