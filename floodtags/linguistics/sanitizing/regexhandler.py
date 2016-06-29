"""
Module containing the regexhandler and enum class of expressions that the regexhandler can handle
"""
import re
from enum import Enum


class Expressions(Enum):
    """
    Enum class containing all possible Expressions for the RegexHandler
    """
    time = "time"
    date = "date"
    website = "website"
    users = "users"
    number = "number"
    hashtag = "hashtag"
    footheight = "footheight"
    meterheight = "meterheight"
    cmheight = "cmheight"
    waterheight = "waterheight"
    reply = "reply"
    falsealarm = "false_alarm"
    file = "file"


class RegexHandler():
    """
    class for handling regular expressions
    """
    def __init__(self):
        """
        constructor for RegexHandler
        :return: None
        """
        self.time = re.compile(
            "((?<=\W)|(?<=^))([0-1]?[0-9]|2[0-3])((:[0-5][0-9])(:[0-5][0-9])?|(( )?[AaPp][Mm])|(:[0-5][0-9])(:[0-5][0-9])?( )?([AaPp][Mm])| o'clock)((?=$)|(?=\W))")
        self.date = re.compile("(([0-9]){2,4})[/-](([0-9]){2})[/-](([0-9]){2,4})")
        self.website = re.compile('https://t\.co/(\S){0,12}')
        self.users = re.compile("(^|[^@\w])@(\w{1,15})")
        self.number = re.compile('((?<=\W)|(?<=^))(\d+(.\d+)?)((?=$)|(?=\W))')
        self.hashtag = re.compile("#(\S*)")
        self.footheight = re.compile("\s((\d{1,2})(\.(\d{1,2}))?)(\W?)(ft[\.|]\W|feet|foot)")
        self.meterheight = re.compile("\s((\d{1,2})(\.(\d{1,2}))?)(\W?)(meter[s|]\W|m\W)")
        self.cmheight = re.compile("\s((\d{1,2})(\.(\d{1,2}))?)(\W?)(centimeter[s|]\W|cm\W)")
        self.waterheight = re.compile(
            "\s((\d{1,2})(\.(\d{1,2}))?)(\W?)(ft|feet|foot|meter[s|]\W|m\W|centimeter[s|]\W|cm\W)")
        self.reply = re.compile("^@([a-zA-Z0-9]*) (.*)")
        self.false_alarm = re.compile("^0( Severe)? Flood (Warning|Alert)")
        self.file = re.compile(".*\.\w{3,4}")

    def replace(self, input, replace, pattern: Expressions) -> str:
        """
        replaces input with replace according to the pattern
        :param input: original string
        :param replace: substring that needs to be used as replacement
        :param pattern: name of regex pattern for replacing
        :return: the changed input string
        """
        ptrn = getattr(self, pattern.value)
        return ptrn.sub(replace, input)

    def exists(self, input, pattern: Expressions) -> bool:
        """
        checks if input matches the pattern
        :param input: string that needs to be matched
        :param pattern: name of regex pattern for matching
        :return:
        """
        ptrn = getattr(self, pattern.value)
        return bool(ptrn.search(input))

    def count(self, input, pattern: Expressions) -> int:
        """
        count the amount of times pattern matches the input
        :param input: string that needs to be matched
        :param pattern: name of regex pattern for counting
        :return:
        """
        ptrn = getattr(self, pattern.value)
        return len(ptrn.findall(input))

    def getMatch(self, input, pattern: Expressions, group=1):
        """

        :param input: string that needs to be checked for match
        :param pattern: name of regex paatern for matching
        :param group: number of the match that you want, default is 1
        :return: The selected match if available
        """
        ptrn = getattr(self, pattern.value)
        return ptrn.search(input).group(group)


