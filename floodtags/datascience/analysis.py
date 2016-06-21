"""
analyzes the tweets to find which language the dataset is and what keyword is the most frequent
"""
from random import randrange
from collections import Counter


class AnalyzeDataSet(object):
    """
    class for analyzing the twitter dataset
    """
    def __init__(self):
        """
        constructor for AnalyzeDataSet
        :return: None
        """
        self.data = []

    def set_data(self, data):
        """
        sets the twitter data
        :param data: twitter dataset
        :return: None
        """
        self.data = data

    def start_analysis(self):
        """
        starts analysis of the dataset
        :return: tuple containing the most frequent keyword and language (keyword, language)
        """
        try:
            keywords = [tweet.tweet["keywords"][0] for tweet in self.data]
        except IndexError:
            keywords = ["flood"]
        languages = self.get_lang()
        return (self.most_common(keywords), self.most_common(languages))

    def get_lang(self):
        """
        finds languages used in the dataset
        :return: list of used languages
        """
        dataset = self.get_random(int(len(self.data) / 100))
        languages = []
        for tweet in dataset:
            languages.append(tweet.language)
        return languages

    def most_common(self, lst):
        """
        gets the most frequent element in lst
        :param lst: dataset that needs to be analyzed
        :return: most frequent element in lst
        """
        data = Counter(lst)
        return data.most_common(1)[0][0]

    def get_random(self, amount):
        """
        selects the specified amount of random tweets
        :param amount: amount of tweets
        :return: list of random tweets
        """
        random_selection = []

        for i in range(0, amount):
            while True:
                rnd = randrange(0, len(self.data))
                if self.data[rnd] not in random_selection:
                    if len(self.data[rnd].tweet["text"].split()) > 3:
                        random_selection.append(self.data[rnd])
                        break

        return random_selection
