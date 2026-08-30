# Digital Twin Architecture

Prototype for the DigitalTwin.ai competition (second round, prototype build).

## System Architecture: 5 Layers

```
REAL / HISTORICAL PRODUCTION DATA
|
v
+--------------------------------+
| 1. DATA + DIGITAL THREAD |
| Parts -> Stations -> Events |
| Sensor streams + timestamps |
+--------------+-----------------+
v
+--------------------------------+
| 2. LIVE DIGITAL TWIN |
| State of every station |
| Buffers / WIP / cycle time |
| Starved / Blocked / Running |
+--------------+-----------------+
v
+--------+--------+
v v
+---------------+ +----------------+
| 3. BOTTLENECK | | 4. DEFECT AI |
| ENGINE | | |
| APM + GNN + | | Temporal model |
| forecasting | | + anomaly AI |
+-------+-------+ +-------+--------+
| |
+--------+--------+
v
+----------------------+
| 5. PRESCRIPTIVE TWIN |
| Counterfactuals |
| What-if simulation |
| Optimization |
+----------+-----------+
v
PLANT TEAM
```

**LLM sits on top as an interface, not the intelligence itself.**

### Layer responsibilities

1. **Data + Digital Thread**: turns raw Bosch production data into a unified trajectory per part: `Part -> Station -> Event`, carrying sensor streams and timestamps.
2. **Live Digital Twin**: current state of every station: buffers, WIP, cycle time, and whether each station is starved / blocked / running.
3. **Bottleneck Engine**: APM baseline (current bottleneck) plus GNN + forecasting to predict where the bottleneck moves next.
4. **Defect AI**: temporal model for evolving defect risk, plus anomaly detection (VAE) for failure modes not seen in historical labels.
5. **Prescriptive Twin**: counterfactual / what-if simulation (SimPy) and optimization, turning predictions into a recommended intervention for the plant team.

## Status

Architecture defined. Build not yet started.
