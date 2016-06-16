import uuid
from abc import ABCMeta


class AbstractNode(metaclass=ABCMeta):
    def add_word(self, word, origin=None):
        if not origin:
            origin = uuid.uuid1()
        if origin not in self.words:
            self.words.append(origin)
        if len(word) == 0:
            return
        index = self._branch_exists(word[0])
        if index == -1:
            self.branches.append(Branch(word[0]))
            index = len(self.branches) - 1
        self.branches[index].add_word(word[1:], origin)

    def _branch_exists(self, value):
        for i in range(len(self.branches)):
            if self.branches[i].get_value() == value:
                return i
        return -1


class Tree(AbstractNode):
    def __init__(self):
        self.words = []
        self.branches = []

    def add_word(self, word, origin=None):
        if not origin:
            origin = uuid.uuid1()
        if len(word) == 0:
            return
        super(Tree, self).add_word(word, origin)
        self.add_word(word[1:], origin)

    def get_longest_common_substring(self):
        list = [x.get_longest_common_substring(self.words) for x in self.branches]
        if not list:
            return ""
        return max(list, key=len)

    def get_longest_most_common_substring(self):
        length = len(self.words)
        substrings = []
        while length >= (len(self.words) // 2) and length > 1:
            list = [x.get_longest_most_common_substring(length) for x in self.branches]
            if not list:
                substrings.append("")
            else:
                substrings.append((max(list, key=len), length))
            length -= 1
        if substrings:
            index = -1
            score = -1
            for i in range(len(substrings)):
                if len(substrings[i][0]) * (substrings[i][1] * 2) > score:
                    index = i
                    score = len(substrings[i][0]) * (substrings[i][1] * 2)
            return substrings[index][0]
        return ""


class Branch(AbstractNode):
    def __init__(self, value):
        self.words = []
        self.branches = []
        self.end_nodes = []
        self.value = value

    def get_value(self):
        return self.value

    def get_longest_common_substring(self, words):
        if set(words) == set(self.words):
            list = [x.get_longest_common_substring(words) for x in self.branches]
            if not list:
                return self.value
            return self.value + max(list, key=len)
        else:
            return ""

    def get_longest_most_common_substring(self, length):
        if len(self.words) >= length:
            list = [x.get_longest_most_common_substring(length) for x in self.branches]
            if not list:
                return self.value
            return self.value + max(list, key=len)
        else:
            return ""
