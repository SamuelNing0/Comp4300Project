import queue
import threading
import time

from network import Network
from receiver import Receiver
from sender import Sender


class SelectiveRepeat:
    def __init__(self):
        self.__sender_queue = queue.Queue()
        self.__receiver_queue = queue.Queue()
        self.__sender_network_queue = queue.Queue()
        self.__receiver_network_queue = queue.Queue()
        self.__sender_network_event = threading.Event()
        self.__receiver_network_event = threading.Event()
        self.__print_lock = threading.Lock()

        self.total_frame_send = 500
        self.cumulative_frame_count = []  # cumulative total number of frames for each attempts
        self.total_time_taken = 0
        self.total_retransmissions = 0

    def __cal_cumulative_frame_count(self, total_frames_per_attempt):
        for i in range(len(total_frames_per_attempt)):
            if i == 0:
                self.cumulative_frame_count.append(total_frames_per_attempt[i])
            else:
                self.cumulative_frame_count.append(self.cumulative_frame_count[i - 1] + total_frames_per_attempt[i])

    def print_stats(self):
        total_frame_sent = self.cumulative_frame_count[len(self.cumulative_frame_count) - 1]

        print("\nTotal time taken:", self.total_time_taken, "second")
        print("Total number of frame sent:", total_frame_sent)
        print("Total number of retransmissions:", self.total_retransmissions)

        print("\nPerformance Metrics")
        print("Throughput:", self.total_frame_send / self.total_time_taken, "frames per second")
        print(f"Efficiency: {(self.total_frame_send / total_frame_sent) * 100}%")
        print("Average number of retransmissions per frame:", self.total_retransmissions / self.total_frame_send)
        print()

    def run(self):
        sender = Sender(self.__sender_queue, self.__sender_network_queue, self.__sender_network_event,
                        self.__print_lock, self.total_frame_send)
        receiver = Receiver(self.__receiver_queue, self.__receiver_network_queue, self.__receiver_network_event,
                            self.__print_lock)
        sender_network = Network(self.__sender_network_queue, self.__sender_network_event, self.__receiver_queue,
                                 self.__print_lock)
        receiver_network = Network(self.__receiver_network_queue, self.__receiver_network_event, self.__sender_queue,
                                   self.__print_lock)

        start_time = time.time()  # Record the start time

        # Start simulation threads
        sender.start()
        receiver.start()
        sender_network.start()
        receiver_network.start()

        sender.join()  # wait for sender to finish

        end_time = time.time()  # Record the end time

        # Terminate other threads
        receiver.terminate()
        sender_network.terminate()
        receiver_network.terminate()

        # Wait for other threads to finish
        receiver.join()
        sender_network.join()
        receiver_network.join()

        # Calculate stats
        self.total_time_taken = end_time - start_time
        self.__cal_cumulative_frame_count(sender.total_frames_per_attempt)
        self.total_retransmissions= sender.total_retransmissions
