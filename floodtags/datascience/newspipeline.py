"""
Module used to find and categorize frequent tweeters into newsaccounts, warningaccounts and spamaccounts
"""
import floodtags.datascience.clustering.singledimension as jenks

import floodtags.linguistics.sanitizing.regexhandler as rh


def frequent_tweeter_analysis(tweets, newslist, warninglist):
    """
    finds frequent tweeters and seperates them into newsaccounts, warningaccounts and spamaccounts
    :param tweets: tweets that need to be analyzed
    :param newslist: Whitelist object containing the whitelist for news account names
    :param warninglist: Whitelist object containing the whitelist for warning words
    :return: tuple containing the usernames of (newsaccounts, warningaccounts, spamacounts)
    """
    jenksnb = jenks.JenksNaturalBreak()

    total = {}
    counter = 0

    def add_user(username):
        if username not in total:
            total[username] = 0
        total[username] += 1

    for tweet in tweets:
        add_user(tweet.tweet["source"]["username"])
        counter += 1

    tweetings = []
    for key in total.keys():
        tweetings.append(total[key])

    classes = 5
    users = [[] for i in range(classes + 1)]

    # create classes
    breaks = jenksnb.analyze(tweetings, classes, 5000, jenks.SubsetType.average)

    # group the users into the classes
    for i in range(len(breaks) - 1):
        if i == 0:
            for key in total.keys():
                if total[key] == breaks[i]:
                    users[i].append(key)
                    break
        for key in total.keys():
            if total[key] > breaks[i] and total[key] <= breaks[i + 1]:
                users[i].append(key)

    poi = [x for i in range(2, classes) for x in users[i]]

    newsaccount = []
    other = []
    for tweeter in poi:
        if newslist.match(tweeter.lower()):
            newsaccount.append(tweeter)
        else:
            other.append(tweeter)

    regexhandler = rh.RegexHandler()

    warningaccount = []
    for tweet in tweets:
        if tweet.tweet["source"]["username"] in other:
            if "flood" in tweet.tweet["text"].lower():
                if warninglist.match(tweet.tweet["text"]):
                    warningaccount.append(tweet.tweet["source"]["username"])
                    other.remove(tweet.tweet["source"]["username"])
                    continue
                if regexhandler.exists(tweet.tweet["text"], rh.Expressions.time):
                    warningaccount.append(tweet.tweet["source"]["username"])
                    other.remove(tweet.tweet["source"]["username"])
                    continue
    spam = other

    return newsaccount, warningaccount, spam
