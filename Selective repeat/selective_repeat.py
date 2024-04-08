import queue
import threading

from network import Network
from receiver import Receiver
from sender import Sender


class SelectiveRepeat:
    def __init__(self):
        self.sender_queue = queue.Queue()
        self.receiver_queue = queue.Queue()
        self.sender_network_queue = queue.Queue()
        self.receiver_network_queue = queue.Queue()
        self.sender_network_event = threading.Event()
        self.receiver_network_event = threading.Event()
        self.print_lock = threading.Lock()

    def run(self):
        sender = Sender(self.sender_queue, self.sender_network_queue, self.sender_network_event, self.print_lock)
        receiver = Receiver(self.receiver_queue, self.receiver_network_queue, self.receiver_network_event,
                            self.print_lock)
        sender_network = Network(self.sender_network_queue, self.sender_network_event, self.receiver_queue,
                                 self.print_lock)
        receiver_network = Network(self.receiver_network_queue, self.receiver_network_event, self.sender_queue,
                                   self.print_lock)

        # Start simulation threads
        sender.start()
        receiver.start()
        sender_network.start()
        receiver_network.start()

        sender.join()  # wait for sender to finish

        # Terminate other threads
        receiver.terminate()
        sender_network.terminate()
        receiver_network.terminate()

        # Wait for other threads to finish
        receiver.join()
        sender_network.join()
        receiver_network.join()
