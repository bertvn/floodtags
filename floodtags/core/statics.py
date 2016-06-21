"""
Contains storage classes for data that is used throughout the program
"""


class StaticData(object):
    """
    used to store data
    """
    language = "english"
    keyword = "flood"
    locations = []

    @staticmethod
    def set_language(lang):
        """
        store a language
        :param lang: language
        :return: None
        """
        StaticData.language = lang

    @staticmethod
    def set_keyword(key):
        """
        store a keyword
        :param key: keyword
        :return: None
        """
        StaticData.keyword = key

    @staticmethod
    def add_locations(locations):
        """
        adds locations to list of locations
        :param locations: list of locations
        :return: None
        """
        StaticData.locations += locations