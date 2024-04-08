import random
import threading
import time


class Network(threading.Thread):
    def __init__(self, network_queue, network_event, send_to_queue, print_lock):
        threading.Thread.__init__(self)
        self.network_queue = network_queue
        self.network_event = network_event
        self.send_to_queue = send_to_queue
        self.print_lock = print_lock

        self._stop_event = threading.Event()
        self.min_delay = 0.01
        self.max_delay = 0.1
        self.frame_loss_rate = 10

    def set_network_delay_time(self, min_delay, max_delay):
        self.min_delay = min_delay
        self.max_delay = max_delay

    def run(self):
        while not self._stop_event.is_set():
            self.network_event.wait()

            while not self.network_queue.empty():
                # Introduce delay
                delay = random.uniform(self.min_delay, self.max_delay)
                time.sleep(delay)

                # Send frame
                frame = self.network_queue.get()

                if self.frame_loss_rate >= random.randint(1, 100):
                    with self.print_lock:
                        print("Lost frame:", frame, flush=True)
                else:
                    self.send_to_queue.put(frame)

            self.network_event.clear()

    def terminate(self):
        self._stop_event.set()
        self.network_event.set()
