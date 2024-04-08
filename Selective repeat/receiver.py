import threading


class Receiver(threading.Thread):
    def __init__(self, receiver_queue, network_queue, network_event, print_lock):
        threading.Thread.__init__(self)
        self.receiver_queue = receiver_queue
        self.network_queue = network_queue
        self.network_event = network_event
        self.print_lock = print_lock

        self._stop_event = threading.Event()
        self.expected_seq_num = 0
        self.window_size = 8
        self.buff = []

    def set_window_size(self, window_size):
        self.window_size = window_size

    def run(self):
        while not self._stop_event.is_set():
            while not self.receiver_queue.empty():
                frame = self.receiver_queue.get()

                if self.expected_seq_num <= frame.seq_num < self.expected_seq_num + self.window_size:
                    if frame.seq_num == self.expected_seq_num:
                        with self.print_lock:
                            print("Received frame:", frame.seq_num, flush=True)
                        self.expected_seq_num += 1
                    elif frame.seq_num not in self.buff:
                        with self.print_lock:
                            print("Received out-of-order frame:", frame.seq_num, flush=True)
                        self.buff.append(frame.seq_num)
                    else:
                        with self.print_lock:
                            print("Duplicate frame:", frame.seq_num, flush=True)

                    frame.ack()
                    self.network_queue.put(frame)
                    self.network_event.set()
                elif frame.seq_num < self.expected_seq_num:
                    frame.ack()
                    self.network_queue.put(frame)
                    self.network_event.set()

            while self.expected_seq_num in self.buff:
                self.buff.remove(self.expected_seq_num)
                self.expected_seq_num += 1

    def terminate(self):
        self._stop_event.set()
