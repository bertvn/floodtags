"""
interacts with the floodtags api
"""
import datetime
import json
import urllib.error
import urllib.request
from time import sleep


class FetchTweets:
    """
    class that calls the floodtags API
    """
    def __init__(self, config):
        """
        constructor for FetchTweets
        :param config: APIConfig object which contains the information needed to make the API call
        :return: None
        """
        self.config = config

    def fetch(self):
        """
        calls api
        :return: tweets
        """
        urlbuilder = ["https://api.floodtags.com/v1/tags/",
                      self.config.get_filter(),
                      "/index?",
                      "omitRetweets=",
                      str(not self.config.get_retweets()).lower(),
                      "&apiKey=",
                      self.config.get_api_key(),
                      "&limit=100"
                      ]

        date = self.config.generate_range()
        base_url = "".join(urlbuilder)
        result = []

        temp = base_url + "&" + date + "&skip="
        index = 0
        while True:
            try:
                response = urllib.request.urlopen(temp + str(index * 100))
                response_string = response.read().decode('utf-8')
                output = json.loads(response_string)
                result += output["tags"]
                # if there are no more tweets left to pull
                if len(output["tags"]) < 100:
                    break
                index += 1
            except urllib.error.HTTPError as error:
                # wait for the API to come back
                sleep(300)
        return result


class APIConfig():
    """
    config class for calling the API
    """
    def __init__(self):
        """
        constructor for APIConfig
        :return: None
        """
        self.apiKey = None
        self.retweets = False
        self.start_date = None
        self.end_date = None
        self.filter = "flood"

    def set_api_key(self, key):
        """
        sets the API key
        :param key: API key
        :return: None
        """
        self.apiKey = key

    def get_api_key(self):
        """
        returns the API key
        :return: API key
        """
        return self.apiKey

    def set_start_time(self, date: datetime.datetime):
        """
        sets the start time
        :param date: datetime object containing the start time
        :return: None
        """
        gmtdifference = datetime.datetime.utcnow() - datetime.datetime.now()
        self.start_date = date + gmtdifference

    def get_start_time(self):
        """
        returns the starting time
        :return: datetime object containing the start time
        """
        return self.start_date

    def set_end_time(self, date: datetime.datetime):
        """
        sets the end time
        :param date: datetime object containing the end time
        :return: None
        """
        gmtdifference = datetime.datetime.utcnow() - datetime.datetime.now()
        self.end_date = date + gmtdifference

    def get_end_time(self):
        """
        returns the end time
        :return: datetime object containing the end time
        """
        return self.end_date

    def set_filter(self, filter):
        """
        sets the datastream name of te API
        :param filter: datastream name to be used
        :return: None
        """
        self.filter = filter

    def get_filter(self):
        """
        returns the datestream name
        :return: String containing the name of the datastream
        """
        return self.filter

    def set_retweets(self, retweets: bool):
        """
        set whether or not retweets are included
        :param retweets: boolean containing whether or not retweets are included
        :return: false
        """
        self.retweets = retweets

    def get_retweets(self):
        """
        gets whether or not retweets are included
        :return: retweet value
        """
        return self.retweets

    def generate_range(self):
        """
        generates the date range used in the API call
        :return: time range string for the API call
        """
        # format: until=2015-12-30T23:00:00.000Z&since=2015-12-16T23:00:00.000Z
        string_builder = ["until=",
                          self.end_date.strftime("%Y-%m-%dT%H:%M:%S.") + str(self.end_date.microsecond // 100) + "Z",
                          "&since=",
                          self.start_date.strftime("%Y-%m-%dT%H:%M:%S.") + str(self.start_date.microsecond // 100) + "Z"
                          ]
        return ''.join(string_builder)
