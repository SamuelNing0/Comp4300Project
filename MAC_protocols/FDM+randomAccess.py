import math
import random
import simpy
import numpy as np
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
node_packets_sent = [[0,0,0],[0,0,0],[0,0,0]]
node_collisions = [[0,0,0],[0,0,0],[0,0,0]]


def node_simulation(env, name, band_status, load_percent, transmission_time, band_idx, node_idx):

    while True:
        yield env.timeout(random.uniform(0, 0.5)) # time duration of checking incoming packets
        if chance_true(load_percent):
            not_sent = True
            curr_collision_count = 0
            while not_sent:

                # Check if band is free
                if not band_status['busy']:
                    # Change band status and send the frame
                    band_status['busy'] = True
                    print(f"{name} starts transmitting at {env.now}")
                    yield env.timeout(transmission_time)
                    print(f"{name} ends transmitting at {env.now}")
                    band_status['busy'] = False
                    not_sent = False

                    # update packets sent log
                    packets_sent[band_idx] += 1
                    node_packets_sent[band_idx][node_idx] += 1

                    packets_sent_time[band_idx][env.now] = packets_sent[band_idx]
                    packets_sent_time_node[band_idx][node_idx][env.now] = node_packets_sent[band_idx][node_idx]

                    # packet sent cooloff time
                    yield env.timeout(random.uniform(0,0.5))

                else:
                    print(f"{name} detected busy band at {env.now}. Wait and Retrying...")
                    curr_collision_count += 1
                    node_collisions[band_idx][node_idx] += 1

                    yield env.timeout(random.randrange(1, 2 ** curr_collision_count))
def transmit(env, name, speed, band_status, data_load_percent, band_idx):
    # transmission time in each band, speed dependent
    transmission_time = ((2*TOTAL_SPEED) / speed)
    yield env.timeout(0.1)

    # Create nodes process for all nodes in this band
    for node_idx in range(NUM_NODES_IN_BAND):
        env.process(node_simulation(env, f"{name}: Node {node_idx+1}",band_status,data_load_percent[node_idx],
                                    transmission_time,band_idx, node_idx))


#Set up bandwidth resource
env = simpy.Environment()
band_status = [{'busy': False} for _ in range(NUM_BANDS)]

# Assign transmission tasks in each bandwidth(frequency)
for band_idx, band in enumerate(band_status):
    speed = BANDWIDTH_SPEEDS[band_idx]
    load = DATA_LOAD_PERCENT_FDM[band_idx]
    env.process(transmit(env, f"Band {band_idx+1}", speed, band, load, band_idx))

# Run simulation
env.run(until=SIMULATION_TIME)



#calculate total packets sent
total_packets =  sum(packets_sent)

# Calculate total collisions and collision rate
band_total_collisions = [0,0,0]
for band_idx, band_collisions in enumerate(node_collisions):
    band_total_collisions[band_idx] = sum(band_collisions)

total_collisions = sum(band_total_collisions)
total_collision_rate = format((total_collisions/(total_collisions+total_packets)) *100, '.2f')

#Set up plot
plt.figure(figsize=(18, 6))

# Plotting each band's data
band_collision_rates = []
for band_idx, band_data in enumerate(packets_sent_time):

    # Get time and cumulative frames in order
    times = sorted(band_data.keys())
    packets_cummu = [band_data[time] for time in times]

    # Plotting the line graph for current band
    band_collision_rate = format(100*(band_total_collisions[band_idx]/(band_total_collisions[band_idx]+packets_sent[band_idx])),'.2f')
    band_collision_rates.append(band_collision_rate)
    plt.plot(times, packets_cummu, label=f'Band {band_idx + 1}- speed: {BANDWIDTH_SPEEDS[band_idx]}, Data Load:{DATA_LOAD_PERCENT_FDM[band_idx]}.'
                                         f'collision rate: {band_collision_rate}%')

# Plot title and labels
plt.title(f'FDM+Random Access: Packet Transmission Over Time by Band. Total packets sent: {total_packets} '
          f'Throughput: {total_packets/SIMULATION_TIME} packets/time unit, Total collision rate: {total_collision_rate}%')
plt.xlabel('Time (Unit)')
plt.ylabel('Cumulative Packets Sent')

# legend
plt.legend()

# Show the plot
plt.show()


#### Plot individual node

for band_idx, band_data in enumerate(packets_sent_time):
    plt.figure(figsize=(18, 6))

    # Get time and cumulative frames in order
    times = sorted(band_data.keys())
    packets_cummu = [band_data[time] for time in times]

    # Plotting the line graph for current band
    plt.plot(times, packets_cummu, label=f'Band {band_idx + 1} total- speed: {BANDWIDTH_SPEEDS[band_idx]}, '
                                         f'Data Load:{DATA_LOAD_PERCENT_FDM[band_idx]}. Band collision rate: {band_collision_rates[band_idx]}%')

    # plot individual node's transmission in this band
    for node_idx in range(NUM_NODES_IN_BAND):
        times = sorted(packets_sent_time_node[band_idx][node_idx].keys())
        packets_cummu = [packets_sent_time_node[band_idx][node_idx][time] for time in times]

        node_collision_rate = format(100*(node_collisions[band_idx][node_idx]/(node_collisions[band_idx][node_idx]+node_packets_sent[band_idx][node_idx])),'.2f')
        plt.plot(times, packets_cummu,
                 label=f'Band {band_idx + 1} Node {node_idx + 1}, Data Load: {DATA_LOAD_PERCENT_FDM[band_idx][node_idx]}. Node collision rate: {node_collision_rate}%')

    # Plot title and labels
    plt.title(f'FDM+Random Access: Packet Transmission Over Time. Band{band_idx+1} packets sent: {packets_sent[band_idx]} '
              f'Band {band_idx+1} throughput: {packets_sent[band_idx] / SIMULATION_TIME} packets/time unit ')
    plt.xlabel('Time (Unit)')
    plt.ylabel('Cumulative Packets Sent')
    plt.legend()
    plt.show()


# Plot packets loss and packets sent comparison

# concatenate node packets sent and node collisions in all bands
node_packets_sent = sum(node_packets_sent, [])
node_collisions = sum(node_collisions, [])



# Display collision and packets send bar plots for each node
# Setting up the x locations
ind = np.arange(len(node_collisions))  # x axis locations
width = 0.3  # the width of the bars

fig, axes = plt.subplots(figsize=(12, 6))
bar1 = axes.bar(ind - width / 2, node_collisions, width, label='Collisions', color='SkyBlue')
bar2 = axes.bar(ind + width / 2, node_packets_sent, width, label='Packets Sent', color='IndianRed')

# Attach labels and title, tick marks and legend
axes.set_xlabel('Node')
axes.set_ylabel('Counts')
axes.set_title(f'Collisions and Packets Comparison Sent by Node in randomAccess protocol.  ')
axes.set_xticks(ind)
ticks_labels = []
for band_idx in range(NUM_BANDS):
    for node_idx in range(NUM_NODES_IN_BAND):
        ticks_labels.append(f"Band {band_idx}Node{node_idx}")

axes.set_xticklabels(ticks_labels)
axes.legend()

# Bar plot labels on top
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        axes.annotate('{}'.format(height),
                      xy=(rect.get_x() + rect.get_width() / 2, height),
                      xytext=(0, 3),  #
                      textcoords="offset points",
                      ha='center', va='bottom')

autolabel(bar1)
autolabel(bar2)

fig.tight_layout()

plt.show()