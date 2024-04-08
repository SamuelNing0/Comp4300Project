import threading

from timer_manager import TimerManager
from frame import Frame


class Sender(threading.Thread):
    def __init__(self, sender_queue, network_queue, network_event, print_lock, total_frames):
        threading.Thread.__init__(self)
        self.__sender_queue = sender_queue
        self.__network_queue = network_queue
        self.__network_event = network_event
        self.__print_lock = print_lock
        self.__total_frames = total_frames

        # Set initial sender window parameters
        self.__window_size = 4

        # Initialize sequence numbers
        self.__send_base = 0
        self.__next_seq_num = 0

        self.__timeout = 0.5
        self.__manager = TimerManager()
        self.__buff = []

        # Initialize lists to track simulation metrics
        self.total_frames_per_attempt = [0] * 500  # Stores the number of frames sent per sequence number
        self.total_retransmissions = 0  # Track total retransmissions

    def __resend_frame(self, seq_num):
        if seq_num >= self.__send_base:
            with self.__print_lock:
                print("Timeout occurred, resending frame", seq_num, flush=True)

            self.__network_queue.put(Frame(seq_num))
            self.__network_event.set()

            self.total_frames_per_attempt[seq_num] += 1
            self.total_retransmissions += 1

        # Restart timer
        self.__manager.create_timer(seq_num, self.__timeout, self.__resend_frame)

    def run(self):
        while self.__send_base < self.__total_frames:

            # Sending frame
            if self.__next_seq_num < min(self.__send_base + self.__window_size, self.__total_frames):
                with self.__print_lock:
                    print("Sending frame:", self.__next_seq_num, flush=True)
                self.__network_queue.put(Frame(self.__next_seq_num))
                self.__network_event.set()

                self.total_frames_per_attempt[self.__next_seq_num] += 1

                self.__manager.create_timer(self.__next_seq_num, self.__timeout, self.__resend_frame)
                self.__next_seq_num += 1

            # Checking timeout
            self.__manager.check_timers()

            # Check for Ack
            while not self.__sender_queue.empty():
                ack_frame = self.__sender_queue.get()

                with self.__print_lock:
                    print("ACK received for frame", ack_frame.seq_num, flush=True)

                if ack_frame.seq_num == self.__send_base:
                    self.__send_base += 1
                else:
                    self.__buff.append(ack_frame.seq_num)

                self.__manager.cancel_timer(ack_frame.seq_num)

            while self.__send_base in self.__buff:
                self.__buff.remove(self.__send_base)
                self.__send_base += 1


