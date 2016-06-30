"""
module for grading the importance of clusters
"""
import floodtags.core.statics
import floodtags.datascience.filtering.algorithms as algorithms
import floodtags.linguistics.sanitizing.regexhandler as regex
from collections import Counter


class Filter(object):
    """
    Class for grading the importance of all clusters
    """
    def __init__(self):
        """
        constructor for Filter
        :return:
        """
        self.data = []

    def set_data(self, data):
        """
        set clusters that need to be analyzed for importance values
        :param data: list of clusters
        :return: None
        """
        self.data = data

    def start_filtering(self):
        """
        calculate the importance values
        :return: list containing the order of the clusters based on importance
        """
        clanalysis = ClusterAnalysis()
        ratings = []
        for cluster in self.data:
            if cluster.get_length() <= 3:
                ratings.append(-100)
            else:
                ratings.append(clanalysis.analyze_cluster(cluster))
        order = []
        while max(ratings) >= 0:
            value = max(ratings)
            index = ratings.index(value)
            order.append((index, value))
            ratings[index] = -1
        return order


class ClusterAnalysis(object):
    """
    class for grading the importance of a cluster
    """
    def __init__(self):
        """
        constructor for ClusterAnalysis
        :return: None
        """
        self.data = []
        self.twan = TweetAnalysis()
        self.lcs = algorithms.LongestCommonSubstring()

    def analyze_cluster(self, cluster):
        """
        calculate the importance value of the cluster
        :param cluster: cluster of which the importance value needs to be calculated
        :return: importance value (between 0 and 1)
        """
        res = 1.0
        cs = cluster.get_cosine_sim()
        res *= (1.01 - (cs / 2))
        word_count = 5
        if cs >= 0.5:
            lcs = algorithms.LongestCommonSubstring()
            twt = lcs.lcs_cluster(cluster)
            if len(twt) > 8:
                cluster.lcs = twt
                mlp = (((len(twt) - 8)) * 2) + 1
                res *= mlp
            else:
                # top 5 words is stored as lcs
                words = []
                for tweet in cluster.get_tweets():
                    words += [word.lower() for word in tweet.tweet["text"].split() if len(word) > 3]
                count = Counter(words)
                flcs = []
                for word in count.most_common(word_count):
                    flcs.append(word[0])
                cluster.lcs = ", ".join(flcs)
            usr = lcs.lcs_cluster_usernames(cluster)
            if len(usr) > 5:
                res * (1 + (len(usr) / 10))
        else:
            # top 10 words is stored as lcs
            words = []
            for tweet in cluster.get_tweets():
                words += [word.lower() for word in tweet.tweet["text"].split() if len(word) > 3]
            count = Counter(words)
            flcs = []
            for word in count.most_common(word_count):
                flcs.append(word[0])
            cluster.lcs = ", ".join(flcs)

        for tweet in cluster.get_tweets():
            res *= (self.twan.analyze_tweet(tweet))
        result = self.normalize(res, cluster.get_length())
        cluster.set_importance(result)
        return result

    @staticmethod
    def normalize(value, clustersize):
        """
        nomralize the importance value of the cluster
        :param value: unnormalized importance value
        :param clustersize: size of the cluster
        :return:
        """
        max = (0.60 * 9605 * 2.2 * (1.08171 ** clustersize)) / clustersize
        min = 1.01 / clustersize
        return (value - min) / (max - min)


class TweetAnalysis():
    """
    class for grading the importance of a tweet
    """
    def __init__(self):
        """
        constructor for TweetAnalysis
        :return: None
        """
        self.language = floodtags.core.statics.StaticData.language
        self.keyword = floodtags.core.statics.StaticData.keyword
        self.regex_handler = regex.RegexHandler()

    def analyze_tweet(self, tweet):
        """
        calculate importance value of tweet
        :param tweet: tweet that needs to be analyzed
        :return: importance value
        """
        res = 1.0
        if tweet.language != self.language:
            return res
        if self.keyword in tweet.tweet["keywords"]:
            res *= 1.01
        if tweet.tweet["photos"]:
            res *= 1.02
        if self.regex_handler.exists(tweet.tweet["text"], regex.Expressions.waterheight):
            res *= 1.05
        return res
