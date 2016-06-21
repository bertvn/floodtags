import unittest

from floodtags.linguistics.sanitizing.regexhandler import RegexHandler, Expressions


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_count(self):
        han = RegexHandler()
        self.assertEqual(7, han.count("#how #many #bloody #hashtags #do #you #want?", Expressions.hashtag))

    def test_exists_1(self):
        han = RegexHandler()
        self.assertTrue(han.exists("2016-42-2016", Expressions.date))

    def test_exists_2(self):
        han = RegexHandler()
        self.assertTrue(han.exists("8 o'clock", Expressions.time))

    def test_exists_3(self):
        han = RegexHandler()
        self.assertTrue(han.exists("23:59 ", Expressions.time))

    def test_replace(self):
        han = RegexHandler()
        self.assertEqual("how late is it? it is now", han.replace("how late is it? it is 9am", "now", Expressions.time))


if __name__ == '__main__':
    unittest.main()
