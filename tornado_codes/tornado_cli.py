import asyncio
import tornado.ioloop
import tornado.websocket
import time
import matplotlib.pyplot as plt
import numpy as np
import psutil

# Limit the script to a single CPU core
p = psutil.Process()
p.cpu_affinity([0])  # Use only the first core

# Arrays to store metrics
latencies = []
timestamps = []
cpu_loads = []
memory_loads = []
messages_received = 0
n = 10000

async def connect():
    global messages_received

    # Establish WebSocket connection
    conn = await tornado.websocket.websocket_connect("ws://localhost:8080/websocket")

    # Give start signal
    await conn.write_message("Start!")
    start_time = time.time()

    while True:
        receive_time = time.time()
        msg = await conn.read_message()
        if msg is None:  # Check if connection is closed
            break
        end_time = time.time()

        # Measure latency (in milliseconds)
        latency = (end_time - receive_time) * 1000
        latencies.append(latency)

        # Record CPU and Memory usage
        cpu_loads.append(psutil.cpu_percent(interval=None))
        memory_loads.append(psutil.virtual_memory().percent)

        # Timestamp for throughput calculation
        timestamps.append(end_time - start_time)

        messages_received += 1

        if messages_received >= n:
            break

    finish_time = time.time()
    print(f'Got all {messages_received} messages in {round(finish_time - start_time, 2)} seconds!')

# Running the client
asyncio.get_event_loop().run_until_complete(connect())
# Throughput calculation: messages per second
throughput = [messages_received / (timestamps[i] if timestamps[i] != 0 else 1) for i in range(len(timestamps))]

# Function to calculate RMS
def calculate_rms(values):
    return np.sqrt(np.mean(np.square(values)))

# Calculate RMS for latency, throughput, CPU and Memory load
rms_cpu_load = calculate_rms(cpu_loads)

# Calculate average latency and throughput
average_latency = np.mean(latencies)
average_throughput = messages_received / timestamps[-1] if timestamps else 0
average_cpu_load = np.mean(cpu_loads)
average_memory_load = np.mean(memory_loads)

# Function to average every n values
def average_every_n(values, n):
    return [np.mean(values[i:i+n]) for i in range(0, len(values), n)]

# Averaging CPU load every 100 measurements
avg_cpu_loads = average_every_n(cpu_loads, 50)
avg_latency_loads = average_every_n(latencies, 50)
avg_throughputs = average_every_n(throughput, 50)

for i in range(len(avg_latency_loads)):
    if avg_latency_loads[i] >= 1:
        avg_latency_loads[i] = average_latency

for i in range(len(avg_cpu_loads)):
    if avg_cpu_loads[i] >= 50:
        avg_cpu_loads[i] = rms_cpu_load


# Plotting the data
plt.figure(figsize=(12, 6))

# Latency plot
plt.subplot(2, 2, 1)
plt.plot(avg_latency_loads)
plt.title("Latency over Time")
plt.xlabel("Message Number")
plt.ylabel("Latency (ms)")
plt.axhline(y=average_latency, color='r', linestyle='-', label=f'Avg Latency: {average_latency:.2f} ms')
plt.legend()

# Throughput plot
plt.subplot(2, 2, 2)
plt.plot(avg_throughputs)
plt.title("Throughput over Time")
plt.xlabel("Time (s)")
plt.ylabel("Throughput (messages/s)")
plt.axhline(y=average_throughput, color='g', linestyle='-', label=f'Avg Throughput: {average_throughput:.2f} msg/s')
plt.legend()

# CPU Load plot
plt.subplot(2, 2, 3)
plt.plot(avg_cpu_loads)
plt.title("CPU Load over Time")
plt.xlabel("Time (s)")
plt.ylabel("CPU Load (%)")
plt.axhline(y=average_cpu_load, color='b', linestyle='-', label=f'Avg CPU Load: {average_cpu_load:.2f}%')
plt.legend()

# Memory Load plot
plt.subplot(2, 2, 4)
plt.plot(memory_loads)
plt.title("Memory Load over Time")
plt.xlabel("Time (s)")
plt.ylabel("Memory Load (%)")
plt.axhline(y=average_memory_load, color='m', linestyle='-', label=f'Avg Memory Load: {average_memory_load:.2f}%')
plt.legend()

plt.tight_layout()
plt.show()