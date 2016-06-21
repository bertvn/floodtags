"""
module containing algorithms for analyzing clusters
"""
import floodtags.linguistics.sanitizing.regexhandler as regex
import floodtags.linguistics.nlcs.lcs


class LongestCommonSubstring():
    """
    class for calculating the longest (most) common substring
    """
    def __init__(self):
        """
        contstructor for LongestCommonSubstring
        :return: Nonr
        """
        return

    def lcs_cluster(self, cluster):
        """
        calculate the longest most common substring of a cluster of tweets
        :param cluster: cluster who' tweets need to be analysed
        :return: longest most common substring
        """
        text = []
        regexhandler = regex.RegexHandler()
        for tweet in cluster.get_tweets():
            text.append(regexhandler.replace(tweet.tweet["text"],"",regex.Expressions.website))
        lcs = floodtags.linguistics.nlcs.lcs.LongestCommonString()
        return lcs.lmcs(text)

    def lcs_cluster_usernames(self, cluster):
        """
        calculates the longest most common subtring for usernames in a cluster
        :param cluster: cluster who's users need to be analysed
        :return: longest most common substring
        """
        usernames = []
        for tweet in cluster.get_tweets():
            usernames.append(tweet.tweet["source"]["username"])
        lcs = floodtags.linguistics.nlcs.lcs.LongestCommonString()
        return lcs.lmcs(usernames)

    def lcs_array(self, array):
        """
        calculates longest common substring for an list of strings
        :param array: list of strings
        :return: longest common substring
        """
        base = self.lcs(array[0], array[1])
        i = 2
        while i < len(array):
            base = self.lcs(base, array[i])
            i += 1
            if len(base) == 0:
                break
        return base

    def lcs(self, str1, str2):
        """
        calculates the longest common substring for 2 strings
        :param str1: first string to be analysed
        :param str2: second string that needs to be analysed
        :return: longest common substring between str1 and str2
        """
        result = []
        if not str1 and not str2 and not (len(str1) > 0) and not (len(str2) > 0):
            return ""
        str1 = str1.lower()
        str2 = str2.lower()
        num = [[0] * len(str2) for x in range(len(str1))]
        maxlen = 0
        last_subs_begin = 0
        for i in range(len(str1)):
            for j in range(len(str2)):
                if str1[i] == str2[j]:
                    if i == 0 or j == 0:
                        num[i][j] = 1
                    else:
                        num[i][j] = 1 + num[i - 1][j - 1]
                    if num[i][j] > maxlen:
                        maxlen = num[i][j]
                        this_subs_begin = i - num[i][j] + 1
                        if last_subs_begin == this_subs_begin:
                            result.append(str1[i])
                        else:
                            last_subs_begin = this_subs_begin
                            result = []
                            result.append(str1[last_subs_begin:i + 1])
        return ''.join(result)
