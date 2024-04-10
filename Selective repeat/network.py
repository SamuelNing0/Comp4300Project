import random
import threading
import time


class Network(threading.Thread):
    def __init__(self, network_queue, network_event, send_to_queue, print_lock):
        threading.Thread.__init__(self)
        self.__network_queue = network_queue
        self.__network_event = network_event
        self.__send_to_queue = send_to_queue
        self.__print_lock = print_lock

        self.__stop_event = threading.Event()
        self.__min_delay = 0.01
        self.__max_delay = 0.1
        self.__frame_loss_rate = 20

    def set_network_delay_time(self, min_delay, max_delay):
        self.__min_delay = min_delay
        self.__max_delay = max_delay

    def set_frame_loss_rate(self, frame_loss_rate):
        self.__frame_loss_rate = frame_loss_rate

    def run(self):
        while not self.__stop_event.is_set():
            self.__network_event.wait()

            while not self.__network_queue.empty():
                # Introduce delay
                delay = random.uniform(self.__min_delay, self.__max_delay)
                time.sleep(delay)

                # Send frame
                frame = self.__network_queue.get()

                if self.__frame_loss_rate >= random.randint(1, 100):
                    with self.__print_lock:
                        print("Lost frame:", frame, flush=True)
                else:
                    self.__send_to_queue.put(frame)

            self.__network_event.clear()

    def terminate(self):
        self.__stop_event.set()
        self.__network_event.set()
