class Frame:
    def __init__(self, seq_num):
        self.seq_num = seq_num
        self.acknowledgment = False
        self.cumulative_acknowledgment = False
        self.seq_num_list = None

    def ack(self):
        self.acknowledgment = True

    def cum_ack(self, seq_num_list):
        self.cumulative_acknowledgment = True
        self.seq_num_list = seq_num_list

    def __str__(self):
        if self.cumulative_acknowledgment:
            return f"Frame {self.seq_num_list} CUM_ACK"
        elif self.acknowledgment:
            return f"Frame {self.seq_num} ACK"
        else:
            return f"Frame {self.seq_num}"
