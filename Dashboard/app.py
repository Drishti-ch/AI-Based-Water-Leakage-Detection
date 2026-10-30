import streamlit as st
import pandas as pd
import altair as alt
import time
from sqlalchemy import text
import sys
import os


# Allow Python to access the project root
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from Database.database import engine


def styled_line_chart(data, colors=None, height=310):
    """Render a dashboard-matched interactive line chart."""
    chart_data = data.reset_index()
    timestamp_column = chart_data.columns[0]
    value_columns = list(chart_data.columns[1:])

    tidy_data = chart_data.melt(
        id_vars=[timestamp_column],
        value_vars=value_columns,
        var_name="Sensor",
        value_name="Reading"
    )

    color_scale = alt.Scale(
        domain=value_columns,
        range=colors or ["#147d92", "#35c5c8", "#0b5263", "#79d6d0"]
    )

    chart = (
        alt.Chart(tidy_data)
        .mark_line(
            interpolate="monotone",
            strokeWidth=2.2,
            opacity=0.92
        )
        .encode(
            x=alt.X(
                f"{timestamp_column}:T",
                title=None,
                axis=alt.Axis(
                    format="%b %d",
                    labelColor="#9ab7c2",
                    grid=False,
                    tickColor="#315462"
                )
            ),
            y=alt.Y(
                "Reading:Q",
                title=None,
                axis=alt.Axis(
                    labelColor="#9ab7c2",
                    gridColor="#21404b",
                    gridOpacity=.85,
                    tickColor="#315462"
                )
            ),
            color=alt.Color(
                "Sensor:N",
                scale=color_scale,
                legend=alt.Legend(
                    orient="top",
                    title=None,
                    labelColor="#b7d1d8",
                    symbolStrokeWidth=3
                )
            ),
            tooltip=[
                alt.Tooltip(f"{timestamp_column}:T", title="Time", format="%Y-%m-%d %H:%M"),
                alt.Tooltip("Sensor:N"),
                alt.Tooltip("Reading:Q", format=".3f")
            ]
        )
        .properties(height=height)
        .configure_view(stroke="#21404b", fill="#10232d")
        .configure(background="#10232d")
    )
    st.altair_chart(chart, use_container_width=True)


def styled_bar_chart(data, height=280):
    """Render a dashboard-matched status distribution chart."""
    chart_data = data.rename("Readings").reset_index()
    chart_data.columns = ["Status", "Readings"]

    chart = (
        alt.Chart(chart_data)
        .mark_bar(
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8,
            size=70
        )
        .encode(
            x=alt.X(
                "Status:N",
                title=None,
                axis=alt.Axis(labelColor="#b7d1d8", labelAngle=0, ticks=False)
            ),
            y=alt.Y(
                "Readings:Q",
                title=None,
                axis=alt.Axis(labelColor="#9ab7c2", gridColor="#21404b")
            ),
            color=alt.Color(
                "Status:N",
                scale=alt.Scale(
                    domain=["Normal", "Potential Leakage"],
                    range=["#35b99a", "#d64550"]
                ),
                legend=None
            ),
            tooltip=[alt.Tooltip("Status:N"), alt.Tooltip("Readings:Q", format=",d")]
        )
        .properties(height=height)
        .configure_view(stroke="#21404b", fill="#10232d")
        .configure(background="#10232d")
    )
    st.altair_chart(chart, use_container_width=True)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Water Leakage Monitoring",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# Visual theme
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: #e6f7fa;
        --muted: #9ab7c2;
        --blue: #147d92;
        --blue-dark: #61d9df;
        --aqua: #35c5c8;
        --surface: #10232d;
        --surface-soft: #0d1d25;
        --line: #21404b;
        --danger: #d64550;
        --success: #16866a;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--ink);
    }

    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 85% 0%, rgba(20,125,146,.13), transparent 28%),
                    linear-gradient(135deg, #07141b 0%, #0b1c24 48%, #08151c 100%);
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { right: 1rem; }

    .block-container {
        max-width: 1500px;
        padding: 2rem 3rem 4rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--ink) !important;
        letter-spacing: -0.025em;
    }

    h1 { font-size: clamp(2rem, 4vw, 3.25rem) !important; line-height: 1.05 !important; }
    h2 { margin-top: 2rem !important; }
    h3 { margin-top: 1.25rem !important; }

    [data-testid="stMarkdownContainer"] p { color: var(--muted); line-height: 1.65; }
    [data-testid="stCaptionContainer"] p { color: #9ab7c2 !important; }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label { color: #b7d1d8 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #9ab7c2 !important; }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.4rem 2.7rem;
        margin-bottom: 1.8rem;
        border-radius: 28px;
        color: white;
        background: radial-gradient(circle at 86% 20%, rgba(53,197,200,.35), transparent 26%),
                    linear-gradient(120deg, #0b5263 0%, #147d92 55%, #1a9da0 100%);
        box-shadow: 0 18px 45px rgba(11, 82, 99, .18);
    }

    .hero h1 { color: #ffffff !important; margin: 0 0 .7rem; }
    .hero p,
    [data-testid="stMarkdownContainer"] .hero p { color: rgba(255,255,255,.86) !important; max-width: 760px; margin: 0; font-size: 1.05rem; }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        padding: .35rem .75rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,.3);
        border-radius: 999px;
        color: #d7ffff;
        background: rgba(255,255,255,.1);
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    [data-testid="stMetric"] {
        min-height: 126px;
        padding: 1.15rem 1.3rem;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(16,35,45,.92);
        box-shadow: 0 8px 24px rgba(0,0,0,.2);
    }

    [data-testid="stMetricLabel"] p { color: #9ab7c2 !important; font-size: .84rem; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #e6f7fa !important; font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stMetricDelta"] { color: #9ab7c2 !important; }

    [data-testid="stAlert"] {
        border-radius: 16px;
        border: 1px solid rgba(20,125,146,.15);
        box-shadow: 0 8px 20px rgba(16,42,67,.04);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(16,42,67,.05);
    }

    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] { gap: 1rem; }
    [data-testid="stTabs"] [role="tab"] { color: var(--muted); font-weight: 600; }
    [data-testid="stTabs"] [aria-selected="true"] { color: var(--blue-dark); }

    [data-testid="stSidebar"] {
        border-right: 1px solid var(--line);
        background: #0a1a22;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        color: var(--blue-dark) !important;
        font-size: 1.2rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] b { color: #e6f7fa !important; }

    [data-testid="stAlert"] p { color: inherit !important; }
    [data-testid="stDownloadButton"] button,
    [data-testid="stButton"] button { color: #ffffff !important; }

    .section-kicker {
        margin: 1.8rem 0 .25rem;
        color: var(--blue) !important;
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
    }

    .footer {
        padding-top: 1.5rem;
        color: var(--muted);
        font-size: .82rem;
        text-align: center;
    }

    .tech-grid {
        background-image: linear-gradient(rgba(53,197,200,.045) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(53,197,200,.045) 1px, transparent 1px);
        background-size: 28px 28px;
    }

    .live-strip {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: .8rem 1rem;
        margin: .5rem 0 1.25rem;
        border: 1px solid rgba(53,197,200,.35);
        border-radius: 12px;
        color: #b9ffff;
        background: linear-gradient(90deg, #092f3b, #0b5263);
        box-shadow: 0 0 24px rgba(53,197,200,.12), inset 0 0 20px rgba(53,197,200,.05);
        font-family: 'Space Grotesk', sans-serif;
        font-size: .78rem;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .live-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin-right: .45rem;
        border-radius: 50%;
        background: #35e0b0;
        box-shadow: 0 0 0 0 rgba(53,224,176,.7);
        animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(53,224,176,.65); }
        70% { box-shadow: 0 0 0 9px rgba(53,224,176,0); }
        100% { box-shadow: 0 0 0 0 rgba(53,224,176,0); }
    }

    .telemetry-readout {
        padding: .8rem 1rem;
        border-left: 3px solid #35c5c8;
        background: rgba(53,197,200,.08);
        color: #b9ffff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: .86rem;
    }

    @media (max-width: 800px) {
        .block-container { padding: 1.2rem 1rem 3rem; }
        .hero { padding: 1.6rem; border-radius: 20px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Title
# --------------------------------------------------

st.markdown(
    """
    <div class="hero tech-grid">
        <div class="hero-badge">● Live SCADA monitoring</div>
        <h1>AI Water Leakage<br>Monitoring System</h1>
        <p>AI-powered anomaly detection for flow, pressure, and water-level sensors — helping teams spot unusual patterns before they become costly leaks.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="section-kicker">Control center</div>', unsafe_allow_html=True)


# --------------------------------------------------
# Load prediction data
# --------------------------------------------------

@st.cache_data
def load_predictions():

    query = """
        SELECT *
        FROM leakage_predictions
        ORDER BY Timestamp
    """

    return pd.read_sql(
        text(query),
        engine
    )


# --------------------------------------------------
# Load pressure data
# --------------------------------------------------

@st.cache_data
def load_pressure_data():

    query = """
        SELECT Timestamp, n1, n4, n31, n54
        FROM pressure_readings
        ORDER BY Timestamp
    """

    return pd.read_sql(
        text(query),
        engine
    )


# --------------------------------------------------
# Load water level data
# --------------------------------------------------

@st.cache_data
def load_water_level_data():

    query = """
        SELECT Timestamp, T1
        FROM water_level_readings
        ORDER BY Timestamp
    """

    return pd.read_sql(
        text(query),
        engine
    )


# --------------------------------------------------
# Load flow data
# --------------------------------------------------

@st.cache_data
def load_flow_data():

    query = """
        SELECT *
        FROM flow_readings
        ORDER BY Timestamp
    """

    return pd.read_sql(
        text(query),
        engine
    )


# --------------------------------------------------
# Load all data
# --------------------------------------------------

predictions = load_predictions()
flow_data = load_flow_data()
pressure_data = load_pressure_data()
water_level_data = load_water_level_data()


# --------------------------------------------------
# Convert timestamps
# --------------------------------------------------

predictions["Timestamp"] = pd.to_datetime(
    predictions["Timestamp"]
)

flow_data["Timestamp"] = pd.to_datetime(
    flow_data["Timestamp"]
)

pressure_data["Timestamp"] = pd.to_datetime(
    pressure_data["Timestamp"]
)

water_level_data["Timestamp"] = pd.to_datetime(
    water_level_data["Timestamp"]
)

# --------------------------------------------------
# Live demonstration mode
# --------------------------------------------------

with st.sidebar:
    st.markdown("## ◈ Control Deck")
    st.caption("SCADA monitoring interface")
    live_mode = st.toggle("Enable live detection", value=False)

    if live_mode:
        refresh_seconds = st.select_slider(
            "Refresh interval",
            options=[2, 3, 5, 10],
            value=3,
            format_func=lambda value: f"Every {value} seconds"
        )
        st.info("Live demo replays recorded SCADA readings as an advancing sensor stream.")
        st.markdown(
            f'<div class="telemetry-readout">STREAM // ACTIVE<br>REFRESH // {refresh_seconds}s<br>MODE // HISTORICAL REPLAY</div>',
            unsafe_allow_html=True
        )

        # Force periodic reruns so judges can watch the telemetry advance.
        st.markdown(
            f'<meta http-equiv="refresh" content="{refresh_seconds}">',
            unsafe_allow_html=True
        )

        live_position = int((time.time() * 12) % len(predictions))
        live_timestamp = predictions.iloc[live_position]["Timestamp"]
        live_start = max(0, live_position - 287)
        live_end = live_position + 1

        predictions = predictions.iloc[live_start:live_end].copy()
        flow_data = flow_data.iloc[max(0, live_position - 287):live_end].copy()
        pressure_data = pressure_data.iloc[max(0, live_position - 287):live_end].copy()
        water_level_data = water_level_data.iloc[max(0, live_position - 287):live_end].copy()

        st.markdown(
            f'<div class="live-strip"><span><span class="live-dot"></span>Live detection active</span><span>{live_timestamp:%Y-%m-%d %H:%M:%S}</span></div>',
            unsafe_allow_html=True
        )

# --------------------------------------------------
# Date and Time Filter
# --------------------------------------------------

st.subheader("Monitoring Window")

min_date = predictions["Timestamp"].min().date()
max_date = predictions["Timestamp"].max().date()

if not live_mode:
    selected_dates = st.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    selected_dates = None
    st.caption("Live replay window: latest 24 hours of the advancing SCADA stream")

if not live_mode and isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date, end_date = selected_dates

    start_datetime = pd.Timestamp(start_date)
    end_datetime = (
        pd.Timestamp(end_date)
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    predictions = predictions[
        (predictions["Timestamp"] >= start_datetime)
        & (predictions["Timestamp"] <= end_datetime)
    ]

    flow_data = flow_data[
        (flow_data["Timestamp"] >= start_datetime)
        & (flow_data["Timestamp"] <= end_datetime)
    ]

    pressure_data = pressure_data[
        (pressure_data["Timestamp"] >= start_datetime)
        & (pressure_data["Timestamp"] <= end_datetime)
    ]

    water_level_data = water_level_data[
        (water_level_data["Timestamp"] >= start_datetime)
        & (water_level_data["Timestamp"] <= end_datetime)
    ]
# --------------------------------------------------
# KPI calculations
# --------------------------------------------------

total_readings = len(predictions)

normal_readings = len(
    predictions[
        predictions["status"] == "Normal"
    ]
)

potential_leaks = len(
    predictions[
        predictions["status"] == "Potential Leakage"
    ]
)

anomaly_percentage = (
    potential_leaks / total_readings
) * 100


# --------------------------------------------------
# KPI cards
# --------------------------------------------------

st.markdown('<div class="section-kicker">At a glance</div>', unsafe_allow_html=True)
st.subheader("System Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Readings",
        f"{total_readings:,}"
    )

with col2:
    st.metric(
        "Normal Readings",
        f"{normal_readings:,}"
    )

with col3:
    st.metric(
        "Potential Leakage",
        f"{potential_leaks:,}"
    )

with col4:
    st.metric(
        "Anomaly Rate",
        f"{anomaly_percentage:.2f}%"
    )


# --------------------------------------------------
# Latest system status
# --------------------------------------------------

st.markdown('<div class="section-kicker">Operational health</div>', unsafe_allow_html=True)
st.subheader("Current System Status")

latest_status = predictions.iloc[-1]["status"]

if latest_status == "Normal":

    st.success(
        "🟢 Current Status: Normal — "
        "No abnormal sensor pattern detected in the latest reading."
    )

else:

    st.error(
        "🔴 Current Status: Potential Leakage — "
        "An abnormal sensor pattern has been detected."
    )

    # --------------------------------------------------
# Latest Sensor Readings
# --------------------------------------------------

# --------------------------------------------------
# Sensor Health Status
# --------------------------------------------------

st.markdown('<div class="section-kicker">Connected systems</div>', unsafe_allow_html=True)
st.subheader("Sensor Health Status")

health_col1, health_col2, health_col3, health_col4 = st.columns(4)

with health_col1:
    st.success("🟢 Flow Sensors\n\nActive")

with health_col2:
    st.success("🟢 Pressure Sensors\n\nActive")

with health_col3:
    st.success("🟢 Water Level Sensor\n\nActive")

with health_col4:
    st.success("🟢 Prediction System\n\nActive")


st.markdown('<div class="section-kicker">Live telemetry</div>', unsafe_allow_html=True)
st.subheader("Latest Sensor Readings")

latest_flow = flow_data.iloc[-1]
latest_pressure = pressure_data.iloc[-1]
latest_water_level = water_level_data.iloc[-1]

sensor_col1, sensor_col2, sensor_col3, sensor_col4 = st.columns(4)

with sensor_col1:
    st.metric(
        "Flow p227",
        f"{latest_flow['p227']:.2f}"
    )

with sensor_col2:
    st.metric(
        "Flow p235",
        f"{latest_flow['p235']:.2f}"
    )

with sensor_col3:
    st.metric(
        "Pump 1",
        f"{latest_flow['PUMP_1']:.2f}"
    )

with sensor_col4:
    st.metric(
        "Water Level",
        f"{latest_water_level['T1']:.2f}"
    )


pressure_col1, pressure_col2, pressure_col3, pressure_col4 = st.columns(4)

with pressure_col1:
    st.metric(
        "Pressure n1",
        f"{latest_pressure['n1']:.2f}"
    )

with pressure_col2:
    st.metric(
        "Pressure n4",
        f"{latest_pressure['n4']:.2f}"
    )

with pressure_col3:
    st.metric(
        "Pressure n31",
        f"{latest_pressure['n31']:.2f}"
    )

with pressure_col4:
    st.metric(
        "Pressure n54",
        f"{latest_pressure['n54']:.2f}"
    )


# --------------------------------------------------
# AI Model Information
# --------------------------------------------------

st.markdown('<div class="section-kicker">Detection engine</div>', unsafe_allow_html=True)
st.subheader("AI Model Information")

model_col1, model_col2, model_col3, model_col4 = st.columns(4)

with model_col1:
    st.metric(
        "Model",
        "Isolation Forest"
    )

with model_col2:
    st.metric(
        "Features Used",
        "8"
    )

with model_col3:
    st.metric(
        "Estimators",
        "100"
    )

with model_col4:
    st.metric(
        "Anomaly Threshold",
        "5%"
    )

st.divider()

st.markdown('<div class="footer">AI Water Leakage Monitoring · Isolation Forest anomaly detection · SCADA sensor data</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Prediction distribution
# --------------------------------------------------

st.subheader("Detection Summary")

status_counts = (
    predictions["status"]
    .value_counts()
)

styled_bar_chart(status_counts)

# --------------------------------------------------
# Anomaly Timeline
# --------------------------------------------------

st.subheader("Potential Leakage Trend")

anomaly_timeline = (
    predictions[
        predictions["status"] == "Potential Leakage"
    ]
    .set_index("Timestamp")
    .resample("D")
    .size()
)

styled_line_chart(anomaly_timeline.to_frame("Potential Leakage"), colors=["#d64550"], height=280)


# --------------------------------------------------
# Flow monitoring
# --------------------------------------------------

st.subheader("Water Flow Monitoring")

flow_chart = flow_data[
    ["Timestamp", "p227", "p235", "PUMP_1"]
].set_index("Timestamp")

# Display only the latest 1000 readings
# Complete data remains stored in SQLite.
flow_chart = flow_chart.tail(1000)

styled_line_chart(
    flow_chart,
    colors=["#147d92", "#35c5c8", "#0b5263"],
    height=320
)


# --------------------------------------------------
# Sensor Monitoring
# --------------------------------------------------

st.subheader("Sensor Monitoring")

sensor_col1, sensor_col2 = st.columns(2)


# --------------------------------------------------
# Pressure sensors
# --------------------------------------------------

with sensor_col1:

    st.write("**Pressure Sensors**")

    pressure_chart = pressure_data[
        ["Timestamp", "n1", "n4", "n31", "n54"]
    ].set_index("Timestamp")

    # Display only the latest 1000 readings
    pressure_chart = pressure_chart.tail(1000)

    styled_line_chart(
        pressure_chart,
        colors=["#147d92", "#35c5c8", "#0b5263", "#79d6d0"],
        height=300
    )


# --------------------------------------------------
# Water level
# --------------------------------------------------

with sensor_col2:

    st.write("**Water Level**")

    water_chart = water_level_data[
        ["Timestamp", "T1"]
    ].set_index("Timestamp")

    # Display only the latest 1000 readings
    water_chart = water_chart.tail(1000)

    styled_line_chart(water_chart, colors=["#147d92"], height=300)


# --------------------------------------------------
# Potential Leakage Alerts
# --------------------------------------------------

st.subheader("🚨 Potential Leakage Alerts")

leakage_events = predictions[
    predictions["status"] == "Potential Leakage"
].copy()

if len(leakage_events) > 0:

    st.warning(
        f"{len(leakage_events):,} sensor readings have been "
        "identified as potential anomalies."
    )

    # Latest detected anomaly
    latest_alert = leakage_events.iloc[-1]

    alert_col1, alert_col2 = st.columns(2)

    with alert_col1:
        st.metric(
            "Latest Alert Time",
            latest_alert["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        )

    with alert_col2:
        st.metric(
            "Detection Status",
            "Potential Leakage"
        )

    st.write("**Latest Alert Record**")

    st.dataframe(
        pd.DataFrame([latest_alert]),
        width="stretch"
    )

    st.write("**Recent Potential Leakage Events**")

    latest_alerts = leakage_events.tail(10).sort_values(
        "Timestamp",
        ascending=False
    )

    st.dataframe(
        latest_alerts,
        width="stretch"
    )

else:

    st.success(
        "No potential leakage anomalies detected."
    )


# --------------------------------------------------
# Recent predictions
# --------------------------------------------------

st.subheader("Recent Detection Results")

recent_predictions = predictions.tail(20).copy()

st.dataframe(
    recent_predictions,
    width="stretch"
)

# --------------------------------------------------
# Download Detection Results
# --------------------------------------------------

st.subheader("Export Detection Results")

download_data = predictions.copy()

csv_data = download_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Detection Results",
    data=csv_data,
    file_name="water_leakage_detection_results.csv",
    mime="text/csv"
)

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "AI Water Leakage Monitoring System | "
    "Isolation Forest Anomaly Detection | "
    "SQLite Database"
)
