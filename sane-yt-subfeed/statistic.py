from math import fsum
from timer import Timer

all_statistics = []


class Statistic:
    global all_statistics
    timers = []
    tid = 0
    cur_tid = tid
    my_id = None

    def __init__(self, name, timer=False):
        """

        :param name: Name of statistic
        :param timer: Boolean to toggle creating a single timer upon instantiation
        """
        self.name = name
        self.my_id = len(all_statistics)
        if timer:
            self.timers.append(Timer())
            self.tid += 1

        all_statistics.append(self)

    def start_timer(self, tid=None):
        if tid:
            self.timers[tid].start()
        else:
            self.timers.append(Timer())
        self.tid += 1
        self.cur_tid = self.tid

    def stop_timer(self, tid=cur_tid):
        """
        Stop a timer, if no tid is given the latest timer gets stopped
        :param tid:
        :return:
        """
        if tid < 0:
            raise ValueError("Tried to stop a negative time ID! (stop_timer(tid=%s))" % tid)
        if tid > (len(self.timers)-1):
            raise ValueError("Tried to stop a time ID that was out of bounds! (stop_timer(tid=%s), timer amount: %s)"
                             % (tid, len(self.timers)))

        t_elapsed = self.timers[tid].stop()
        self.cur_tid = 0

        # Return elapsed time
        return t_elapsed

    def stop_all_timers(self):
        t_elapsed = []
        for i in range(self.tid + 1):
            t_elapsed.append(self.stop_timer(i))

        # Return elapsed times (list)
        return t_elapsed

    def add_finished_timer(self, time_elapsed):
        self.timers.append(Timer(time_elapsed))

    def print_stats_summary(self, indent='', print_name=True):
        """
        Print some fancy min, max and average timing stats for this Statistic object.
        :param print_name:
        :param indent:
        :return:
        """
        if print_name:
            print(indent + self.name)
        timers_time = []
        print(self.timers)
        for t in self.timers:
            print(t.time_elapsed)
            timers_time.append(t.time_elapsed)
        print(indent + "Fastest load: %s seconds." % min(timers_time))
        print(indent + "Slowest load: %s seconds." % max(timers_time))
        print(indent + "Average load: %s seconds." % float(fsum(timers_time) / float(len(timers_time))))

