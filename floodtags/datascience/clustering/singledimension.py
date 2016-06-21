"""
module for clustering 1 dimensional data via Jenks Natural Breaks Optimization
"""

from enum import Enum
from random import randrange


class SubsetType(Enum):
    """
    enum class containing the options for the JenksNaturalBreak class
    """
    random = 0
    average = 1


class JenksNaturalBreak(object):
    """
    Class for calculating the Jenks Natural Breaks Optimization
    """
    def __init__(self):
        """
        constructor for JenksNaturalBreak
        :return: None
        """
        self.data = []
        self.classes = 3

    def analyze(self, data, classes=3, subset=None, type: SubsetType = SubsetType.average) -> list:
        """
        Calculate the breaks so the data can be grouped into classes
        :param data: data that needs to be analyzed
        :param classes: amount of classes
        :param subset: size of the subset used, optional only use for large datasets
        :param type: kind of subset used
        :return: list of breakpoints
        """
        data.sort()
        self.data = data
        if subset and subset < len(data):
            self.subset = subset
            self._get_subset(type)
        self.classes = classes
        matrices = self._get_matrices()
        return self._breaks(matrices[0])

    def _get_subset(self, type):
        """
        gathers the subset that is to be used
        :param type: type of subset to be created
        :return: None
        """
        if type == SubsetType.average:
            self.data = self._get_average_subset()
            return
        if type == SubsetType.random:
            self.data = self._get_random_subset()
            return
        self.data = self._get_random_subset()

    def _get_random_subset(self) -> list:
        """
        generates a random subset
        :return: list of random elements from the complete dataset
        """
        ids = [0, len(self.data) - 1]
        for i in range(self.subset - 2):
            while True:
                rnd = randrange(0, len(self.data))
                if rnd not in ids:
                    ids.append(rnd)
                    break
        data_subset = []
        for i in ids:
            data_subset.append(self.data[i])
        data_subset.sort()
        data = data_subset
        return data

    def _get_average_subset(self) -> list:
        """
        combines elements to create a subset of averages
        :return: list of the averages of the elements
        """
        data = []
        data.append(self.data[0])
        size = (len(self.data) - 2) // (5000 - 2)
        for i in range(1, len(self.data), size):
            temp = 0
            max_iter = len(self.data) - i - 1
            if max_iter > size:
                max_iter = size
            if max_iter == 0:
                break
            for j in range(0, max_iter):
                temp += self.data[i + j]
            data.append(temp / max_iter)
        data.append(self.data[len(self.data) - 1])
        return data

    def _get_matrices(self):
        """
        calculates the breaks
        :return: (lower limits of each class, variance combinations)
        """
        # optimal lower class limits
        lower_class_limits = [[1 for x in range(self.classes + 1)] for x in range(len(self.data) + 1)]
        # optimal variance combinations for all classes
        variance_combinations = [[0 for x in range(self.classes + 1)] for x in range(len(self.data) + 1)]
        variance = 0

        for i in range(1, self.classes + 1):
            lower_class_limits[1][i] = 1
            variance_combinations[1][i] = 0
            for j in range(2, len(self.data) + 1):
                variance_combinations[j][i] = float('inf')

        for l in range(2, len(self.data) + 1):
            sum = 0
            sum_squares = 0
            w = 0
            i4 = 0
            for m in range(1, l + 1):
                lower_class_limit = l - m + 1
                val = self.data[lower_class_limit - 1]
                w += 1
                sum += val
                sum_squares += (val * val)
                variance = (sum_squares - ((sum * sum) / w))
                i4 = lower_class_limit - 1
                if i4 is not 0:
                    for j in range(1, self.classes + 1):
                        if variance_combinations[l][j] >= (variance + variance_combinations[i4][j - 1]):
                            lower_class_limits[l][j] = lower_class_limit
                            variance_combinations[l][j] = variance + variance_combinations[i4][j - 1]
            lower_class_limits[l][1] = 1
            variance_combinations[l][1] = variance

        return (lower_class_limits, variance_combinations)

    def _breaks(self, lower_class_limits):
        """
        generates a list containing each border value
        :param lower_class_limits: lower limits of the classes
        :return: list of break borders
        """
        k = len(self.data)
        count_num = self.classes
        kclass = [0] * (count_num + 1)

        kclass[count_num] = self.data[len(self.data) - 1]
        kclass[0] = self.data[0]

        while count_num > 1:
            temp = lower_class_limits[k][count_num]
            kclass[int(count_num - 1)] = self.data[int(temp - 2)]
            k = temp - 1
            count_num -= 1

        return kclass
