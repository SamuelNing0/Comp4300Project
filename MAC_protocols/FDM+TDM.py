import simpy
from randomizer import chance_true
import matplotlib.pyplot as plt

# Simulation parameters
NUM_BANDS = 3  # Number of distinct frequency bands
NUM_NODES_IN_BAND = 3 # number of nodes  sharing a band using TDM
BANDWIDTH_SPEEDS = [1, 2, 3]  # Relative speeds of each band
TOTAL_SPEED = 6 # assume at full speed  transmission time is 2 unit
DATA_LOAD_PERCENT_FDM = [[10, 20, 30], [40, 50, 60], [70, 80, 90] ]# percentage that a band has data to send
SIMULATION_TIME = 1000

#performance parameters
packets_sent_time = [{},{},{}]
packets_sent = [0,0,0]
packets_sent_time_node = [[{},{},{}], [{},{},{}], [{},{},{}]]



def node(env, name, band, slot_duration, slot_wait, data_load_percent, band_idx, node_num):
    # first iteration wait for slot's turn
    yield env.timeout(slot_wait)
    # wait time for next iteration
    slot_wait = slot_duration * (NUM_NODES_IN_BAND-1)
    packets_sent_node = 0

    while True:

        # send packet if has packet to send.
        if chance_true(data_load_percent):
            with band.request() as req:
                yield req
                # update both band and node packets sent
                packets_sent[band_idx] += 1
                packets_sent_node += 1

                packets_sent_time[band_idx][env.now] = packets_sent[band_idx]
                packets_sent_time_node[band_idx][node_num][env.now] = packets_sent_node
                print(f"{name} is transmitting at {env.now}")

        yield env.timeout(slot_duration)
        yield env.timeout(slot_wait)


def transmit(env, name, band, speed, data_load_percent, band_index):
    # TDM slow duration in each band, speed dependent
    slot_duration = ((2*TOTAL_SPEED) / speed)+0.5
    yield env.timeout(0.1)

    # Create nodes process for all nodes in this band
    for node_num in range(NUM_NODES_IN_BAND):
        initial_slot_wait = node_num * slot_duration
        env.process(node(env, f"{name}: Node {node_num+1}", band, slot_duration,  initial_slot_wait, data_load_percent[node_num], band_index, node_num))



# Set up bandwidth resource
env = simpy.Environment()
bands = [simpy.Resource(env) for _ in range(NUM_BANDS)]

# Assign transmission tasks in each bandwidth(frequency)
for band_idx, band in enumerate(bands):
    speed = BANDWIDTH_SPEEDS[band_idx]
    load = DATA_LOAD_PERCENT_FDM[band_idx]
    env.process(transmit(env, f"Band {band_idx+1}", band, speed, load, band_idx))

# Run simulation
env.run(until=SIMULATION_TIME)




#calculate total packets sent
total_packets = 0
for packets in packets_sent:
    total_packets += packets

#Set up plot
plt.figure(figsize=(12, 6))

# Plotting each band's data
for band_idx, band_data in enumerate(packets_sent_time):

    # Get time and cumulative frames in order
    times = sorted(band_data.keys())
    packets_cummu = [band_data[time] for time in times]

    # Plotting the line graph for current band
    plt.plot(times, packets_cummu, label=f'Band {band_idx + 1} total- speed: {BANDWIDTH_SPEEDS[band_idx]}, Data Load:{DATA_LOAD_PERCENT_FDM[band_idx]}.')

# Plot title and labels
plt.title(f'FDM+TDM: Packet Transmission Over Time by Band. Total packets sent: {total_packets} '
          f'Throughput: {total_packets/SIMULATION_TIME} packets/time unit ')
plt.xlabel('Time (Unit)')
plt.ylabel('Cumulative Packets Sent')

# legend
plt.legend()

# Show the plot
plt.show()

#### Plot individual node
for band_idx, band_data in enumerate(packets_sent_time):
    plt.figure(figsize=(12, 6))

    # Get time and cumulative frames in order
    times = sorted(band_data.keys())
    packets_cummu = [band_data[time] for time in times]

    # Plotting the line graph for current band
    plt.plot(times, packets_cummu, label=f'Band {band_idx + 1} total- speed: {BANDWIDTH_SPEEDS[band_idx]}, Data Load:{DATA_LOAD_PERCENT_FDM[band_idx]}.')

    # plot individual node's transmission in this band
    for node_idx in range(NUM_NODES_IN_BAND):
        times = sorted(packets_sent_time_node[band_idx][node_idx].keys())
        packets_cummu = [packets_sent_time_node[band_idx][node_idx][time] for time in times]
        plt.plot(times, packets_cummu,
                 label=f'Band {band_idx + 1} Node {node_idx + 1}, Data Load:{DATA_LOAD_PERCENT_FDM[band_idx][node_idx]}.')

    # Plot title and labels
    plt.title(f'FDM+TDM: Packet Transmission Over Time. Band {band_idx+1} packets sent: {packets_sent[band_idx]}, '
              f'Band {band_idx+1} throughput: {packets_sent[band_idx] / SIMULATION_TIME} packets/time unit ')
    plt.xlabel('Time (Unit)')
    plt.ylabel('Cumulative Packets Sent')
    plt.legend()
    plt.show()