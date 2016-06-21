"""handles interactions with the floodtags api and other data sources"""
import datetime
import json
import re
from abc import ABCMeta

import polyglot.detect

import floodtags.api.crawler as crawler
import os

class APIHandler(object):
    """handles the api"""
    def __init__(self, api):
        """
        constructor for APIHandler
        :param api: class that interacts with the api
        :return: None
        """
        self.api = api
        self.last = datetime.datetime.now() - datetime.timedelta(hours=12)

    def get_tweets(self):
        """
        fetches tweets and wraps them in Tweet objects
        :return: list of tweets
        """
        now = datetime.datetime.now()
        tweet_json = self.api.get_tweets(self.last, now)
        self.last = now
        return [Tweet(x) for x in tweet_json]


class Tweet(object):
    """
    wrapper for tweet dictionary
    """
    def __init__(self, tweet_json):
        """
        constructor for Tweet class
        :param tweet_json: tweet dictionary that needs to be wrapped
        :return:
        """
        self.tweet = tweet_json
        self.date = datetime.datetime.strptime(self.tweet["date"], "%Y-%m-%dT%H:%M:%S.000Z")
        self.processed = False
        self.max_importance = 0
        try:
            text = re.sub(self.tweet["keywords"][0], '', self.tweet["text"])
        except IndexError:
            text = self.tweet["text"]
        try:
            self.language = polyglot.detect.Detector(re.sub('#', '', text)).language.name
        except polyglot.detect.base.UnknownLanguage as e:
            self.language = "mixed"
        except:
            self.language = polyglot.detect.Detector(''.join([i if ord(i) < 128 else ' ' for i in text])).language.name

    def get_language(self):
        """
        get language of tweet according to polyglot
        :return: language string
        """
        return self.language

    def get_processed_text(self):
        """
        get pre-processed tweet
        :return: pre-processed tweet
        """
        return self.processed

    def set_processed_text(self, text):
        """
        set pre-processed tweet
        :param text: pre-processed tweet
        :return: None
        """
        self.processed = text

    def update_importance(self, importance):
        """
        updates max_importance value if importance is higher then max_importance
        :param importance: new importance value
        :return: None
        """
        if importance > self.max_importance:
            self.max_importance = importance

    def get_importance(self):
        """
        get max_importance value
        :return: highest importance value
        """
        return self.max_importance


class AbstractAPI(object, metaclass=ABCMeta):
    """
    Abstract base class for API
    """
    def __init__(self, region):
        """
        constructor for the AbstractAPI
        :param region: datasource
        :return: None
        """
        self.region = region

    def get_tweets(self, start_date, end_date):
        """
        fetches tweets from start date till end date
        :param start_date: datetime that contains the starting point to gather tweets
        :param end_date: datetime that contains the end point for gathering tweets
        :return: tweets
        """
        pass


class API(AbstractAPI):
    """
    API class for getting tweets
    """
    def __init__(self, region):
        """
        constructor for API
        :param region: datastream to be used
        :return: None
        """
        super().__init__(region)

    def get_tweets(self, start_date, end_date):
        """
        fetches tweets from start date till end date
        :param start_date: datetime that contains the starting point to gather tweets
        :param end_date: datetime that contains the end point for gathering tweets
        :return: tweets
        """
        # get tweets from api
        config = crawler.APIConfig()
        config.set_api_key("8e1618e9-419f-4239-a2ee-c0680740a500")
        config.set_end_time(end_date)
        config.set_filter(self.region)
        config.set_start_time(start_date)
        return crawler.FetchTweets(config).fetch()


class FakeAPI(AbstractAPI):
    """
    API class used when either using the demo data or a seperate file instead of the actual API
    """
    def __init__(self, region):
        """
        constructor for FakeAPI
        :param region: datasource
        :return: None
        """
        self.counter = 550
        super().__init__(region)

    def get_tweets(self, start_date, end_date):
        """
        fetches tweets
        :param start_date: unused, is added to match the real API
        :param end_date: unused, is added to match the real API
        :return: tweets
        """
        if self.region == "demo":
            # use tweets from demo set
            result = []
            for i in range(self.counter, (self.counter - 5), -1):
                with open(os.path.join(os.path.dirname(__file__),'demodata/data' + str(i) + '.json'), encoding="utf8") as data_file:
                    result += json.load(data_file)
            self.counter -= 5
            return result
        else:
            #use tweets form file
            with open(self.region, encoding="utf8") as data_file:
                return json.load(data_file)["tags"]
