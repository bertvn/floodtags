"""
module containing output formatters for the result of the algorithm
"""
import os
import sys
from abc import ABCMeta


class AbstractFormatter(metaclass=ABCMeta):
    def __init__(self, output):
        """
        constructor for the Abstract Base Class AbstractFormatter
        :param output: location for output
        :return: None
        """
        self.tweets = []
        self.clusters = []
        self.accounts = []
        self.order = []
        self.locations = []

        if output.endswith("/"):
            output += "result.json"

        if sys.platform.startswith('win'):
            if output.startswith("/"):
                output = os.getcwd() + output
        else:
            if output.startswith("./"):
                output = os.getcwd() + output[1:]

        self.output = output

    def set_tweets(self, tweets):
        """
        set tweets
        :param tweets: tweets that are to be used as output
        :return: None
        """
        self.tweets = tweets

    def set_original_tweets(self, tweets):
        """
        set original un orderded tweets
        :param tweets: original tweets
        :return: None
        """
        pass

    def set_clusters(self, clusters, order):
        """
        set cluster and order of clusters
        :param clusters: clusters of clustered tweets
        :param order: order of priority of the clusters
        :return: None
        """
        self.clusters = clusters
        self.order = order

    def set_newsaccounts(self, accounts):
        """
        set newsaccount
        :param accounts: accounts that belong to news agencies
        :return: None
        """
        self.accounts = accounts

    def set_locations(self, locations):
        """
        sets locations
        :param locations: set locations found in the tweets
        :return: None
        """
        self.locations = locations

    def output_result(self):
        """
        create output file
        :return: None
        """
        pass


class FormatResult(AbstractFormatter):
    """
    Result formatter used for the web application
    """

    def __init__(self, output):
        """
        Constructor for FormatResult
        :param output: location for output
        :return: None
        """
        super().__init__(output)

    def output_result(self):
        """
        creates the output file
        :return: None
        """
        result = ["{\"clusters\" : ", self._output_clusters(), ",\"news\" : "]
        if self.accounts:
            result.append(self._output_news())
        else:
            result.append("[]")

        result.append(", \"locations\" : ")
        if self.locations:
            result.append(self._output_locations())
        else:
            result.append("[]")

        result.append("}")
        writer = open(self.output, "w",
                      encoding='utf-8')
        writer.write(''.join(result))
        writer.close()

    def _output_clusters(self):
        """
        formats the clusters for use in the web application
        :return: JSON string representation of the clusters
        """
        result = ["["]
        for i in range(0, 10):
            result.append(
                "{\"cluster\": " + str(i) + ", \"lcs\" : \"" + self.clusters[
                    self.order[i][0]].lcs + "\", \"tweets\" : [")
            temp = self.clusters[self.order[i][0]].get_five_latest()
            for j in range(0, len(temp)):
                result.append(
                    "{\"id\" : \"" + temp[j].tweet["source"]["id"] + "\",\"username\" : \"" + temp[j].tweet["source"][
                        "username"] + "\"}")
                result.append(",")
            del result[-1]
            result.append("]}")
            result.append(",")
        del result[-1]
        result.append("]")
        return ''.join(result)

    def _output_news(self):
        """
        gathers the latest 5 news tweets and formats them for the web application
        :return: JSON representation of the 5 latest news tweets
        """
        result = ["["]
        newstweets = [tweet for tweet in self.tweets if tweet.tweet["source"]["username"] in self.accounts]
        sorted(newstweets, key=lambda tweet: tweet.date, reverse=True)
        amount = 5
        if len(newstweets) < amount:
            amount = len(newstweets)
        for i in range(amount):
            result.append(
                "{\"id\" : \"" + newstweets[i].tweet["source"]["id"] + "\",\"username\" : \"" +
                newstweets[i].tweet["source"][
                    "username"] + "\"}")
            result.append(",")
        del result[-1]
        result.append("]")
        return ''.join(result)

    def _output_locations(self):
        """
        formats the locations found in the tweets for use in the web application
        :return: JSON string representation of the locations
        """
        result = ["["]
        for location in self.locations:
            result.append("\"" + location + "\"")
            result.append(",")
        del result[-1]
        result.append("]")
        return ''.join(result)


class JsonFormat(AbstractFormatter):
    # TODO make a formatter that adds importance to the original tweets from the server
    pass


class RatingFormat(AbstractFormatter):
    """
    formatter for using the algorithm in the pipeline
    """

    def __init__(self, output):
        """
        constructor for RatingFormat
        :param output: location for the output file
        :return: None
        """
        self.origin = []
        super().__init__(output)

    def set_original_tweets(self, tweets):
        """
        sets the original tweets pre removing, clustering and filtering
        :param tweets: original tweets
        :return: None
        """
        self.origin = tweets

    def output_result(self):
        """
        creates the output file
        :return: None
        """

        result = ["["]
        for ori in self.origin:
            found = False
            for cluster in self.clusters:
                for tweet in cluster.get_tweets():
                    if ori.tweet["source"]["id"] == tweet.tweet["source"]["id"]:
                        result.append("{\"id\" : \"" + str(tweet.tweet["source"]["id"]) + "\", \"importance\" : " + str(
                            tweet.get_importance()) + "}")
                        result.append(",")
                        found = True
                        break
                if found:
                    break
            if not found:
                result.append("{\"id\" : \"" + str(ori.tweet["source"]["id"]) + "\", \"importance\" : " + str(
                    ori.get_importance()) + "}")
                result.append(",")

        del result[-1]
        result.append("]")
        writer = open(self.output, "w",
                      encoding='utf-8')
        writer.write(''.join(result))
        writer.close()


class ClusterFormat(AbstractFormatter):
    """
    formatter for using the algorithm in the pipeline v2
    """

    def __init__(self, output):
        """
        constructor for ClusterFormat
        :param output: location for the output file
        :return: None
        """
        self.origin = []
        super().__init__(output)

    def set_original_tweets(self, tweets):
        """
        sets the original tweets pre removing, clustering and filtering
        :param tweets: original tweets
        :return: None
        """
        self.origin = tweets

    def output_result(self):
        """
        creates the output file
        :return: None
        """
        spam = []
        result = ["["]
        for ori in self.origin:
            found = False
            for cluster in self.clusters:
                for tweet in cluster.get_tweets():
                    if ori.tweet["source"]["id"] == tweet.tweet["source"]["id"]:
                        found = True
                        break
                if found:
                    break
            if not found:
                spam.append(str(ori.tweet["source"]["id"]))
        index = -1
        print(len(self.clusters), " : ", len(self.order))
        for i in range(len(self.clusters)):
            clust = ["{\"id\" : "]
            clust.append(str(i))
            clust.append(", \"score\" : ")
            try:
                clust.append(str(self.order[i][1]))
            except:
                clust.append("0")
            clust.append(", \"summary\" : \"")
            clust.append(self.clusters[self.order[i][0]].lcs)
            clust.append("\", \"ids\" : [")
            for tweet in self.clusters[self.order[i][0]].get_tweets():
                clust.append(str(tweet.tweet["source"]["id"]))
                clust.append(",")
            del clust[-1]
            clust.append("]}")
            result.append(''.join(clust))
            result.append(",")
            index = i
        clust = ["{\"id\" : "]
        clust.append(str(i))
        clust.append(", \"score\" : 0")
        clust.append(", \"summary\" : \"spam\"")
        clust.append("\", \"ids\" : [")
        for id in spam:
            clust.append(id)
            clust.append(",")
        del clust[-1]
        clust.append("]}")
        result.append(''.join(clust))
        result.append("]")
        writer = open(self.output, "w",
                      encoding='utf-8')
        writer.write(''.join(result))
        writer.close()


class TestFormat(AbstractFormatter):
    """
    formatter used to print the top 20 clusters and their 5 lates tweets
    """

    def __init__(self, output):
        """
        constructor for TestFormat
        :param output: location of the output file
        :return: None
        """
        super().__init__(output)

    def output_result(self):
        """
        creates the output file
        :return: None
        """
        writer = open(self.output, "w", encoding='utf-8')
        for i in range(20):
            writer.write("-" * 79 + "\n")
            writer.write("cluster " + str(i) + "\n")
            writer.write("importance value: " + str(self.order[i][1]) + "\n")
            writer.write("lcs: " + self.clusters[self.order[i][0]].lcs + "\n")
            writer.write("-" * 79 + "\n")
            writer.write("-" * 79 + "\n")
            tweets = self.clusters[self.order[i][0]].get_tweets()
            for tweet in tweets:
                writer.write(tweet.tweet["text"] + "\n")
                writer.write("-" * 79 + "\n")
        writer.close()
