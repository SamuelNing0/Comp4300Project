class Frame:
    def __init__(self, seq_num):
        self.seq_num = seq_num
        self.acknowledgment = False

    def ack(self):
        self.acknowledgment = True

    def __str__(self):
        if self.acknowledgment:
            return f"Frame {self.seq_num} ACK"
        else:
            return f"Frame {self.seq_num}"
