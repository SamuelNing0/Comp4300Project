import simpy
import matplotlib.pyplot as plt

from randomizer import chance_true

SIMULATION_TIME = 1000  # Simulation time in units
SLOT_DURATION = 2.5 # Duration of each time slot at full speed (1 frequency only)
DATA_LOAD_PERCENT = [10, 20, 30, 40, 50, 60, 70, 80, 90]  # percentage that a band has data to send
NUM_NODES = 9  # Number of nodes in the simulation

total_packets = 0
packets_sent_time = {}
packets_sent_time_node = [{},{},{},{},{},{},{},{},{}]


def node(env, name, slot_wait, data_load_percent, node_idx):
    # first iteration wait for slot's turn
    yield env.timeout(slot_wait)
    global total_packets
    node_packets_sent = 0

    # wait time for next iteration
    slot_wait = SLOT_DURATION * (NUM_NODES-1)

    while True:
        # send packet if has packet to send.
        if chance_true(data_load_percent):
            # update both total log and node's log
            total_packets += 1
            node_packets_sent +=1

            packets_sent_time[env.now] = total_packets
            packets_sent_time_node[node_idx][env.now] = node_packets_sent
            print(f"{name} is transmitting at {env.now}")

        # Simulate the duration of the time slot + wait time
        yield env.timeout(SLOT_DURATION)
        yield env.timeout(slot_wait)



env = simpy.Environment()

# Create and schedule transmissions for each node
for i in range(NUM_NODES):
    env.process(node(env, f"Node {i}", i * SLOT_DURATION, DATA_LOAD_PERCENT[i], i))

env.run(until=SIMULATION_TIME)

# Plot size
plt.figure(figsize=(10, 6))
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

    # Plotting the line graph for current band
    plt.plot(times, packets_cummu, label=f'Node: {i+1}, Data Load:{DATA_LOAD_PERCENT[i]}.')



# Plot title and labels
plt.title(f'TDM: Packet Transmission Over Time. Total packets sent: {total_packets} '
          f'Throughput: {total_packets / SIMULATION_TIME} packets/time unit ')
plt.xlabel('Time (Unit)')
plt.ylabel('Cumulative Packets Sent')

# legend
plt.legend()
# Show the plot
plt.show()
