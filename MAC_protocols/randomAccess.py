import simpy
import random
import matplotlib.pyplot as plt
import numpy as np
from randomizer import chance_true

SIMULATION_TIME = 1000  # Simulation time in units
DATA_LOAD_PERCENT = [10, 20, 30, 40, 50, 60, 70, 80, 90]  # percentage that a band has data to send
NUM_NODES = 9  # Number of nodes in the simulation
TRANSMISSION_TIME = 2

# Performance metrics
total_packets = 0
packets_sent_time = {} # over all time- packets sent log
packets_sent_time_node = [{},{},{},{},{},{},{},{},{}]
node_collisions = [0,0,0,0,0,0,0,0,0]
node_packets_sent = [0,0,0,0,0,0,0,0,0]

def node_simulation(env, name, band_status, load_percent, node_idx):
    global total_packets

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
                    yield env.timeout(TRANSMISSION_TIME)
                    print(f"{name} ends transmitting at {env.now}")
                    band_status['busy'] = False
                    not_sent = False

                    # update packets sent log
                    total_packets += 1
                    node_packets_sent[node_idx] += 1

                    packets_sent_time[env.now] = total_packets
                    packets_sent_time_node[node_idx][env.now] = node_packets_sent[node_idx]

                    # packet sent cooloff time
                    yield env.timeout(random.uniform(0,0.5))

                else:
                    print(f"{name} detected busy band at {env.now}. Wait and Retrying...")
                    curr_collision_count += 1
                    node_collisions[node_idx] += 1

                    yield env.timeout(random.randrange(1, 2 ** curr_collision_count))


env = simpy.Environment()
band_status = {'busy': False}  # Shared medium status

# Create multiple nodes
for node_idx in range(NUM_NODES):
    env.process(node_simulation(env, f"Node {node_idx + 1}", band_status, DATA_LOAD_PERCENT[node_idx], node_idx))

env.run(until=SIMULATION_TIME)


# Calculate total collisions and collision rate
total_collisions = 0
for collision_count in node_collisions:
    total_collisions += collision_count

total_collision_rate = format((total_collisions/(total_collisions+total_packets)) *100, '.2f')

# Plot size
plt.figure(figsize=(15, 6))
# Get time and cumulative frames in order
times = sorted(packets_sent_time.keys())
frames = [packets_sent_time[time] for time in times]

# Plotting the line graph for the band
plt.plot(times, frames, label = "Total frames sent in all node.")

# Plot individual node's frames
for i in range(NUM_NODES):

    # Get time and cumulative frames in order
    times = sorted(packets_sent_time_node[i].keys())
    packets_cummu = [packets_sent_time_node[i][time] for time in times]

    # Plotting the line graph for current node
    plt.plot(times, packets_cummu, label=f'Node: {i+1}, Data Load:{DATA_LOAD_PERCENT[i]}, packets sent:'
                                         f' {node_packets_sent[i]}, (collision rate={100*(node_collisions[i]/(node_collisions[i]+node_packets_sent[i]))}%')



# Plot title and labels
plt.title(f'Random Access: Packet Transmission Over Time. Total packets sent: {total_packets} '
          f'Throughput: {total_packets / SIMULATION_TIME} packets/time unit, Total collision rate {total_collision_rate}%')
plt.xlabel('Time (Unit)')
plt.ylabel('Cumulative Packets Sent')

# legend
plt.legend()
# Show the plot
plt.show()


# Display collision and packets send bar plots for each node
# Setting up the x locations
ind = np.arange(len(node_collisions))  # x axis locations
width = 0.3  # the width of the bars

fig, axes = plt.subplots(figsize=(12, 6))
bar1 = axes.bar(ind - width / 2, node_collisions, width, label='Collisions', color='IndianRed')
bar2 = axes.bar(ind + width / 2, node_packets_sent, width, label='Packets Sent', color='SkyBlue')

# Attach labels and title, tick marks and legend
axes.set_xlabel('Node')
axes.set_ylabel('Counts')
axes.set_title(f'Collisions and Packets Comparison Sent by Node in randomAccess protocol.  ')
axes.set_xticks(ind)
axes.set_xticklabels([f'Node {i + 1}' for i in range(len(node_collisions))])
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


