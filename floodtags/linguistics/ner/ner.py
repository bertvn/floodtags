"""
module containing handlers for named entity recognition implementations
"""
import os
import sys

from nltk import StanfordNERTagger
from polyglot.text import Text
from multiprocessing.dummy import Pool as ThreadPool
import polyglot.detect
import re


class NERHandler(object):
    """
    handler class for the Stanford NER
    """

    def __init__(self):
        """
        constructor for the NERHandler class
        :return:
        """
        if sys.platform.startswith('win'):
            os.environ['CLASSPATH'] = os.path.dirname(__file__) + "\\stanford-ner-2015-12-09\\"
            os.environ['STANFORD_MODELS'] = os.path.dirname(__file__) + "\\stanford-ner-2015-12-09\\classifiers\\"
            os.environ['JAVAHOME'] = "C:\\Program Files\\Java\\jre1.8.0_91"
        else:
            os.environ['CLASSPATH'] = os.path.dirname(__file__) + "/stanford-ner-2015-12-09/"
            os.environ['STANFORD_MODELS'] = os.path.dirname(__file__) + "/stanford-ner-2015-12-09/classifiers/"

        self.st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')

    def tag(self, text):
        """
        search for Named locations within text
        :param text: String list containing text that needs to be searched
        :return: list of locations
        """
        text = '. '.join(text)
        tags = self.st.tag(text.split())
        # if there is tag 'LOCATION' add to locations, note locations can be multiple tags long
        i = 0
        locations = []
        while i < len(tags):
            location = []
            if tags[i][1] == "LOCATION":
                location.append(tags[i][0])
                i += 1
                while tags[i][1] == "LOCATION":
                    location.append(tags[i][0])
                    i += 1
                locations.append(' '.join(location))
            else:
                i += 1

        locations = list(set(locations))
        return locations


# TODO: implement polyglot NER if language is not english

def poly_ner(text):
    processed = Text(text)
    locations = []
    try:
        for entity in processed.entities:
            if entity.tag == "I-LOC":
                loc = []
                for part in entity:
                    loc.append(part)
                locations.append((" ".join(loc)))
        return locations
    except Exception as e:
        print(e)
        print("language:", polyglot.detect.Detector(re.sub('#', '', text)).language.name)
        print("can't analyse tweet")


class PolyHandler(object):

    def tag(self, text):
        pool = ThreadPool(4)
        locations = pool.map(poly_ner, text)
        locations[:] = [item for sublist in locations for item in sublist]
        locations = list(set(locations))
        return locations
