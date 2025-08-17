import time
import csv
from datetime import datetime
import subprocess
import os
import matplotlib.pyplot as plt

# CONFIGURATION

LATENCY_THRESHOLD = 150  # milliseconds
CHECK_INTERVAL = 10      # seconds
LOG_FILE = "network_log.csv"
HTML_FILE = "network_status.html"


# FUNCTIONS

def load_ips(filename="ips.txt"):
    """Load list of IPs/domains from a text file"""
    try:
        with open(filename, "r") as f:
            ips = [line.strip() for line in f if line.strip()]
        return ips
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please create it and add IPs/domains to monitor.")
        return []

def get_default_gateway():
    """Detect default gateway"""
    try:
        route = os.popen("ip route | grep default").read().strip()
        if route:
            return route.split()[2]
        return None
    except Exception as e:
        print(f"Error detecting default gateway: {e}")
        return None

def ping_host(ip):
    """Ping an IP once and return latency (ms) or None if down"""
    try:
        output = subprocess.run(
            ["ping", "-c", "1", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if output.returncode == 0:
            for line in output.stdout.split("\n"):
                if "time=" in line:
                    latency_str = line.split("time=")[1].split(" ")[0]
                    return float(latency_str)
        return None
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return None

def log_result(ip, latency, status):
    """Log results into CSV"""
    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), ip, latency, status])

def update_html_status(results):
    """Write current status into an HTML file"""
    with open(HTML_FILE, "w") as f:
        f.write("<html><head><title>Network Status</title>")
        f.write("<meta http-equiv='refresh' content='60'>")
        f.write("<style>")
        f.write("table {border-collapse: collapse; width: 60%;}")
        f.write("th, td {border: 1px solid black; padding: 8px; text-align: center;}")
        f.write(".ok {background-color: lightgreen;}")
        f.write(".high-latency {background-color: yellow;}")
        f.write(".down {background-color: salmon;}")
        f.write("</style></head><body>")
        f.write("<h2>Network Monitoring Dashboard</h2>")
        f.write(f"<p>Last updated: {datetime.now()}</p>")
        f.write("<table>")
        f.write("<tr><th>IP Address</th><th>Latency (ms)</th><th>Status</th></tr>")

        for ip, latency, status in results:
            css_class = "ok" if status == "OK" else "high-latency" if status == "HIGH LATENCY" else "down"
            latency_display = latency if latency is not None else "N/A"
            f.write(f"<tr class='{css_class}'><td>{ip}</td><td>{latency_display}</td><td>{status}</td></tr>")

        f.write("</table></body></html>")


# MAIN

IPS_TO_MONITOR = load_ips()
gateway_ip = get_default_gateway()
if gateway_ip and gateway_ip not in IPS_TO_MONITOR:
    IPS_TO_MONITOR.insert(0, gateway_ip)

print(f"Monitoring IPs: {IPS_TO_MONITOR}")

# To initialize CSV log
with open(LOG_FILE, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "IP Address", "Latency (ms)", "Status"])

# Visualization setup
plt.ion()
fig, ax = plt.subplots()
latency_history = {ip: [] for ip in IPS_TO_MONITOR}
time_history = []

print("Starting Network Monitoring...")

while True:
    cycle_results = []
    current_time = datetime.now().strftime("%H:%M:%S")
    time_history.append(current_time)

    for ip in IPS_TO_MONITOR:
        latency = ping_host(ip)
        if latency is None:
            status = "DOWN"
            log_result(ip, None, status)
        elif latency > LATENCY_THRESHOLD:
            status = "HIGH LATENCY"
            log_result(ip, latency, status)
        else:
            status = "OK"
            log_result(ip, latency, status)

        cycle_results.append((ip, latency, status))
        print(f"{datetime.now()} | {ip} | {status} | {latency if latency else 'N/A'} ms")

        # Store latency for graph
        if latency is not None:
            latency_history[ip].append(latency)
        else:
            latency_history[ip].append(None)

    update_html_status(cycle_results)

    # Update live visualization
    ax.clear()
    for ip in IPS_TO_MONITOR:
        ax.plot(time_history, latency_history[ip], marker='o', label=ip)
    ax.axhline(y=LATENCY_THRESHOLD, color='r', linestyle='--', label="Threshold")
    ax.set_title("Network Latency Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Latency (ms)")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.pause(0.1)

    time.sleep(CHECK_INTERVAL)
