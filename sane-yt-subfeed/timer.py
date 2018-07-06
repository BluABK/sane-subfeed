from timeit import default_timer


class Timer:
    t_start = None
    t_stop = None
    time_elapsed = None

    def __init__(self, autostart=True):
        """
        Start, stop and query a default_timer
        :param autostart: start a timer upon instantiation
        """
        if autostart:
            self.start()

    def start(self):
        self.t_start = default_timer()

    def stop(self):
        self.t_stop = default_timer()
        self.time_elapsed = self.t_stop - self.t_start

        # Return elapsed time
        return self.time_elapsed
