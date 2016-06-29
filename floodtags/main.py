"""Starter script for the FloodFilter algorithm"""
import argparse
import datetime
import logging
import os
from multiprocessing.pool import ThreadPool

import floodtags.core.dependencyinjection as di
import floodtags.datascience.newspipeline
from floodtags.core.statics import StaticData
from floodtags.linguistics.sanitizing.regexhandler import Expressions


def main(input, location, type, proc, loop, timeframe):
    """
    Main part of the program
    :param input: input source can be a file or a stream or demo
    :param location: where to put the output file
    :param type: type of output
    :param proc: amount of processes used
    :param loop: amount of times the algorithm is repeated
    :return: None
    """
    if loop == "infinite":
        loop = float("inf")

    container = di.Container()
    regex = container.create("regex")
    file = False
    if regex.exists(input,Expressions.file):
        file = True
    logging.disable(logging.WARNING)

    container.set_input(input)
    container.set_location(location)
    container.set_type(type)
    container.set_proc(proc)
    handler = container.create("handler")
    totaltweets = []
    # while there are not enough tweets
    while len(totaltweets) < 5000:
        # get tweets
        totaltweets += handler.get_tweets()
    # analyse tweets
    analysis = container.create("analysis")
    analysis.set_data(totaltweets)
    keyword, language = analysis.start_analysis()
    StaticData.set_language(language)
    StaticData.set_keyword(keyword)

    # set language for NER if not english
    content = []
    for tweet in totaltweets:
        content.append(tweet.tweet["text"])

    # TODO use polyglot if language is not english
    ner = container.create("NER")
    StaticData.add_locations(ner.tag('. '.join(content)))

    lang = False
    # apply blacklist
    if os.path.isdir(os.path.dirname(os.path.abspath(__file__)) + "/linguistics/language/" + language.lower()):
        lang = True

    userblacklist = container.create("bannedusers")
    tweets = [tweet for tweet in totaltweets if not userblacklist.match(tweet.tweet["source"]["username"])]
    temp = [tweet for tweet in tweets if not regex.exists(tweet.tweet["text"], Expressions.falsealarm)]
    tweets = temp
    if lang:
        container.set_language(language.lower())
        blacklist = container.create("blacklist")
        tweets = [tweet for tweet in tweets if not blacklist.match(tweet.tweet["text"])]
        newslist = container.create("newsaccounts")
        warnlist = container.create("warnlist")

    index = 0

    while True:
        if not file:
            maxdate = datetime.datetime.strptime("1900-01-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
            for tweet in tweets:
                if maxdate < tweet.date:
                    maxdate = tweet.date

            timedselection = [x for x in tweets if x.date > (maxdate - datetime.timedelta(minutes=int(timeframe)))]
            if lang:
                pool = ThreadPool(processes=1)
                async_result = pool.apply_async(floodtags.datascience.newspipeline.frequent_tweeter_analysis,
                                            (tweets, newslist, warnlist))
        else:
            timedselection = tweets
        # cluster + spamfilter -- if language exists otherwise skip spamfilter


        clustering = container.create("clustering")
        clustering.set_data(timedselection)

        clusters = clustering.start_algorithm()

        if not file and lang:
            newsaccounts, warnaccounts, spam = async_result.get()
            for account in spam:
                userblacklist.append(account)
        else:
            newsaccounts = []

        # order
        filtering = container.create("filtering")
        filtering.set_data(clusters)
        order = filtering.start_filtering()

        # write results
        writer = container.create("outputformatter")
        writer.set_original_tweets(totaltweets)
        writer.set_tweets(tweets)
        writer.set_clusters(clusters, order)
        writer.set_newsaccounts(newsaccounts)
        writer.set_locations(StaticData.locations)
        writer.output_result()

        # if event is over -- what condition? shutdown file from webapp?
        # break
        if int(index) >= int(loop):
            return
        else:
            index += 1

        # get tweets
        totaltweets += handler.get_tweets()
        # apply blacklist
        tweets = [tweet for tweet in totaltweets if not userblacklist.match(tweet.tweet["source"]["username"])]
        if lang:
            tweets = [tweet for tweet in tweets if not blacklist.match(tweet.tweet["text"])]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", "--input", dest="input", default="demo",
                        help="datasource; " +
                             "demo for tests; " +
                             "stream name for running on api; " +
                             "file location for running on file; " +
                             "(default: demo)")
    parser.add_argument("-out", "--output", dest="loc", default="/", help="location of output (default: /)")
    parser.add_argument("-tp", "--outputtype", dest="type", default="webapp",
                        help="type of output; " +
                             "webapp for use in dashboard; " +
                             # "json for original json + enrichment; " +
                             "enrichment for id + enrichment; " +
                             "test for the top 20 clusters and their 5 latest tweets; " +
                             "(default:webapp)")
    parser.add_argument("-p", "--processes", dest="proc", default=4,
                        help="amount of processes used in clustering (default: 4)")
    parser.add_argument("-l", "--loop", dest="loop", default=0,
                        help="amount of times the algorithm loops; integer value or \"infinite\" (default:0)")
    parser.add_argument("-tf", "-timeframe", dest="timeframe", default=360,
                        help="time frame, used for clustering tweets, in minutes")

    args = parser.parse_args()
    main(args.input, args.loc, args.type, args.proc, args.loop, args.timeframe)
