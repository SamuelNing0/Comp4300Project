import simpy
from randomizer import chance_true
import matplotlib.pyplot as plt

# Simulation parameters
NUM_BANDS = 9  # Number of distinct frequency bands
BANDWIDTH_SPEEDS = [5, 5, 5, 5, 5, 5, 5, 5, 5]  # Relative speeds of each band
TOTAL_SPEED = 45 # assume at full speed transmission time is 2 unit
DATA_LOAD_PERCENT = [10, 20, 30, 40, 50, 60, 70, 80, 90] # percentage that a band has data to send
SIMULATION_TIME = 1000

#performance parameters
packets_sent_time = [{},{},{},{},{},{},{},{},{}]
packets_sent = [0,0,0,0,0,0,0,0,0]


def transmit(env, name, band, speed, data_load_percent, index):
    while True:
        # simulate incoming data stream costs 0.5 time unit
        yield env.timeout(0.5)
        if chance_true(data_load_percent):
            with band.request() as req:
                yield req
                print(f"{name} starts transmitting at {env.now} on band with speed {speed}")
                transmission_time = (2*TOTAL_SPEED) / speed  # Simulate faster transmission in faster bands
                yield env.timeout(transmission_time)

                # record cumulative packet number sent and sent time
                packets_sent[index] +=1 ;
                packets_sent_time[index][env.now] = packets_sent[index];
                print(f"{name} ends transmitting at {env.now}")



def plot(title):
    # calculate total packets sent
    total_packets = 0
    for packets in packets_sent:
        total_packets += packets
    # Set up plot
    plt.figure(figsize=(10, 6))

    # Plotting each band's data
    for i, band_data in enumerate(packets_sent_time):
        # Get time and cumulative frames in order
        times = sorted(band_data.keys())
        packets_cummu = [band_data[time] for time in times]

        # Plotting the line graph for current band
        plt.plot(times, packets_cummu,
                 label=f'Band {i + 1}- speed: {BANDWIDTH_SPEEDS[i]}, Data Load:{DATA_LOAD_PERCENT[i]}.')

    # Plot title and labels
    plt.title(f'{title}. Total packets sent: {total_packets} '
              f'Throughput: {total_packets / SIMULATION_TIME} packets/time unit ')
    plt.xlabel('Time (Unit)')
    plt.ylabel('Cumulative Packets Sent')

    # legend
    plt.legend()

    # Show the plot
    plt.show()


def run(graph_title):
    # Set up bandwidth resource
    env = simpy.Environment()
    bands = [simpy.Resource(env) for _ in range(NUM_BANDS)]

    # Assign transmission tasks in each bandwidth(frequency)
    for i, band in enumerate(bands):
        speed = BANDWIDTH_SPEEDS[i]
        load = DATA_LOAD_PERCENT[i]
        env.process(transmit(env, f"Band {i+1}", band, speed, load, i))

    # Run simulation
    env.run(until=SIMULATION_TIME)

    plot(graph_title)


run("FDM: Packet Transmission Over Time by Band")

## Set each band with different bandwidth, proportional to the load
# Simulation parameters
BANDWIDTH_SPEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # Relative speeds of each band

#performance parameters
packets_sent_time = [{},{},{},{},{},{},{},{},{}]
packets_sent = [0,0,0,0,0,0,0,0,0]

run("FDM with various bandwidth: Packet Transmission Over Time by Band")
