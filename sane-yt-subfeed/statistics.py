from math import fsum
from timer import Timer


class Statistics:
    timers = []

    def __init__(self, name, timer=False):
        """

        :param name: Name of statistic
        :param timer: Boolean to toggle creating a single timer upon instantiation
        """
        self.name = name
        if timer:
            self.timers.append(Timer())

    @staticmethod
    def print_stats_summary(time_list, indent=''):
        """
        Print some fancy min, max and average timing stats for various code/functions.
        :param time_list:
        :param indent:
        :return:
        """
        print(indent + "Fastest load: %s seconds." % min(time_list))
        print(indent + "Slowest load: %s seconds." % max(time_list))
        print(indent + "Average load: %s seconds." % float(fsum(time_list) / float(len(time_list))))
