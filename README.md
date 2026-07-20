# 🌐 SDN Congestion Detection & Auto-Mitigation

A Software-Defined Networking (SDN) project that detects link congestion in real time and automatically reroutes traffic — built with **Mininet**, the **Ryu controller**, and **OpenFlow**.

Traditional networks route traffic statically: even when a link is overloaded, packets keep piling up until performance collapses. This project implements a control-plane feedback loop that continuously monitors flow stats, flags congested ports against a threshold, and reroutes traffic on the fly.

---

## ⚙️ How It Works

```
Switch Features Handler → Packet Received → Learn MAC-to-Port Mapping
        ↓
Periodic Port Stats Request (every 10s) → Compare TX packets to threshold
        ↓
Congestion Detected? → Reroute traffic / Flood congested ports
        ↓
Install updated flow rule → Continue monitoring
```

1. **Monitoring** — the Ryu controller polls `OFPFlowStatsRequest` / `OFPPortStatsRequest` on every connected switch every 10 seconds.
2. **Detection** — if a port's TX packet count exceeds a configurable threshold, it's flagged as congested.
3. **Mitigation**:
   - **Traffic rerouting** — flow tables are modified via OpenFlow `FlowMod` messages to push traffic onto alternate paths.
   - **Flooding fallback** — `OFPP_FLOOD` temporarily balances load across multiple ports when no clear alternate path exists.
   - **Logging** — every detection and rerouting action is logged for analysis and threshold tuning.

---

## 🧩 Topologies

Three Mininet topologies were built and tested to evaluate the controller under different network shapes:

| Topology | Description | Scale Tested |
|---|---|---|
| **Linear** | Switches chained in a line, one host per switch | 3 switches, 3 hosts |
| **Tree** | Recursive fanout tree topology | Depth 3, fanout 2 |
| **Fat-Tree** | Core/aggregation/edge layers, standard datacenter topology | k=4 → 7 switches, 8 hosts |

Each topology is paired with its own Ryu controller app that handles switch connections, default flow installation, and congestion monitoring.

---

## 📊 Results

| Test | Result |
|---|---|
| Ping reachability (Linear) | ✅ 100% (6/6 packets) |
| Ping reachability (Tree) | ✅ 100% (12/12 packets) |
| Ping reachability (Fat-Tree) | ✅ 100% (56/56 packets) |
| Throughput (Fat-Tree, iperf) | ✅ ~36.4–36.5 Gbits/sec |
| Congestion detection & reroute | ✅ Verified live in controller logs across all topologies |

**Sample controller log output:**
```
[STATS] Switch=4, Port=1, TX_packets=852908, RX_packets=242999
[DETECTED] Congestion on Switch=4, Port=1. Rerouting traffic.
[ACTION] Flow added: Switch=4, Priority=10, Match=OFPMatch(...)
[ACTION] Traffic rerouted: Switch=4, In_Port=1, Out_Port=OFPP_FLOOD
```

---

## 🛠️ Tech Stack

- **Mininet** — network emulation
- **Ryu** — SDN controller framework (Python, OpenFlow 1.3)
- **OpenFlow** — flow rule installation & stats requests
- **iperf3** — throughput/bandwidth testing
- **PuTTY + VirtualBox** — remote VM access and environment setup

---

## 📂 Project Structure

```
├── linear_topo.py                     # Linear topology definition
├── linear_congestion_controller.py    # Ryu controller for linear topology
├── tree_topo.py                       # Tree topology definition
├── tree_congestion_controller.py      # Ryu controller for tree topology
├── fat_tree_topo.py                   # Fat-tree topology definition
├── fat_tree_congestion_controller.py  # Ryu controller for fat-tree topology
└── README.md
```

---

## ▶️ Running It

```bash
# 1. Start the Ryu controller (in one terminal)
ryu-manager tree_congestion_controller.py

# 2. Launch the topology (in another terminal)
sudo python3 tree_topo.py

# 3. Inside the Mininet CLI
mininet> pingall
mininet> iperf h1 h2
```

Swap `tree_*` for `linear_*` or `fat_tree_*` to run the other topologies.

---

## 💡 Key Learnings

- Debugging the SDN control plane end-to-end: from OpenFlow message flow to real-time flow table manipulation.
- Environment setup taught as much as the code did — resolving a Python "externally managed environment" error, configuring a Host-Only Adapter for a usable static IP, and using `pipx` when `pip3` wouldn't cooperate with Ryu's install.
- Threshold-based detection is simple and effective, but static thresholds have limits — a natural next step is adaptive detection (EWMA or percentile-based) for production-grade sensitivity.

---

## 🔭 Future Improvements

- [ ] Adaptive/dynamic congestion thresholds instead of static packet counts
- [ ] Path-cost-aware rerouting instead of flood-based fallback
- [ ] Integration with a monitoring dashboard (Grafana/Prometheus) for live visualization
- [ ] Automated regression testing across topology scales

---

## 📄 License

This project was built for academic and portfolio purposes. Feel free to fork and adapt for your own SDN experiments.
