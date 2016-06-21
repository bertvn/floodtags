import inspect
import os

import floodtags.api.handler
import floodtags.core.formatOutput
import floodtags.datascience.analysis
import floodtags.datascience.clustering.clustering
import floodtags.datascience.filtering.filtering
import floodtags.linguistics.language.wordlists
import floodtags.linguistics.sanitizing.regexhandler
import floodtags.linguistics.ner.ner


class Container:
    def __init__(self):
        self._build_container()

    def create(self, classname):
        """
        creates class and it's dependencies according to self.container
        :param classname: name class is registered as in the container
        :return: object that matches classname
        """
        for component_name, component_class, component_args in self.container:
            if component_name == classname:
                if component_args is None:
                    if inspect.isclass(component_class):
                        return component_class()
                    else:
                        return component_class
                else:
                    return component_class(*map(self.create, component_args))
        return None

    def set_language(self, language):
        """
        switches which folder is used for language files
        :param language: language that is to be used
        :return: None
        """
        self.container = [(a, b, c) for a, b, c in self.container if not a.endswith("file")]
        self.container.append(("blacklistfile", "linguistics/language/" + language + "/blacklist.txt", None))
        self.container.append(("newsaccountsfile", "linguistics/language/" + language + "/newsaccounts.csv", None))
        self.container.append(("warnlistfile", "linguistics/language/" + language + "/warningsystem.txt", None))

    def set_input(self, input):
        """
        set which datastream to use
        :param input: String containing either the name of a datastream, "demo" or a file on disk
        :return: None
        """
        if input == "demo":
            self.container.append(("api", floodtags.api.handler.FakeAPI, ("region",)))
            self.container.append(("region", "demo", None))
        elif os.path.isfile(input):
            self.container.append(("api", floodtags.api.handler.FakeAPI, ("region",)))
            self.container.append(("region", input, None))
        else:
            self.container.append(("api", floodtags.api.handler.API, ("region",)))
            self.container.append(("region", input, None))

    def set_location(self, location):
        self.container.append(("outputlocation", location, None))

    def set_type(self, type):
        if type == "webapp":
            self.container.append(("outputformatter", floodtags.core.formatOutput.FormatResult, ("outputlocation",)))
        if type == "enrichment":
            self.container.append(("outputformatter", floodtags.core.formatOutput.RatingFormat, ("outputlocation",)))
        if type == "test":
            self.container.append(("outputformatter", floodtags.core.formatOutput.TestFormat, ("outputlocation",)))

    def set_proc(self, proc):
        self.container.append(("cores", proc, None))

    def _build_container(self):
        """
        Builds dependency injection container
        each line is a class and has the following structure:
        (name used to create object, class, dependencies)
        dependencies are a tuple or None
        :return: None
        """
        self.container = [
            ("handler", floodtags.api.handler.APIHandler, ("api",)),
            ("analysis", floodtags.datascience.analysis.AnalyzeDataSet, None),
            ("blacklist", floodtags.linguistics.language.wordlists.WordList, ("blacklistfile",)),
            ("blacklistfile", "linguistics/language/english/blacklist.txt", None),
            ("newsaccounts", floodtags.linguistics.language.wordlists.PartialWordList, ("newsaccountsfile",)),
            ("newsaccountsfile", "linguistics/language/english/newsaccounts.csv", None),
            ("warnlist", floodtags.linguistics.language.wordlists.WordList, ("warnlistfile",)),
            ("warnlistfile", "linguistics/language/english/warningsystem.txt", None),
            ("clustering", floodtags.datascience.clustering.clustering.BisectingKmeansFun, ("cores",)),
            ("cores", 4, None),
            ("filtering", floodtags.datascience.filtering.filtering.Filter, None),
            ("bannedusers", floodtags.linguistics.language.wordlists.WordList, ("banneduserfile",)),
            ("banneduserfile", "linguistics/language/bannedusers.txt", None),
            ("regex", floodtags.linguistics.sanitizing.regexhandler.RegexHandler, None),
            ("NER", floodtags.linguistics.ner.ner.NERHandler,None)
        ]
