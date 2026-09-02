# 🏭 Bosch Digital Twin — Factory Intelligence Platform

A data-driven **Digital Twin Analytics Platform** designed to monitor and analyze manufacturing operations using production events, anomaly detection, quality-risk prediction, and interactive dashboards.

The project transforms manufacturing data into actionable insights at the **factory, station, part, and event levels**.

PROTOTYPE LINK : https://bosch-digital-twin-dazhd6kjuqvngcvuhpsfwr.streamlit.app/
---

## 🚀 Project Overview

Modern manufacturing systems generate large amounts of data from production lines, stations, sensors, and individual parts.

This project builds a Digital Twin analytics layer that uses this information to:

- Monitor factory-wide production activity
- Identify abnormal production events
- Detect high-risk production stations
- Identify parts with elevated quality risk
- Analyze predicted defect probability
- Investigate sensor, process, WIP, flow, and factory anomalies
- Present the results through an interactive Streamlit dashboard

The goal is to provide a **single visual interface for understanding manufacturing health and production risks**.

---

## 🎯 Key Features

### 📊 Factory Overview

Provides a high-level view of the manufacturing system, including:

- Total production events
- Number of tracked parts
- Number of monitored stations
- Warning events
- Anomalous events
- Critical-quality-risk parts
- Mean and maximum anomaly scores
- Mean predicted defect probability
- Factory anomaly distribution
- Part quality-risk distribution
- Highest-risk parts

---

### 🏭 Station Intelligence

Analyzes individual production stations to identify areas requiring attention.

Features include:

- Station Digital Twin status
- Station anomaly scores
- Highest-anomaly stations
- Station quality-risk probability
- Production activity
- Station-level summary tables

---

### 🔩 Part Intelligence

Provides part-level production and quality analysis.

The dashboard identifies parts with elevated:

- Predicted defect probability
- Quality risk
- Anomaly exposure
- Process-time variation
- Station WIP
- Sensor coverage
- Bottleneck scores

It also provides a ranking of the highest-risk parts.

---

### 🚨 Anomaly Intelligence

Allows users to investigate individual production events using interactive filters.

Available filters include:

- Production Line
- Station
- Anomaly Level
- Quality Risk

The dashboard provides:

- Filtered event counts
- Mean anomaly score
- Mean defect probability
- Anomaly-score distributions
- Defect-probability distributions
- Anomaly-level distribution
- Highest-risk events
- Sensor anomaly scores
- Process anomaly scores
- WIP anomaly scores
- Flow anomaly scores
- Factory anomaly scores

---

## 🧠 Anomaly Detection

The platform combines multiple anomaly dimensions to provide a broader view of manufacturing behavior.

The main anomaly components are:

| Component | Purpose |
|---|---|
| Sensor Anomaly | Identifies unusual sensor-related behavior |
| Process Anomaly | Identifies unusual production/process behavior |
| WIP Anomaly | Detects unusual Work-In-Progress conditions |
| Flow Anomaly | Identifies unusual production-flow behavior |
| Factory Anomaly | Represents broader factory-level abnormality |

These signals contribute to the overall **anomaly score** used by the dashboard.

---

## 🏗️ System Architecture

The project follows a layered Digital Twin architecture:

```text
Manufacturing Data
        │
        ▼
┌──────────────────────────┐
│ Digital Thread / Events  │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Feature Engineering      │
│ & Production Analytics   │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Quality & Anomaly Models │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Layer 5 Digital Twin     │
│ Analytics                │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Streamlit Dashboard      │
└──────────────────────────┘





