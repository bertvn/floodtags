"""
module for clustering tweets
"""
import multiprocessing as mp
import re
from abc import ABCMeta
from itertools import repeat

from nltk.stem.snowball import SnowballStemmer
from sklearn.cluster.k_means_ import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import floodtags.core.statics
import floodtags.linguistics.ner.ner
import floodtags.linguistics.sanitizing.regexhandler as regex


def recluster(cluster, min_size, guard, func):
    """
    reclusters clusters until they are below or equal to min_size or if the result of func is higher then the guard
    :param cluster: cluster that is to be reclustered
    :param min_size: minimal allowed size for clusters
    :param guard: minimum value of func for cluster to be concise enough
    :param func: function used to calculate if it exceeds guard
    :return: Cluster or list of clusters or None in case cluster is empty
    """
    if cluster.get_length() == 0:
        return
    if cluster.get_length() <= min_size:
        return cluster
    sim = func(cluster.get_tweets())
    if sim < guard:
        kmeans = TweetKMeans(2)
        kmeans.set_data(cluster.get_tweets())
        return kmeans.start_algorithm()
    return cluster


class Vectorizer:
    """
    class used to vectorize tweets
    """

    def vectorize_data(self, data, idf=False):
        """
        turns tweets into vector representations
        :param data: tweets that are to be vectorized.
        :param idf: wether or not to use tf-idf or just tf, default is False
        :return: sparse vector array
        """

        # collect only the cleaned text of the tweet
        text = []
        for tweet in data:
            if not tweet.get_processed_text():
                tweet.set_processed_text(self.clean_tweet(tweet))
            text.append(tweet.get_processed_text())

        # vectorize tweets

        if idf:
            vectorizer = TfidfVectorizer(min_df=((len(data) // 1000) + 1), max_df=10000, ngram_range=(1, 3))
        else:
            vectorizer = CountVectorizer(min_df=((len(data) // 1000) + 1), max_df=10000, ngram_range=(1, 3))

        # vectorizer = TFVectorizing()
        vectors = vectorizer.fit_transform(text)
        return vectors

    @staticmethod
    def rreplace(s, old, new, occurrence):
        """
        replaces the 1 instance of old with new
         which instance is decided by occurrence and is counted backwards (1 is last occurrence)
        :param s: string that needs to be updated
        :param old: substring that needs to be changed
        :param new: replacement substring
        :param occurrence: which instance of old has to be swapped
        :return: updated string
        """
        li = s.rsplit(old, occurrence)
        return new.join(li)

    @staticmethod
    def clean_tweet(tweet):
        """
        adds features to the tweet for more similarity and easier clustering
        :param tweet: tweet that needs to be cleaned
        :return: cleaned string
        """
        reply_pattern = re.compile("^@([a-zA-Z0-9]*) (.*)")
        regexhandler = regex.RegexHandler()
        # add mark if tweets starts with a mention (@user)
        if reply_pattern.match(tweet.tweet["text"]) is not None:
            temp = "MarkReply " + tweet.tweet["text"]
        else:
            temp = tweet.tweet["text"]
        # language dependent

        if floodtags.core.statics.StaticData.locations:
            for location in floodtags.core.statics.StaticData.locations:
                if location in temp:
                    temp += " MarkLocation"

        try:
            stemmer = SnowballStemmer(floodtags.core.statics.StaticData.language.lower())
            # stem words
            temp = " ".join(
                [stemmer.stem(x) if x not in tweet.tweet[
                    "keywords"] and "MarkReply" not in x and "MarkLocation" not in x else x for x in temp.split()])
        except ValueError:
            print("language not found:", floodtags.core.statics.StaticData.language)
            # pass

        # store language
        temp = "Mark" + tweet.language + " " + temp

        # store keyword

        # replace each website with 'MarkWebsite' to create more similarity
        temp = regexhandler.replace(temp, 'MarkWebsite', regex.Expressions.website)
        # replace each photo url with 'MarkPhoto' to create more similarity
        for i in range(len(tweet.tweet["photos"])):
            temp = Vectorizer.rreplace(temp, "MarkWebsite", "MarkPhoto", 1)
        # replace each height with 'MarkHeight' to create more similarity
        temp = regexhandler.replace(temp, "MarkHeight", regex.Expressions.waterheight)
        # replace each time with 'MarkTime' to create more similarity
        temp = regexhandler.replace(temp, "MarkTime", regex.Expressions.time)
        # replace each date with 'MarkDate' to create more similarity
        temp = regexhandler.replace(temp, "MarkDate", regex.Expressions.date)
        # replace each number with 'MarkNumber' to create more similarity
        temp = regexhandler.replace(temp, "MarkNumber", regex.Expressions.number)
        temp = re.sub('\n', ' ', temp)
        results = re.findall("(^|[^@\w])@(\w{1,15})", temp)
        # add mark for each user name
        if results is not None:
            for i in range(len(results)):
                temp += " MarkUserName"
        results = re.findall("#(\S*)", temp)
        # add mark for each hashtag
        if results is not None:
            for i in range(len(results)):
                temp += " MarkHashTag"
        # add sender as feature
        temp = "Sender" + tweet.tweet["source"]["username"] + " " + temp
        # remove unnecessary characters and chance text to lower case
        return re.sub('[#\.,:]', '', temp)


class CosineSimilarity:
    """
    class for calculating the consine similarity of tweets
    """

    def __init__(self):
        """
        constructor for CosineSimilarity
        :return: None
        """
        self.vectorizer = Vectorizer()

    def calculate_similarity(self, tweets):
        """
        calculates the cosine similarity of tweets
        :param tweets: list of tweets
        :return: cosine similarity value
        """
        if (len(tweets) == 1):
            return 0
        vectors = self.vectorizer.vectorize_data(tweets, False)

        temp = cosine_similarity(vectors[0:-1], vectors)
        temp = [item for sublist in temp for item in sublist]
        sim = sum(temp) / len(temp)
        return sim


class Cluster:
    """
    class for storing tweets
    """

    def __init__(self):
        """
        constructor for the Cluster class
        :return: None
        """
        self.tweets = []
        self.lcs = "mixed"
        self.importance = 0

    def add_tweet(self, tweet):
        """
        add tweet to the cluster
        :param tweet: tweet that needs to be added
        :return: None
        """
        self.tweets.append(tweet)

    def get_tweets(self):
        """
        get list of tweets
        :return: list of tweets
        """
        return self.tweets

    def get_tweet(self, id):
        """
        get a specific tweet
        :param id: id of tweet within cluster
        :return: tweet
        """
        return self.tweets[id]

    def get_length(self):
        """
        gets amount of tweets in the cluster
        :return: amount of tweets
        """
        return len(self.tweets)

    def get_five_random(self):
        """
        gets five random tweets from the cluster, if there are less then five then all are returned
        :return: list of tweets
        """
        if self.get_length() > 5:
            random_selection = []

            from random import randrange

            for i in range(0, 5):
                while True:
                    rnd = randrange(0, self.get_length())
                    if self.get_tweet(rnd) not in random_selection:
                        random_selection.append(self.get_tweet(rnd))
                        break
            return random_selection
        else:
            return self.tweets

    def get_five_latest(self):
        """
        gets the five latest tweets from the cluster, if there are less then five then all are returned
        :return: list of tweets
        """
        selection = []
        sorted(self.tweets, key=lambda tweet: tweet.date, reverse=True)
        amount = 5
        if self.get_length() < 5:
            amount = self.get_length()
        for i in range(amount):
            selection.append(self.tweets[i])
        return selection

    def get_cosine_sim(self):
        """
        calculates the cosine similarity of the cluster
        :return: cosine similarity value
        """
        return CosineSimilarity().calculate_similarity(self.tweets)

    def set_importance(self, importance):
        """
        set importance value of the tweets in the cluster
        :param importance: importance value
        :return: None
        """
        self.importance = importance
        for tweet in self.tweets:
            tweet.update_importance(importance)


class AbstractClustering(metaclass=ABCMeta):
    """
    Abstract base class for cluster algorithms
    """

    def set_data(self, data):
        """
        sets data for the clustering algorithm
        :param data: tweets
        :return: None
        """
        self.tweets = data

    def start_algorithm(self):
        """
        start clustering the stored tweets
        :return: list of clusters containing tweets
        """
        pass

    def vectorize_data(self, idf=False):
        """
        turns tweets into vector representations
        :param idf: wether or not to use tf-idf, default False
        :return: sparse vector array
        """
        vectorizer = Vectorizer()
        return vectorizer.vectorize_data(self.tweets, idf)

    def cluster_tweet(self, clustering, data=None, amount=None):
        """
        groups clustered tweets into cluster objects
        :param clustering: array containing the cluster for each tweet
        :param data: clustered tweets. if left empty the entire collection of tweets will be used
        :param amount: amount of clusters if left empty the the cluster amount will be gotten from self.cluster_amount
        :return: array of cluster objects
        """
        if data is None:
            data = self.tweets
        if amount is None:
            amount = self.cluster_amount
        clusters = []
        for i in range(0, amount):
            temp = Cluster()
            for j in range(0, len(clustering)):
                if i == clustering[j]:
                    temp.add_tweet(data[j])
            clusters.append(temp)
        return clusters


class TweetKMeans(AbstractClustering):
    """
    Class for performing kmeans clustering on tweets
    """

    def __init__(self, cluster_amount):
        """
        constructor for TweetKMeans
        :param cluster_amount: amount of clusters to cluster tweets into
        :return: None
        """
        self.cluster_amount = cluster_amount
        self.tweets = []

    def start_algorithm(self):
        """
        start clustering the stored tweets
        :return: list of clusters containing tweets
        """
        vectors = self.vectorize_data()
        kmeans = KMeans(init='k-means++', n_clusters=self.cluster_amount, n_init=10)
        kmeans.fit(vectors)
        return self.cluster_tweet(kmeans.labels_)


class BisectingKmeansFun(AbstractClustering):
    """
    Class for applying Bisecting Kmeans on tweets using a function as limiter
    """

    def __init__(self, cores):
        """
        constructor for BisectingKmeansFun
        :param cores: amount of processes the clustering is allowed to use
        :return: None
        """
        self.kmeans = TweetKMeans(2)
        self.tweets = []
        self.guard = 0.5
        self.cores = cores
        self.function = CosineSimilarity().calculate_similarity

    def set_function(self, function, guard):
        """
        changes the function and limit value. by default it is set to cosine similarity with a guard of 0.5
        :param function: function that is used to decide whether clustering is done
        :param guard: value that decides whether clustering is done
        :return: None
        """
        self.function = function
        self.guard = guard

    def start_algorithm(self):
        """
        starts clustering the tweets
        :return: List of clusters containing tweets
        """
        self.kmeans.set_data(self.tweets)
        clusters = self.kmeans.start_algorithm()
        min_size = len(self.tweets) * 0.005
        if min_size < 50:
            min_size = 50
        max_size = len(self.tweets) * 0.20

        amount = 0

        while amount < len(clusters):
            amount = len(clusters)
            pool = mp.Pool(self.cores)
            new_clusters = pool.starmap(recluster,
                                        zip(clusters, repeat(min_size), repeat(self.guard), repeat(self.function)))
            pool.close()
            pool.join()
            clusters = new_clusters
            temp = []
            for cluster in clusters:
                if isinstance(cluster, Cluster):
                    temp.append(cluster)
                else:
                    temp += cluster
            clusters = temp
        return clusters
