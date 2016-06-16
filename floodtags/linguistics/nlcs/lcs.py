import floodtags.linguistics.nlcs.tree.tree

class LongestCommonString():

    def lcs(self, strings, string = None):
        if string:
            data = []
            data.append(strings)
            data.append(string)
            strings = data
        tree = floodtags.linguistics.nlcs.tree.tree.Tree()
        for str in strings:
            tree.add_word(str.lower())
        return tree.get_longest_common_substring()

    def lmcs(self, strings, string = None):
        if string:
            data = []
            data.append(strings)
            data.append(string)
            strings = data
        tree = floodtags.linguistics.nlcs.tree.tree.Tree()
        for str in strings:
            tree.add_word(str.lower())
        return tree.get_longest_most_common_substring()