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


def main(cumulative_ack, loss_rate):

    sr = SelectiveRepeat(500)
    sr.run(cumulative_ack, 5, 1, 0.01, 0.05, loss_rate)
    sr.print_stats()
    graph(sr.total_frame_send, "Total Frames Send Per Attempt", sr.total_frames_per_attempt, cumulative_ack)
    graph(sr.total_frame_send, "Cumulative Attempt Count", sr.cumulative_frame_count, cumulative_ack)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Selective Repeat Simulation")
    parser.add_argument("-lr", "--loss-rate", type=int, default=5, help="Frame loss rate")
    parser.add_argument("-cum-ack", "--cumulative-ack", action="store_true", help="Enable cumulative acknowledgment")
    args = parser.parse_args()

    main(args.cumulative_ack, args.loss_rate)
