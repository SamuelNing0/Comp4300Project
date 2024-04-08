import threading

from timer_manager import TimerManager
from frame import Frame


class Sender(threading.Thread):
    def __init__(self, sender_queue, network_queue, network_event, print_lock):
        threading.Thread.__init__(self)
        self.sender_queue = sender_queue
        self.network_queue = network_queue
        self.network_event = network_event
        self.print_lock = print_lock

        # Set initial sender window parameters
        self.window_size = 4
        self.max_window_size = 8
        self.min_window_size = 1

        # Initialize sequence numbers
        self.send_base = 0
        self.next_seq_num = 0

        # Set default values for simulation parameters
        self.total_frames = 500
        self.timeout = 1

        self.manager = TimerManager()
        self.buff = []

    def resend_frame(self, seq_num):
        if seq_num >= self.send_base:
            with self.print_lock:
                print("Timeout occurred, resending frame", seq_num, flush=True)

            self.network_queue.put(Frame(seq_num))
            self.network_event.set()

        # Restart timer
        self.manager.create_timer(seq_num, self.timeout, self.resend_frame)

    def run(self):
        while self.send_base < self.total_frames:

            # Sending frame
            if self.next_seq_num < min(self.send_base + self.window_size, self.total_frames):
                with self.print_lock:
                    print("Sending frame:", self.next_seq_num, flush=True)
                self.network_queue.put(Frame(self.next_seq_num))
                self.network_event.set()
                self.manager.create_timer(self.next_seq_num, self.timeout, self.resend_frame)
                self.next_seq_num += 1

            # Checking timeout
            self.manager.check_timers()

            # Check for Ack
            while not self.sender_queue.empty():
                ack_frame = self.sender_queue.get()

                with self.print_lock:
                    print("ACK received for frame", ack_frame.seq_num, flush=True)

                if ack_frame.seq_num == self.send_base:
                    self.send_base += 1
                else:
                    self.buff.append(ack_frame.seq_num)

                self.manager.cancel_timer(ack_frame.seq_num)

            while self.send_base in self.buff:
                self.buff.remove(self.send_base)
                self.send_base += 1


