import threading

FILE = "/etc/issue"


class OpenFileDescriptorThread(threading.Thread):

    def __init__(self, thread_id):
        """
        Init OpenFileDescriptorThread
        :param thread_id:
        :param channel:
        :param info:
        :param debug:
        """
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.f = None

    def run(self):
        """
        Override threading.Thread.run() with its own code
        :return:
        """
        self.f = open(FILE, 'r')
        self.f.read()


def open_1000_file_descriptors():
    """
    Used for debugging issues where python hits the fd ceiling ulimit.
    :return:
    """
    fd_threads = []

    # Create threads
    for i in range(1000):
        thread = OpenFileDescriptorThread(i)
        fd_threads.append(thread)

    # Run threads
    for t in fd_threads:
        t.start()

