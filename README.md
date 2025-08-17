**NETWORK MONITOR DASHBOARD**

A lightweight python tool to help monitor the network, log latency and visualize its results in an auto refreshing HTML dashboard.
It pings a list of IPs/Domains from ips.txt, logs the result to network_log.csv and generates a browser friendly dashboard network_status.html which contains a status table as well as rolling latency graphs.

Features:
1. Can monitor multiple IPs or Domains from thr ips.txt
2. Detects the status - OK / High Latency / Down
3. Logs reults to network_log.csv, current logs along with previous logs
4. Auto-detects default gateway and monitors it too
5. Auto-refreshing HTML dashboard

Python 3.8+

**Packages**: matplotlib

**Dashboard Preview**
Status Table:
Green = OK
Yellow = High Latency
Red = Down

**Future Improvements**
~Email/SMS alerts
~Configurable thresholds per IP
~Dockerized Version
