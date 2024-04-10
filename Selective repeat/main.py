import matplotlib.pyplot as plt

from selective_repeat import SelectiveRepeat


def graph(total_attempts, ylabel_title, ylabel, cum_ack):
    attempts = list(range(1, total_attempts + 1))

    # Plot graphs
    plt.plot(attempts, ylabel)

    # Add labels and title
    plt.xlabel('Frame send successful')
    plt.ylabel(ylabel_title)

    if cum_ack:
        plt.title('Selective Repeat With Cumulative Acknowledgment')
    else:
        plt.title('Selective Repeat')

    plt.show()


if __name__ == '__main__':
    use_cum_ack = True

    sr = SelectiveRepeat(300)
    sr.run(use_cum_ack, 10, 4, 0.01, 0.3, 20)
    sr.print_stats()
    graph(sr.total_frame_send, "Total Frames Send Per Attempt", sr.total_frames_per_attempt, use_cum_ack)
    graph(sr.total_frame_send, "Cumulative Attempt Count", sr.cumulative_frame_count, use_cum_ack)


