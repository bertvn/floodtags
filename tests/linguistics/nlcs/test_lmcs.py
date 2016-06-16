import unittest

import floodtags.linguistics.nlcs.lcs


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_two_strings1(self):
        lcs_obj = floodtags.linguistics.nlcs.lcs.LongestCommonString()
        self.assertEqual(lcs_obj.lmcs("how do you write tests?", "Writing is an essential part of coding"), "writ")

    def test_two_strings2(self):
        lcs_obj = floodtags.linguistics.nlcs.lcs.LongestCommonString()
        self.assertEqual(lcs_obj.lmcs("piilosana", "namiloma"), "ilo")

    def test_n_strings1(self):
        lcs_obj = floodtags.linguistics.nlcs.lcs.LongestCommonString()
        list = ["Love living in the north west - flood warning everywhere, we've got a leak in our roof at the moment",
                "There are multiple reasons for the recent flooding in the north of England and elsewhere. This problem is a world... https://t.co/wl5Ie6yI9r",
                'While giant corporations swim in a sea of tax avoided wealth the North drowns in  the raging rivers of broken Tory promises #floods',
                "https://t.co/cm6qJba5ot #yorkfloods RT URY1350: If a city floods in the north but a southerner isn't there to see… https://t.co/dmiJKclN2j",
                "Know people affected by flooding in Rochdale and Bury. Can't believe what's been happening across the North West.Never seen anything like it",
                '#ukfloods Many devastating scenes in the North in particular of what the damage the winter floods have done. Relief & resilience key.',
                'Go on my Tory chums. Please defend  300 + #floods  defence cuts up in the North of England. Resign @David_Cameron youre not fit for office',
                'Floods in the north = higher insurance prices for the rest of us.',
                'Pictures of the flooding in the North Nest and North Wales are truly horrific. Please stay safe my colleagues from @RBNNorth',
                'The North is suffering the worst flooding in 15 years and where is Jeremy Corbyn? On a beach in the Med plotting against Blairites.',
                "Although, he must have been on crack or something, because floods only happen in the north, don't they?",
                "@EssenceInsanity we've had floods in the north... But even then it hasn't been cold at all.",
                'The north of the UK is in trouble with big storms and flood. I hope they can keep safe somehow... — feeling worried',
                '#jeremycorbyn was on holiday abroad whilst lots of Labour councils in the north were flooded....wonder if the dumb lefties and bbc will say?',
                'There is so much of our taxes spent in the south to upgrade flood defences in the North is a fraction off the cost of Crossrail',
                "England suffering a natural disaster with disastrous flooding in the north-west. Except of course it's the man-made result of #ClimateChange",
                'I was born in the North.\nGrew up in the (constant bloody) rain.\nNever flooded.']
        self.assertEqual(lcs_obj.lmcs(list), " in the north")

    def test_n_strings2(self):
        lcs_obj = floodtags.linguistics.nlcs.lcs.LongestCommonString()
        list = ["this part is similar followed by random stuff deokorenufe short sub",
                "this part is similar followed by random stuff riojeowjnew short sub",
                "this part is similar followed by random stuff fwaeamdjkna short sub",
                "while the last is almost completely different short sub"]
        self.assertEqual(lcs_obj.lmcs(list), "this part is similar followed by random stuff ")

    def test_no_substring1(self):
        lcs_obj = floodtags.linguistics.nlcs.lcs.LongestCommonString()
        list = ["bejdeodeobej", "lpokollpokpl", "qwuvmwqqw"]
        self.assertEqual(lcs_obj.lmcs(list), "o")

    def test_no_substring2(self):
        lcs_obj = floodtags.linguistics.nlcs.lcs.LongestCommonString()
        list = ["this string is very similar to the next",
                "this string is very similar to the previous",
                "xcz"]
        self.assertEqual(lcs_obj.lmcs(list), "this string is very similar to the ")

    def test_same_string(self):
        lcs_obj = floodtags.linguistics.nlcs.lcs.LongestCommonString()
        list = ["mirror's edge", "mirror's edge", "mirror's edge", "mirror's edge", "mirror's edge", "mirror's edge"]
        self.assertEqual(lcs_obj.lmcs(list), "mirror's edge")


if __name__ == '__main__':
    unittest.main()
