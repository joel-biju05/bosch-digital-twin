import os
import warnings
from textwrap import dedent

warnings.filterwarnings("ignore")

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Bosch Digital Twin",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_html(content):
    """
    Safely render HTML/CSS using Streamlit.
    """
    st.markdown(
        dedent(content).strip(),
        unsafe_allow_html=True
    )


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EVENT_FILE = os.path.join(
    BASE_DIR,
    "layer5_dashboard_compact.parquet"
)

PART_FILE = os.path.join(
    BASE_DIR,
    "layer5_part_summary.parquet"
)

STATION_FILE = os.path.join(
    BASE_DIR,
    "layer5_station_summary.parquet"
)

FACTORY_FILE = os.path.join(
    BASE_DIR,
    "layer5_factory_summary.csv"
)




required_files = {
    "Digital Twin Events": EVENT_FILE,
    "Part Summary": PART_FILE,
    "Station Summary": STATION_FILE,
    "Factory Summary": FACTORY_FILE
}

missing_files = [
    name
    for name, path in required_files.items()
    if not os.path.exists(path)
]

if missing_files:

    st.error("Some Layer 5 files are missing.")

    for name in missing_files:
        st.write(f"❌ {name}")

    st.info(
        "Make sure all four Layer 5 files are in the same folder as app.py."
    )

    st.stop()



@st.cache_data
def load_data():

    
        

    factory_df = pd.read_csv(FACTORY_FILE)

    # Check required factory columns
    if "metric" not in factory_df.columns:
        raise ValueError(
            "Factory summary CSV must contain a 'metric' column."
        )

    if "value" not in factory_df.columns:
        raise ValueError(
            "Factory summary CSV must contain a 'value' column."
        )

    factory_dict = dict(
        zip(
            factory_df["metric"].astype(str),
            pd.to_numeric(
                factory_df["value"],
                errors="coerce"
            )
        )
    )

     

    part_df = pd.read_parquet(PART_FILE)
    station_df = pd.read_parquet(STATION_FILE)


    event_columns = [
        "event_id",
        "part_id",
        "line",
        "station",
        "timestamp",
        "anomaly_score",
        "anomaly_level",
        "sensor_anomaly_score",
        "process_anomaly_score",
        "wip_anomaly_score",
        "flow_anomaly_score",
        "factory_anomaly_score",
        "predicted_defect_probability",
        "quality_risk",
        "dashboard_status"
    ]

    # Read only available columns
    event_schema = pd.read_parquet(
        EVENT_FILE
    ).columns.tolist()

    available_columns = [
        column
        for column in event_columns
        if column in event_schema
    ]

    events = pd.read_parquet(
        EVENT_FILE,
        columns=available_columns
    )


    string_columns = [
        "line",
        "anomaly_level",
        "quality_risk",
        "dashboard_status"
    ]

    for column in string_columns:

        if column in events.columns:

            events[column] = (
                events[column]
                .astype("string")
                .str.strip()
            )



    if "station" in events.columns:

        events["station"] = pd.to_numeric(
            events["station"],
            errors="coerce"
        )


    if "timestamp" in events.columns:

        events["timestamp"] = pd.to_numeric(
            events["timestamp"],
            errors="coerce"
        )


    numeric_columns = [
        "anomaly_score",
        "sensor_anomaly_score",
        "process_anomaly_score",
        "wip_anomaly_score",
        "flow_anomaly_score",
        "factory_anomaly_score",
        "predicted_defect_probability"
    ]

    for column in numeric_columns:

        if column in events.columns:

            events[column] = pd.to_numeric(
                events[column],
                errors="coerce"
            )

    return (
        factory_dict,
        part_df,
        station_df,
        events
    )


# =============================================================================
# LOAD EVERYTHING
# =============================================================================

try:

    (
        factory,
        part_df,
        station_df,
        events
    ) = load_data()

except Exception as e:

    st.error(
        "Failed to load Layer 5 data."
    )

    st.exception(e)

    st.stop()


# =============================================================================
# FACTORY METRICS
# =============================================================================

def safe_int(value, default=0):

    try:

        if pd.isna(value):
            return default

        return int(float(value))

    except (TypeError, ValueError):

        return default


def safe_float(value, default=0.0):

    try:

        if pd.isna(value):
            return default

        return float(value)

    except (TypeError, ValueError):

        return default


total_events = safe_int(
    factory.get("total_events", 0)
)

total_parts = safe_int(
    factory.get("total_parts", 0)
)

total_stations = safe_int(
    factory.get("total_stations", 0)
)

normal_events = safe_int(
    factory.get("normal_events", 0)
)

warning_events = safe_int(
    factory.get("warning_events", 0)
)

anomalous_events = safe_int(
    factory.get("anomalous_events", 0)
)

critical_parts = safe_int(
    factory.get("critical_quality_parts", 0)
)

high_parts = safe_int(
    factory.get("high_quality_parts", 0)
)

mean_anomaly = safe_float(
    factory.get("mean_anomaly_score", 0)
)

max_anomaly = safe_float(
    factory.get("max_anomaly_score", 0)
)

mean_defect_probability = safe_float(
    factory.get(
        "mean_predicted_defect_probability",
        0
    )
)


warning_pct = (
    warning_events /
    max(total_events, 1)
    * 100
)

anomaly_pct = (
    anomalous_events /
    max(total_events, 1)
    * 100
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

render_html("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.bosch-header {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #1f2937 100%
    );

    padding: 32px 36px;
    border-radius: 18px;
    margin-bottom: 28px;
    color: white;

    box-shadow:
        0 8px 25px rgba(0,0,0,0.12);
}

.bosch-title {
    font-size: 36px;
    font-weight: 750;
    margin: 0;
    letter-spacing: -0.5px;
    color: #ffffff;
}

.bosch-subtitle {
    font-size: 18px;
    margin-top: 10px;
    color: #f3f4f6;
    opacity: 0.95;
}

.bosch-small {
    font-size: 13px;
    margin-top: 9px;
    color: #d1d5db;
    opacity: 0.75;
}

.section-title {
    font-size: 25px;
    font-weight: 750;
    color: #111827;
    margin-top: 24px;
    margin-bottom: 18px;
}

.kpi-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 22px;
    min-height: 150px;

    box-shadow:
        0 3px 12px rgba(0,0,0,0.06);

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);

    box-shadow:
        0 8px 22px rgba(0,0,0,0.10);
}

.kpi-title {
    font-size: 13px;
    color: #6b7280;
    font-weight: 650;
}

.kpi-value {
    font-size: 30px;
    font-weight: 750;
    color: #111827;
    margin-top: 8px;
}

.kpi-description {
    font-size: 12px;
    color: #9ca3af;
    margin-top: 7px;
}

.status-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 20px;

    box-shadow:
        0 3px 12px rgba(0,0,0,0.05);
}

.status-title {
    font-size: 13px;
    color: #6b7280;
    font-weight: 650;
}

.status-value {
    font-size: 24px;
    font-weight: 750;
    margin-top: 6px;
}

.footer {
    text-align: center;
    color: #9ca3af;
    font-size: 12px;
    padding: 35px 0 10px 0;
}

</style>
""")


# =============================================================================
# SIDEBAR
# =============================================================================

st.sidebar.title("🏭 Navigation")

view = st.sidebar.radio(
    "Select View",
    [
        "Factory Overview",
        "Station Intelligence",
        "Part Intelligence",
        "Anomaly Intelligence"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "BOSCH DIGITAL TWIN"
)

st.sidebar.write(
    f"📦 {total_parts:,} tracked parts"
)

st.sidebar.write(
    f"⚙️ {total_stations} production stations"
)

st.sidebar.write(
    f"📊 {total_events:,} events"
)

st.sidebar.divider()

st.sidebar.caption(
    "Layer 5 Digital Twin Analytics"
)

# =============================================================================
# FACTORY OVERVIEW
# =============================================================================

if view == "Factory Overview":

    render_html("""
    <div class="section-title">
        📊 Factory Overview
    </div>
    """)

    # =========================================================================
    # KPI ROW 1
    # =========================================================================

    c1, c2, c3 = st.columns(3)

    with c1:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Events</div>
            <div class="kpi-value">{total_events:,}</div>
            <div class="kpi-description">
                Factory digital-thread events
            </div>
        </div>
        """)

    with c2:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Tracked Parts</div>
            <div class="kpi-value">{total_parts:,}</div>
            <div class="kpi-description">
                Unique production parts
            </div>
        </div>
        """)

    with c3:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Production Stations</div>
            <div class="kpi-value">{total_stations:,}</div>
            <div class="kpi-description">
                Stations monitored
            </div>
        </div>
        """)

    st.write("")

    # =========================================================================
    # KPI ROW 2
    # =========================================================================

    c1, c2, c3 = st.columns(3)

    with c1:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Warning Events</div>
            <div class="kpi-value">{warning_events:,}</div>
            <div class="kpi-description">
                {warning_pct:.2f}% of all events
            </div>
        </div>
        """)

    with c2:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Anomalous Events</div>
            <div class="kpi-value">{anomalous_events:,}</div>
            <div class="kpi-description">
                {anomaly_pct:.4f}% of all events
            </div>
        </div>
        """)

    with c3:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-title">Critical Quality Parts</div>
            <div class="kpi-value">{critical_parts:,}</div>
            <div class="kpi-description">
                Highest predicted quality risk
            </div>
        </div>
        """)

    # =========================================================================
    # FACTORY HEALTH
    # =========================================================================

    render_html("""
    <div class="section-title">
        🏭 Factory Health
    </div>
    """)

    h1, h2, h3 = st.columns(3)

    with h1:
        render_html(f"""
        <div class="status-card">
            <div class="status-title">
                Mean Anomaly Score
            </div>
            <div class="status-value">
                {mean_anomaly:.4f}
            </div>
        </div>
        """)

    with h2:
        render_html(f"""
        <div class="status-card">
            <div class="status-title">
                Maximum Anomaly Score
            </div>
            <div class="status-value">
                {max_anomaly:.4f}
            </div>
        </div>
        """)

    with h3:
        render_html(f"""
        <div class="status-card">
            <div class="status-title">
                Mean Defect Probability
            </div>
            <div class="status-value">
                {mean_defect_probability:.4f}
            </div>
        </div>
        """)

    # =========================================================================
    # FACTORY ANOMALY DISTRIBUTION
    # =========================================================================

    render_html("""
    <div class="section-title">
        🚨 Factory Anomaly Distribution
    </div>
    """)

    anomaly_distribution = pd.DataFrame({
        "Anomaly Level": [
            "NORMAL",
            "WARNING",
            "ANOMALOUS"
        ],
        "Events": [
            normal_events,
            warning_events,
            anomalous_events
        ]
    })

    col1, col2 = st.columns(2)

    with col1:

        fig = px.pie(
            anomaly_distribution,
            names="Anomaly Level",
            values="Events",
            hole=0.55,
            title="Event Status"
        )

        fig.update_layout(
            height=430,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        fig = px.bar(
            anomaly_distribution,
            x="Anomaly Level",
            y="Events",
            text="Events",
            title="Event Count"
        )

        fig.update_layout(
            height=430,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # =========================================================================
    # QUALITY RISK DISTRIBUTION
    # =========================================================================

    render_html("""
    <div class="section-title">
        🎯 Part-Level Quality Risk
    </div>
    """)

    if "quality_risk" in part_df.columns:

        quality_distribution = (
            part_df["quality_risk"]
            .astype("string")
            .str.upper()
            .str.strip()
            .value_counts()
            .reset_index()
        )

        quality_distribution.columns = [
            "Quality Risk",
            "Parts"
        ]

        fig = px.bar(
            quality_distribution,
            x="Quality Risk",
            y="Parts",
            text="Parts",
            title="Quality Risk Distribution"
        )

        fig.update_layout(
            height=450,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "Quality-risk information is not available."
        )

    # =========================================================================
    # HIGHEST-RISK PARTS
    # =========================================================================

    render_html("""
    <div class="section-title">
        🚨 Highest-Risk Parts
    </div>
    """)

    probability_col = None

    for candidate in [
        "predicted_defect_probability",
        "defect_probability"
    ]:

        if candidate in part_df.columns:
            probability_col = candidate
            break

    if probability_col:

        risk_parts = part_df.copy()

        risk_parts[probability_col] = pd.to_numeric(
            risk_parts[probability_col],
            errors="coerce"
        )

        risk_parts = (
            risk_parts
            .dropna(subset=[probability_col])
            .sort_values(
                probability_col,
                ascending=False
            )
            .head(15)
        )

        display_columns = [
            c for c in [
                "part_id",
                "quality_risk",
                probability_col,
                "digital_twin_status",
                "mean_anomaly_score",
                "max_anomaly_score",
                "anomalous_events",
                "warning_events"
            ]
            if c in risk_parts.columns
        ]

        if display_columns:

            st.dataframe(
                risk_parts[display_columns],
                width="stretch",
                hide_index=True
            )

        else:

            st.info(
                "No compatible columns are available for the risk table."
            )

    else:

        st.warning(
            "Predicted defect probability column was not found."
        )


# =============================================================================
# STATION INTELLIGENCE
# =============================================================================

elif view == "Station Intelligence":

    render_html("""
    <div class="section-title">
        🏭 Station Intelligence
    </div>
    """)

    st.write(
        "Analyze anomaly levels, production activity and quality risk "
        "across the monitored production stations."
    )

    # =========================================================================
    # STATION STATUS
    # =========================================================================

    if "digital_twin_status" in station_df.columns:

        status_counts = (
            station_df["digital_twin_status"]
            .astype("string")
            .str.upper()
            .str.strip()
            .value_counts()
            .reset_index()
        )

        status_counts.columns = [
            "Status",
            "Stations"
        ]

        fig = px.bar(
            status_counts,
            x="Status",
            y="Stations",
            text="Stations",
            title="Station Digital Twin Status"
        )

        fig.update_layout(
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "Station digital-twin status information is not available."
        )

    # =========================================================================
    # TOP STATIONS BY ANOMALY
    # =========================================================================

    render_html("""
    <div class="section-title">
        🚨 Highest-Anomaly Stations
    </div>
    """)

    station_score_col = None

    for candidate in [
        "mean_anomaly_score",
        "max_anomaly_score"
    ]:

        if candidate in station_df.columns:
            station_score_col = candidate
            break

    if station_score_col:

        station_plot = station_df.copy()

        station_plot[station_score_col] = pd.to_numeric(
            station_plot[station_score_col],
            errors="coerce"
        )

        station_plot = (
            station_plot
            .dropna(subset=[station_score_col])
            .sort_values(
                station_score_col,
                ascending=False
            )
            .head(15)
        )

        if "station_key" in station_plot.columns:

            station_label = "station_key"

        elif "station" in station_plot.columns:

            station_label = "station"

        else:

            station_label = station_plot.columns[0]

        fig = px.bar(
            station_plot,
            x=station_label,
            y=station_score_col,
            text_auto=".3f",
            title="Top 15 Stations by Anomaly Score"
        )

        fig.update_layout(
            height=520,
            xaxis_title="Station",
            yaxis_title="Anomaly Score",
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "No station anomaly-score column was found."
        )

    # =========================================================================
    # STATION QUALITY RISK
    # =========================================================================

    render_html("""
    <div class="section-title">
        🎯 Station Quality Risk
    </div>
    """)

    if "mean_quality_risk_probability" in station_df.columns:

        risk_plot = station_df.copy()

        risk_plot["mean_quality_risk_probability"] = pd.to_numeric(
            risk_plot["mean_quality_risk_probability"],
            errors="coerce"
        )

        risk_plot = (
            risk_plot
            .dropna(subset=["mean_quality_risk_probability"])
            .sort_values(
                "mean_quality_risk_probability",
                ascending=False
            )
            .head(15)
        )

        if "station_key" in risk_plot.columns:

            station_label = "station_key"

        elif "station" in risk_plot.columns:

            station_label = "station"

        else:

            station_label = risk_plot.columns[0]

        fig = px.bar(
            risk_plot,
            x=station_label,
            y="mean_quality_risk_probability",
            text_auto=".3f",
            title="Top 15 Stations by Quality Risk"
        )

        fig.update_layout(
            height=520,
            xaxis_title="Station",
            yaxis_title="Mean Quality Risk Probability",
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "Station quality-risk probability is not available."
        )

    # =========================================================================
    # FULL STATION TABLE
    # =========================================================================

    st.subheader("Station Summary")

    display_columns = [
        c for c in [
            "station_key",
            "line",
            "station",
            "total_events",
            "total_parts",
            "mean_anomaly_score",
            "max_anomaly_score",
            "anomalous_events",
            "warning_events",
            "mean_quality_risk_probability",
            "max_quality_risk_probability",
            "anomaly_rate_pct",
            "digital_twin_status"
        ]
        if c in station_df.columns
    ]

    if display_columns:

        st.dataframe(
            station_df[display_columns],
            width="stretch",
            height=550,
            hide_index=True
        )

    else:

        st.warning(
            "No station summary columns are available."
        )


# =============================================================================
# PART INTELLIGENCE
# =============================================================================

elif view == "Part Intelligence":

    render_html("""
    <div class="section-title">
        🔩 Part Intelligence
    </div>
    """)

    st.write(
        "Identify production parts with elevated predicted defect "
        "probability and anomaly exposure."
    )

    # =========================================================================
    # FIND PROBABILITY COLUMN
    # =========================================================================

    probability_col = None

    for candidate in [
        "predicted_defect_probability",
        "defect_probability"
    ]:

        if candidate in part_df.columns:
            probability_col = candidate
            break

    if probability_col:

        # =====================================================================
        # CLEAN PROBABILITY DATA
        # =====================================================================

        part_plot = part_df.copy()

        part_plot[probability_col] = pd.to_numeric(
            part_plot[probability_col],
            errors="coerce"
        )

        part_plot = part_plot.dropna(
            subset=[probability_col]
        )

        # =====================================================================
        # PROBABILITY DISTRIBUTION
        # =====================================================================

        if not part_plot.empty:

            fig = px.histogram(
                part_plot,
                x=probability_col,
                nbins=40,
                title="Predicted Defect Probability Distribution"
            )

            fig.update_layout(
                height=430,
                xaxis_title="Predicted Defect Probability",
                yaxis_title="Parts",
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20
                )
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "No valid defect-probability values are available."
            )

        # =====================================================================
        # QUALITY RISK DISTRIBUTION
        # =====================================================================

        if "quality_risk" in part_df.columns:

            risk_counts = (
                part_df["quality_risk"]
                .astype("string")
                .str.upper()
                .str.strip()
                .value_counts()
                .reset_index()
            )

            risk_counts.columns = [
                "Quality Risk",
                "Parts"
            ]

            fig = px.bar(
                risk_counts,
                x="Quality Risk",
                y="Parts",
                text="Parts",
                title="Part Quality-Risk Categories"
            )

            fig.update_layout(
                height=430,
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20
                )
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        # =====================================================================
        # TOP 50 PARTS
        # =====================================================================

        st.subheader("🚨 Highest-Risk Parts")

        top_parts = (
            part_plot
            .sort_values(
                probability_col,
                ascending=False
            )
            .head(50)
            .copy()
        )

        display_columns = [
            c for c in [
                "part_id",
                "quality_risk",
                probability_col,
                "digital_twin_status",
                "total_events",
                "number_of_unique_stations",
                "mean_process_time",
                "max_process_time",
                "mean_station_wip",
                "max_station_wip",
                "mean_sensor_coverage",
                "mean_bottleneck_score",
                "mean_anomaly_score",
                "max_anomaly_score",
                "anomalous_events",
                "warning_events"
            ]
            if c in top_parts.columns
        ]

        if display_columns:

            st.dataframe(
                top_parts[display_columns],
                width="stretch",
                height=650,
                hide_index=True
            )

        else:

            st.warning(
                "No compatible part-summary columns were found."
            )

    else:

        st.warning(
            "Predicted defect probability column was not found "
            "in the part summary."
        )


# =============================================================================
# ANOMALY INTELLIGENCE
# =============================================================================

elif view == "Anomaly Intelligence":

    render_html("""
    <div class="section-title">
        🚨 Anomaly Intelligence
    </div>
    """)

    st.write(
        "Investigate production events using line, station, anomaly "
        "and quality-risk filters."
    )

    # =========================================================================
    # REQUIRED COLUMNS
    # =========================================================================

    required_anomaly_columns = [
        "anomaly_score",
        "anomaly_level"
    ]

    missing_anomaly_columns = [
        column
        for column in required_anomaly_columns
        if column not in events.columns
    ]

    if missing_anomaly_columns:

        st.error(
            "The event dataset is missing required columns:"
        )

        for column in missing_anomaly_columns:
            st.write(f"❌ {column}")

        st.info(
            "Check the Layer 5 digital twin events parquet file."
        )

    else:

        # =====================================================================
        # FILTERS
        # =====================================================================

        col1, col2, col3, col4 = st.columns(4)

        # ---------------------------------------------------------------------
        # LINE OPTIONS
        # ---------------------------------------------------------------------

        line_options = ["ALL"]

        if "line" in events.columns:

            line_values = (
                events["line"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

            line_options += sorted(line_values)

        # ---------------------------------------------------------------------
        # STATION OPTIONS
        # ---------------------------------------------------------------------

        station_options = ["ALL"]

        if "station" in events.columns:

            station_values = (
                events["station"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

            def station_sort_key(value):

                try:
                    return (0, int(value))

                except (ValueError, TypeError):
                    return (1, str(value))

            station_options += sorted(
                station_values,
                key=station_sort_key
            )

        # ---------------------------------------------------------------------
        # ANOMALY OPTIONS
        # ---------------------------------------------------------------------

        anomaly_options = [
            "ALL",
            "NORMAL",
            "WARNING",
            "ANOMALOUS"
        ]

        # ---------------------------------------------------------------------
        # QUALITY OPTIONS
        # ---------------------------------------------------------------------

        quality_options = [
            "ALL",
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ]

        # ---------------------------------------------------------------------
        # FILTER WIDGETS
        # ---------------------------------------------------------------------

        with col1:

            selected_line = st.selectbox(
                "Production Line",
                line_options,
                key="anomaly_line_filter"
            )

        with col2:

            selected_station = st.selectbox(
                "Station",
                station_options,
                key="anomaly_station_filter"
            )

        with col3:

            selected_anomaly = st.selectbox(
                "Anomaly Level",
                anomaly_options,
                key="anomaly_level_filter"
            )

        with col4:

            selected_quality = st.selectbox(
                "Quality Risk",
                quality_options,
                key="anomaly_quality_filter"
            )

        # =====================================================================
        # FILTER DATA
        # =====================================================================

        filtered = events.copy()

        # ---------------------------------------------------------------------
        # LINE FILTER
        # ---------------------------------------------------------------------

        if (
            selected_line != "ALL"
            and "line" in filtered.columns
        ):

            filtered = filtered[
                filtered["line"]
                .astype(str)
                .str.strip()
                .eq(selected_line)
            ]

        # ---------------------------------------------------------------------
        # STATION FILTER
        # ---------------------------------------------------------------------

        if (
            selected_station != "ALL"
            and "station" in filtered.columns
        ):

            filtered = filtered[
                filtered["station"]
                .astype(str)
                .str.strip()
                .eq(selected_station)
            ]

        # ---------------------------------------------------------------------
        # ANOMALY FILTER
        # ---------------------------------------------------------------------

        if selected_anomaly != "ALL":

            filtered = filtered[
                filtered["anomaly_level"]
                .astype(str)
                .str.upper()
                .str.strip()
                .eq(selected_anomaly)
            ]

        # ---------------------------------------------------------------------
        # QUALITY FILTER
        # ---------------------------------------------------------------------

        if (
            selected_quality != "ALL"
            and "quality_risk" in filtered.columns
        ):

            filtered = filtered[
                filtered["quality_risk"]
                .astype(str)
                .str.upper()
                .str.strip()
                .eq(selected_quality)
            ]

        # =====================================================================
        # FILTERED RESULTS
        # =====================================================================

        st.markdown("### 📊 Filtered Results")

        k1, k2, k3 = st.columns(3)

        with k1:

            st.metric(
                "Filtered Events",
                f"{len(filtered):,}"
            )

        with k2:

            mean_filtered_anomaly = pd.to_numeric(
                filtered["anomaly_score"],
                errors="coerce"
            ).mean()

            if pd.notna(mean_filtered_anomaly):

                st.metric(
                    "Mean Anomaly Score",
                    f"{mean_filtered_anomaly:.4f}"
                )

            else:

                st.metric(
                    "Mean Anomaly Score",
                    "N/A"
                )

        with k3:

            if "predicted_defect_probability" in filtered.columns:

                mean_filtered_defect = pd.to_numeric(
                    filtered["predicted_defect_probability"],
                    errors="coerce"
                ).mean()

                if pd.notna(mean_filtered_defect):

                    st.metric(
                        "Mean Defect Probability",
                        f"{mean_filtered_defect:.4f}"
                    )

                else:

                    st.metric(
                        "Mean Defect Probability",
                        "N/A"
                    )

            else:

                st.metric(
                    "Mean Defect Probability",
                    "N/A"
                )

        # =====================================================================
        # NO RESULTS
        # =====================================================================

        if filtered.empty:

            st.warning(
                "No events match the selected filters."
            )

        else:

            # ================================================================
            # CLEAN NUMERIC DATA
            # ================================================================

            filtered = filtered.copy()

            filtered["anomaly_score"] = pd.to_numeric(
                filtered["anomaly_score"],
                errors="coerce"
            )

            if "predicted_defect_probability" in filtered.columns:

                filtered["predicted_defect_probability"] = pd.to_numeric(
                    filtered["predicted_defect_probability"],
                    errors="coerce"
                )

            # ================================================================
            # SCORE DISTRIBUTIONS
            # ================================================================

            col1, col2 = st.columns(2)

            # ----------------------------------------------------------------
            # ANOMALY SCORE
            # ----------------------------------------------------------------

            with col1:

                anomaly_plot_data = filtered[
                    filtered["anomaly_score"].notna()
                ]

                if not anomaly_plot_data.empty:

                    fig = px.histogram(
                        anomaly_plot_data,
                        x="anomaly_score",
                        nbins=40,
                        title="Anomaly Score Distribution"
                    )

                    fig.update_layout(
                        height=420,
                        margin=dict(
                            l=20,
                            r=20,
                            t=60,
                            b=20
                        )
                    )

                    st.plotly_chart(
                        fig,
                        width="stretch"
                    )

                else:

                    st.info(
                        "No valid anomaly-score values available."
                    )

            # ----------------------------------------------------------------
            # DEFECT PROBABILITY
            # ----------------------------------------------------------------

            with col2:

                if "predicted_defect_probability" in filtered.columns:

                    probability_plot_data = filtered[
                        filtered["predicted_defect_probability"].notna()
                    ]

                    if not probability_plot_data.empty:

                        fig = px.histogram(
                            probability_plot_data,
                            x="predicted_defect_probability",
                            nbins=40,
                            title="Predicted Defect Probability"
                        )

                        fig.update_layout(
                            height=420,
                            margin=dict(
                                l=20,
                                r=20,
                                t=60,
                                b=20
                            )
                        )

                        st.plotly_chart(
                            fig,
                            width="stretch"
                        )

                    else:

                        st.info(
                            "No valid defect-probability values available."
                        )

                else:

                    st.info(
                        "Predicted defect probability is not available."
                    )

            # ================================================================
            # ANOMALY LEVEL DISTRIBUTION
            # ================================================================

            st.markdown(
                "### 🚨 Anomaly Level Distribution"
            )

            dist = (
                filtered["anomaly_level"]
                .astype(str)
                .str.upper()
                .str.strip()
                .value_counts()
                .reset_index()
            )

            dist.columns = [
                "Anomaly Level",
                "Events"
            ]

            fig = px.bar(
                dist,
                x="Anomaly Level",
                y="Events",
                text="Events",
                title="Filtered Anomaly Levels"
            )

            fig.update_layout(
                height=400,
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20
                )
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

            # ================================================================
            # HIGHEST-RISK EVENTS
            # ================================================================

            st.markdown(
                "### 🚨 Highest-Risk Events"
            )

            top_events = (
                filtered
                .sort_values(
                    "anomaly_score",
                    ascending=False,
                    na_position="last"
                )
                .head(50)
                .copy()
            )

            # ================================================================
            # PRODUCTION TIME
            # ================================================================

            if "timestamp" in top_events.columns:

                top_events["Production Time"] = (
                    pd.to_numeric(
                        top_events["timestamp"],
                        errors="coerce"
                    )
                    .apply(
                        lambda x:
                        f"T+{x:.2f}s"
                        if pd.notna(x)
                        else "N/A"
                    )
                )

            # ================================================================
            # EVENT TABLE
            # ================================================================

            display_columns = [
                c for c in [
                    "event_id",
                    "part_id",
                    "line",
                    "station",
                    "Production Time",
                    "anomaly_score",
                    "anomaly_level",
                    "quality_risk",
                    "predicted_defect_probability",
                    "dashboard_status"
                ]
                if c in top_events.columns
            ]

            if display_columns:

                st.dataframe(
                    top_events[display_columns],
                    width="stretch",
                    height=600,
                    hide_index=True
                )

            else:

                st.info(
                    "No event columns are available for display."
                )

            # ================================================================
            # ANOMALY COMPONENTS
            # ================================================================

            st.markdown(
                "### 🧠 Anomaly Components"
            )

            component_mapping = {
                "Sensor": "sensor_anomaly_score",
                "Process": "process_anomaly_score",
                "WIP": "wip_anomaly_score",
                "Flow": "flow_anomaly_score",
                "Factory": "factory_anomaly_score"
            }

            component_rows = []

            for name, column in component_mapping.items():

                if column not in filtered.columns:
                    continue

                values = pd.to_numeric(
                    filtered[column],
                    errors="coerce"
                )

                valid_values = values.dropna()

                if valid_values.empty:
                    continue

                component_rows.append(
                    {
                        "Component": name,

                        "Mean Score": float(
                            valid_values.mean()
                        ),

                        "Maximum Score": float(
                            valid_values.max()
                        ),

                        "Events": int(
                            (valid_values > 0).sum()
                        )
                    }
                )

            # ================================================================
            # COMPONENT VISUALIZATION
            # ================================================================

            if component_rows:

                component_df = pd.DataFrame(
                    component_rows
                )

                col1, col2 = st.columns(2)

                # ----------------------------------------------------------------
                # MEAN
                # ----------------------------------------------------------------

                with col1:

                    fig = px.bar(
                        component_df,
                        x="Component",
                        y="Mean Score",
                        text_auto=".4f",
                        title="Mean Anomaly Score"
                    )

                    fig.update_layout(
                        height=430,
                        margin=dict(
                            l=20,
                            r=20,
                            t=60,
                            b=20
                        )
                    )

                    st.plotly_chart(
                        fig,
                        width="stretch"
                    )

                # ----------------------------------------------------------------
                # MAXIMUM
                # ----------------------------------------------------------------

                with col2:

                    fig = px.bar(
                        component_df,
                        x="Component",
                        y="Maximum Score",
                        text_auto=".4f",
                        title="Maximum Anomaly Score"
                    )

                    fig.update_layout(
                        height=430,
                        margin=dict(
                            l=20,
                            r=20,
                            t=60,
                            b=20
                        )
                    )

                    st.plotly_chart(
                        fig,
                        width="stretch"
                    )

                # ----------------------------------------------------------------
                # COMPONENT TABLE
                # ----------------------------------------------------------------

                st.dataframe(
                    component_df,
                    width="stretch",
                    hide_index=True
                )

            else:

                st.info(
                    "No anomaly-component data is available "
                    "for the selected events."
                )


# =============================================================================
# FOOTER
# =============================================================================

render_html("""
<div class="footer">

    <b>Bosch Digital Twin Analytics Platform</b><br>

    Layer 5 • Factory Intelligence •
    Station Intelligence •
    Part Intelligence •
    Anomaly Detection

</div>
""")


# =============================================================================
# END
# =============================================================================

