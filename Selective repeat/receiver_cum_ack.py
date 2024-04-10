import threading


class Receiver(threading.Thread):
    def __init__(self, receiver_queue, network_queue, network_event, print_lock):
        threading.Thread.__init__(self)
        self.__receiver_queue = receiver_queue
        self.__network_queue = network_queue
        self.__network_event = network_event
        self.__print_lock = print_lock

        self.__stop_event = threading.Event()
        self.__expected_seq_num = 0
        self.__window_size = 8
        self.__buff = []

        self.__all_ack_frame = []

    def set_window_size(self, window_size):
        self.__window_size = window_size

    def run(self):
        while not self.__stop_event.is_set():
            while not self.__receiver_queue.empty():
                frame = self.__receiver_queue.get()

                if self.__expected_seq_num <= frame.seq_num < self.__expected_seq_num + self.__window_size:
                    if frame.seq_num == self.__expected_seq_num:
                        with self.__print_lock:
                            print("Received frame:", frame.seq_num, flush=True)
                        self.__all_ack_frame.append(frame.seq_num)
                        self.__expected_seq_num += 1
                    elif frame.seq_num not in self.__buff:
                        with self.__print_lock:
                            print("Received out-of-order frame:", frame.seq_num, flush=True)
                        self.__all_ack_frame.append(frame.seq_num)
                        self.__buff.append(frame.seq_num)
                    else:
                        with self.__print_lock:
                            print("Duplicate frame:", frame.seq_num, flush=True)

                    seq_num_list = [seq_num for seq_num in self.__all_ack_frame
                                    if seq_num >= self.__expected_seq_num - 1]
                    frame.cum_ack(seq_num_list)
                    self.__network_queue.put(frame)
                    self.__network_event.set()
                elif frame.seq_num < self.__expected_seq_num:
                    with self.__print_lock:
                        print("Duplicate frame outside the window:", frame.seq_num, flush=True)

                    seq_num_list = [seq_num for seq_num in self.__all_ack_frame
                                    if seq_num >= frame.seq_num]
                    frame.cum_ack(seq_num_list)
                    self.__network_queue.put(frame)
                    self.__network_event.set()

            while self.__expected_seq_num in self.__buff:
                self.__buff.remove(self.__expected_seq_num)
                self.__expected_seq_num += 1

    def terminate(self):
        self.__stop_event.set()
