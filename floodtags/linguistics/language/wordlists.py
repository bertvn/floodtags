"""
module containing WordList classes for filtering on/out certain words
"""
import csv
from abc import ABCMeta
import os


class AbstractWordList(metaclass=ABCMeta):
    """
    AbstractWordList is the abstract base class for all wordlist classes
    """
    def __init__(self, file):
        """
        constructor for AbstractWordList
        :param file: name of the file that is used as the wordlist
        :return: None
        """
        self.word_list = self._readfile(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../../", file))

    def _readfile(self, file) -> list:
        """
        reads the file
        :param file: name of the file
        :return: list of words
        """
        pass

    def match(self, sentence) -> bool:
        """
        tests if sentence has a word contained in the wordlist
        :param sentence: string that needs to be checked
        :return: boolean containing whether or not a match has been found
        """
        pass

    def append(self, string):
        """
        add word to the wordlist
        :param string: word that needs to be added
        :return: None
        """
        self.word_list.append(string)


class WordList(AbstractWordList):
    """
    wordlist that matches if word exists
    """
    def __init__(self, file):
        """
        constructor for WordList
        :param file: name of the file that is used as the wordlist
        :return: None
        """
        super().__init__(file)

    def _readfile(self, file) -> list:
        """
        reads the file
        :param file: name of the file
        :return: list of words
        """
        with open(file, encoding="utf8") as data:
            word_list = data.read().split("\n")
        return word_list

    def match(self, sentence) -> bool:
        """
        tests if sentence contains a word in the wordlist
        :param sentence: string that needs to be checked
        :return: Boolean containing whether or not a match has been found
        """
        for word in self.word_list:
            if word.lower() in sentence.lower():
                return True
        return False


class PartialWordList(AbstractWordList):
    """
    Wordlist that matches full, partial and not.
    full meaning the string has to be the same as a full entry in the wordlist
    partial means the string has to contain a partial entry in the wordlist
    not means the must not contain a not entry in the wordlist
    """
    def __init__(self, file):
        """
        constructor for PartialWordList
        :param file: name of the file that is used as the wordlist
        :return: None
        """
        super().__init__(file)

    def _readfile(self, file) -> list:
        """
        reads the file
        :param file: name of the file
        :return: list of words
        """
        with open(file, encoding="utf8") as data:
            word_list = list(csv.reader(data))
        return word_list

    def match(self, sentence) -> bool:
        """
        test if sentence matches a full or partial word, but not a not word
        :param sentence: string that needs to be matched
        :return: Boolean containing whether or not a match has been found
        """
        if (any(word[0] in sentence.lower() for word in self.word_list if word[1] == "partial") or any(
                    word[0].lower() == sentence.lower() for word in self.word_list if word[1] == "full")) and not any(
                    word[0] in sentence.lower() for word in self.word_list if word[1] == "not"):
            return True
        else:
            return False
