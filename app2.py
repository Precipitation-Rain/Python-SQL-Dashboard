import streamlit as st
from db import run_query
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Airlines Dashboard",
    layout="wide",
    page_icon="✈️"
)

# ─────────────────────────────────────────────
#  GLOBAL STYLE
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Font */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Background */
    .stApp {
        background-color: #0f1117;
        color: #e8eaf0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b27;
        border-right: 1px solid #1e2535;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a2035, #1e2840);
        border: 1px solid #2a3550;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] { color: #7b8db0 !important; font-size: 12px; }
    [data-testid="stMetricValue"] { color: #e8eaf0 !important; font-size: 24px; font-weight: 600; }

    /* Section headers */
    h1 { color: #ffffff !important; font-weight: 600; letter-spacing: -0.5px; }
    h2 { color: #c5cde8 !important; font-weight: 500; }
    h3 { color: #a0aec8 !important; font-weight: 500; font-size: 15px; }

    /* Divider */
    hr { border-color: #1e2535 !important; }

    /* Multiselect tags */
    [data-baseweb="tag"] {
        background-color: #2a4080 !important;
        border-radius: 6px !important;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #2a4080, #1e5fa8);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-family: 'DM Sans', sans-serif;
        font-size: 13px;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* Insight cards */
    .insight-card {
        background: linear-gradient(135deg, #1a2035, #1a2840);
        border: 1px solid #2a3550;
        border-left: 3px solid #3a7bd5;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        font-size: 14px;
        color: #c5cde8;
        line-height: 1.6;
    }
    .insight-card span {
        color: #5ba3f5;
        font-weight: 600;
    }

    /* Chart containers */
    .chart-box {
        background: #161b27;
        border: 1px solid #1e2535;
        border-radius: 12px;
        padding: 16px;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CHART THEME — dark matplotlib
# ─────────────────────────────────────────────
def set_chart_style():
    mpl.rcParams.update({
        "figure.facecolor":  "#161b27",
        "axes.facecolor":    "#161b27",
        "axes.edgecolor":    "#2a3550",
        "axes.labelcolor":   "#7b8db0",
        "xtick.color":       "#7b8db0",
        "ytick.color":       "#7b8db0",
        "grid.color":        "#1e2535",
        "grid.linestyle":    "--",
        "grid.alpha":        0.5,
        "text.color":        "#c5cde8",
        "font.family":       "DejaVu Sans",
    })

PALETTE = ["#3a7bd5", "#00c9a7", "#f7971e", "#e040fb", "#ff6b6b", "#4ecdc4"]

def styled_fig(w=8, h=4):
    set_chart_style()
    fig, ax = plt.subplots(figsize=(w, h))
    ax.grid(axis="y", alpha=0.3)
    return fig, ax

PLOTLY_THEME = dict(
    paper_bgcolor="#161b27",
    plot_bgcolor="#161b27",
    font=dict(color="#c5cde8", family="DM Sans"),
    colorway=PALETTE,
)


# ─────────────────────────────────────────────
#  HELPER — build WHERE clause
# ─────────────────────────────────────────────
def build_where(filters: dict) -> str:
    """
    filters = {
        'airline':        list,
        'source_city':    list,
        'destination_city': list,
        'departure_time': list,
        'stops':          list,
        'arrival_time':   list,
        'class':          list,
        'price':          (min, max) tuple  — optional
        'days_left':      (min, max) tuple  — optional
    }
    Returns a WHERE clause string (empty string if no filters).
    """
    conditions = []

    col_map = {
        "airline":           "airline",
        "source_city":       "source_city",
        "destination_city":  "destination_city",
        "departure_time":    "departure_time",
        "stops":             "stops",
        "arrival_time":      "arrival_time",
        "class":             "class",
    }

    for key, col in col_map.items():
        vals = filters.get(key, [])
        if vals:
            escaped = ", ".join(f"'{v}'" for v in vals)
            conditions.append(f"{col} IN ({escaped})")

    if "price" in filters:
        lo, hi = filters["price"]
        conditions.append(f"price BETWEEN {lo} AND {hi}")

    if "days_left" in filters:
        lo, hi = filters["days_left"]
        conditions.append(f"days_left BETWEEN {lo} AND {hi}")

    return ("WHERE " + " AND ".join(conditions)) if conditions else ""


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✈️ Airlines Dashboard")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "🏠 Overview",
            "💰 Price Analysis",
            "✈️ Route & City",
            "🕐 Time Patterns",
            "🏢 Airline Comparison",
            "🔍 Data Explorer",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.success("🟢 Database Connected")
    st.caption("Indian Airline Flights Dataset")


# ══════════════════════════════════════════════
#  PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════
if page == "🏠 Overview":

    st.title("🏠 Overview")
    st.caption("High-level summary of the entire flight dataset")
    st.markdown("---")

    # ── KPI Cards ──────────────────────────────
    st.subheader("Key Metrics")
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        val = run_query("SELECT COUNT(*) FROM flight").iloc[0, 0]
        st.metric("Total Flights", f"{val:,}")
    with c2:
        val = run_query("SELECT COUNT(DISTINCT airline) FROM flight").iloc[0, 0]
        st.metric("Airlines", val)
    with c3:
        val = run_query("SELECT ROUND(AVG(price)) FROM flight").iloc[0, 0]
        st.metric("Avg Ticket Price", f"₹{val:,}")
    with c4:
        val = run_query("SELECT MAX(price) FROM flight").iloc[0, 0]
        st.metric("Most Expensive", f"₹{val:,}")
    with c5:
        val = run_query("SELECT MIN(price) FROM flight").iloc[0, 0]
        st.metric("Cheapest Ticket", f"₹{val:,}")
    with c6:
        val = run_query("SELECT ROUND(AVG(duration)) FROM flight").iloc[0, 0]
        st.metric("Avg Duration (hrs)", val)

    st.markdown("---")

    # ── Insights ───────────────────────────────
    st.subheader("📌 Key Insights")

    insights = [
        ("Business class tickets cost roughly <span>3–5× more</span> than Economy — "
         "yet only a small fraction of travellers book them, making Economy the true "
         "volume driver for every airline."),

        ("Prices <span>drop sharply when booked 30+ days early</span>. "
         "Last-minute bookings (under 7 days) can be 40–60 % more expensive — "
         "booking early is the single biggest money-saving lever."),

        ("<span>Vistara and Air India</span> consistently command the highest average fares, "
         "while IndiGo and SpiceJet anchor the budget end — "
         "reflecting their distinct positioning in the Indian market."),

        ("Routes involving <span>Mumbai and Delhi</span> dominate both flight count and revenue, "
         "confirming these two metros as the backbone of domestic air travel in India."),

        ("Flights with <span>zero stops</span> are priced higher on average than one-stop flights "
         "— travellers pay a clear premium for convenience, not just distance."),
    ]

    for text in insights:
        st.markdown(f'<div class="insight-card">💡 {text}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Charts ─────────────────────────────────
    st.subheader("Flight Distribution")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Total Flights per Route")
        df = run_query("""
            SELECT CONCAT(source_city, ' → ', destination_city) AS route,
                   COUNT(*) AS no_of_flights
            FROM flight
            GROUP BY source_city, destination_city
            ORDER BY no_of_flights DESC
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["route"], y=df["no_of_flights"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Route", fontsize=10)
        ax.set_ylabel("Flights", fontsize=10)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown("##### Avg Price by Airline")
        df = run_query("""
            SELECT airline, ROUND(AVG(price)) AS price
            FROM flight
            GROUP BY airline
            ORDER BY price DESC
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["airline"], y=df["price"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Airline", fontsize=10)
        ax.set_ylabel("Avg Price (₹)", fontsize=10)
        plt.xticks(rotation=30, ha="right", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("##### Avg Price vs Days Left to Departure")
        df = run_query("""
            SELECT days_left, ROUND(AVG(price)) AS price
            FROM flight
            GROUP BY days_left
            ORDER BY days_left
        """)
        fig, ax = styled_fig(7, 4)
        sns.lineplot(x=df["days_left"], y=df["price"], color=PALETTE[0], linewidth=2, ax=ax)
        ax.set_xlabel("Days Left", fontsize=10)
        ax.set_ylabel("Avg Price (₹)", fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)

    with col4:
        st.markdown("##### Market Share by Airline")
        df = run_query("""
            SELECT airline,
                   COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flight) AS percentage_share
            FROM flight
            GROUP BY airline
        """)
        fig = px.pie(
            df, names="airline", values="percentage_share",
            color_discrete_sequence=PALETTE,
            hole=0.4,
        )
        fig.update_layout(**PLOTLY_THEME, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
#  PAGE 2 — PRICE ANALYSIS
# ══════════════════════════════════════════════
elif page == "💰 Price Analysis":

    st.title("💰 Price Analysis")
    st.caption("Explore how price varies across airlines, routes, stops, and booking time")
    st.markdown("---")

    # ── Filters ────────────────────────────────
    st.subheader("Filters")

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        df_opt = run_query("SELECT DISTINCT airline FROM flight")
        airline = st.multiselect("Airline", df_opt["airline"].unique(), key="pa_airline")
    with fc2:
        df_opt = run_query("SELECT DISTINCT source_city FROM flight")
        source = st.multiselect("Source City", df_opt["source_city"].unique(), key="pa_source")
    with fc3:
        df_opt = run_query("SELECT DISTINCT destination_city FROM flight")
        destination = st.multiselect("Destination City", df_opt["destination_city"].unique(), key="pa_destination")
    with fc4:
        df_opt = run_query("SELECT DISTINCT departure_time FROM flight")
        departure_time = st.multiselect("Departure Time", df_opt["departure_time"].unique(), key="pa_departure")

    fc5, fc6, fc7, fc8 = st.columns(4)
    with fc5:
        df_opt = run_query("SELECT DISTINCT stops FROM flight")
        stops = st.multiselect("Stops", df_opt["stops"].unique(), key="pa_stops")
    with fc6:
        df_opt = run_query("SELECT DISTINCT arrival_time FROM flight")
        arrival_time = st.multiselect("Arrival Time", df_opt["arrival_time"].unique(), key="pa_arrival")
    with fc7:
        df_opt = run_query("SELECT DISTINCT class FROM flight")
        flight_class = st.multiselect("Class", df_opt["class"].unique(), key="pa_class")
    with fc8:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Filters", key="pa_clear"):
            for k in ["pa_airline","pa_source","pa_destination","pa_departure",
                      "pa_stops","pa_arrival","pa_class"]:
                st.session_state[k] = []
            st.rerun()

    st.markdown("---")

    # ── Build WHERE ────────────────────────────
    wh = build_where({
        "airline":           airline,
        "source_city":       source,
        "destination_city":  destination,
        "departure_time":    departure_time,
        "stops":             stops,
        "arrival_time":      arrival_time,
        "class":             flight_class,
    })

    # ── Charts ─────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Price Distribution by Airline")
        df = run_query(f"SELECT airline, price FROM flight {wh}")
        fig, ax = styled_fig(7, 4)
        sns.boxplot(x=df["airline"], y=df["price"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Airline", fontsize=10)
        ax.set_ylabel("Price (₹)", fontsize=10)
        plt.xticks(rotation=30, ha="right", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown("##### Overall Price Distribution")
        df = run_query(f"SELECT price FROM flight {wh}")
        fig, ax = styled_fig(7, 4)
        sns.histplot(x=df["price"], bins=30, kde=True, color=PALETTE[0], ax=ax)
        ax.set_xlabel("Price (₹)", fontsize=10)
        ax.set_ylabel("Count", fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("##### Avg Price by Number of Stops")
        df = run_query(f"""
            SELECT stops, ROUND(AVG(price)) AS avg_price
            FROM flight {wh}
            GROUP BY stops
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["stops"], y=df["avg_price"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Stops", fontsize=10)
        ax.set_ylabel("Avg Price (₹)", fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)

    with col4:
        st.markdown("##### Duration vs Price")
        df = run_query(f"SELECT duration, price FROM flight {wh}")
        fig, ax = styled_fig(7, 4)
        sns.scatterplot(x=df["duration"], y=df["price"], alpha=0.4,
                        color=PALETTE[0], ax=ax)
        ax.set_xlabel("Duration (hrs)", fontsize=10)
        ax.set_ylabel("Price (₹)", fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)

    # Days Left line chart — Economy vs Business
    st.markdown("##### Avg Price vs Days Left (Economy vs Business)")

    filters_base = {
        "airline":           airline,
        "source_city":       source,
        "destination_city":  destination,
        "departure_time":    departure_time,
        "stops":             stops,
        "arrival_time":      arrival_time,
    }

    fig, ax = styled_fig(12, 4)

    if not flight_class or "Economy" in flight_class:
        eco_wh = build_where({**filters_base, "class": ["Economy"]})
        df1 = run_query(f"""
            SELECT days_left, AVG(price) AS avg_price
            FROM flight {eco_wh}
            GROUP BY days_left ORDER BY days_left
        """)
        sns.lineplot(x=df1["days_left"], y=df1["avg_price"],
                     label="Economy", color=PALETTE[0], linewidth=2, ax=ax)

    if not flight_class or "Business" in flight_class:
        bus_wh = build_where({**filters_base, "class": ["Business"]})
        df2 = run_query(f"""
            SELECT days_left, AVG(price) AS avg_price
            FROM flight {bus_wh}
            GROUP BY days_left ORDER BY days_left
        """)
        sns.lineplot(x=df2["days_left"], y=df2["avg_price"],
                     label="Business", color=PALETTE[2], linewidth=2, ax=ax)

    ax.set_xlabel("Days Left to Departure", fontsize=10)
    ax.set_ylabel("Avg Price (₹)", fontsize=10)
    ax.legend(facecolor="#1e2535", edgecolor="#2a3550", labelcolor="#c5cde8")
    plt.tight_layout()
    st.pyplot(fig)

    # Route heatmap
    st.markdown("##### Avg Price: Source × Destination Heatmap")
    df = run_query(f"""
        SELECT source_city, destination_city, ROUND(AVG(price)) AS avg_price
        FROM flight {wh}
        GROUP BY source_city, destination_city
    """)
    pivot_df = pd.pivot(data=df, index="source_city",
                        columns="destination_city", values="avg_price")
    fig, ax = styled_fig(10, 5)
    sns.heatmap(pivot_df, annot=True, fmt=".0f", cmap="Blues",
                linewidths=0.5, ax=ax)
    plt.tight_layout()
    st.pyplot(fig)


# ══════════════════════════════════════════════
#  PAGE 3 — ROUTE & CITY
# ══════════════════════════════════════════════
elif page == "✈️ Route & City":

    st.title("✈️ Route & City Analysis")
    st.caption("Which routes are busiest, most expensive, and longest?")
    st.markdown("---")

    # Flight count heatmap
    st.markdown("##### Number of Flights: Source × Destination")
    df = run_query("""
        SELECT source_city, destination_city, COUNT(*) AS count
        FROM flight
        GROUP BY source_city, destination_city
    """)
    pivot_df = pd.pivot(data=df, index="source_city",
                        columns="destination_city", values="count")
    fig, ax = styled_fig(10, 5)
    sns.heatmap(pivot_df, annot=True, fmt=".0f", cmap="YlOrBr",
                linewidths=0.5, ax=ax)
    plt.tight_layout()
    st.pyplot(fig)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Top 10 Routes by Avg Price")
        df = run_query("""
            SELECT ROUND(AVG(price)) AS avg_price,
                   CONCAT(source_city, ' → ', destination_city) AS route
            FROM flight
            GROUP BY source_city, destination_city
            ORDER BY avg_price DESC LIMIT 10
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["avg_price"], y=df["route"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Avg Price (₹)", fontsize=10)
        ax.set_ylabel("")
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown("##### Top 10 Routes by Flight Count")
        df = run_query("""
            SELECT COUNT(*) AS count,
                   CONCAT(source_city, ' → ', destination_city) AS route
            FROM flight
            GROUP BY source_city, destination_city
            ORDER BY count DESC LIMIT 10
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["count"], y=df["route"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Number of Flights", fontsize=10)
        ax.set_ylabel("")
        plt.tight_layout()
        st.pyplot(fig)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("##### Avg Duration per Route")
        df = run_query("""
            SELECT FLOOR(AVG(duration)) AS avg_duration,
                   CONCAT(source_city, ' → ', destination_city) AS route
            FROM flight
            GROUP BY source_city, destination_city
            ORDER BY avg_duration DESC
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["route"], y=df["avg_duration"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Route", fontsize=10)
        ax.set_ylabel("Avg Duration (hrs)", fontsize=10)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)

    with col4:
        st.markdown("##### Stops Breakdown")
        df = run_query("""
            SELECT stops, COUNT(*) AS count
            FROM flight
            GROUP BY stops
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["stops"], y=df["count"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Stops", fontsize=10)
        ax.set_ylabel("Number of Flights", fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)


# ══════════════════════════════════════════════
#  PAGE 4 — TIME PATTERNS
# ══════════════════════════════════════════════
elif page == "🕐 Time Patterns":

    st.title("🕐 Time Patterns")
    st.caption("When do people fly, and does timing affect price?")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Flights by Departure Time Slot")
        df = run_query("""
            SELECT departure_time, COUNT(*) AS count
            FROM flight GROUP BY departure_time
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["departure_time"], y=df["count"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Departure Time", fontsize=10)
        ax.set_ylabel("Flights", fontsize=10)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown("##### Avg Price by Departure Time Slot")
        df = run_query("""
            SELECT departure_time, ROUND(AVG(price)) AS avg_price
            FROM flight GROUP BY departure_time
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["departure_time"], y=df["avg_price"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Departure Time", fontsize=10)
        ax.set_ylabel("Avg Price (₹)", fontsize=10)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("##### Departure × Arrival Time — Flight Count Heatmap")
    df = run_query("""
        SELECT departure_time, arrival_time, COUNT(*) AS count
        FROM flight GROUP BY departure_time, arrival_time
    """)
    pivot_df = pd.pivot(data=df, index="departure_time",
                        columns="arrival_time", values="count")
    fig, ax = styled_fig(10, 5)
    sns.heatmap(pivot_df, annot=True, fmt=".0f", cmap="Blues",
                linewidths=0.5, ax=ax)
    plt.tight_layout()
    st.pyplot(fig)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("##### Avg Price by Arrival Time Slot")
        df = run_query("""
            SELECT arrival_time, ROUND(AVG(price)) AS avg_price
            FROM flight GROUP BY arrival_time
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["arrival_time"], y=df["avg_price"], palette=PALETTE, ax=ax)
        ax.set_xlabel("Arrival Time", fontsize=10)
        ax.set_ylabel("Avg Price (₹)", fontsize=10)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

    with col4:
        st.markdown("##### Departure Time Breakdown per Airline")
        df = run_query("""
            SELECT COUNT(*) AS count,
                   CONCAT(airline, ' — ', departure_time) AS airline_time
            FROM flight
            GROUP BY departure_time, airline
        """)
        fig, ax = styled_fig(7, 4)
        sns.barplot(x=df["airline_time"], y=df["count"], palette=PALETTE, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("Flights", fontsize=10)
        plt.xticks(rotation=45, ha="right", fontsize=7)
        plt.tight_layout()
        st.pyplot(fig)


# ══════════════════════════════════════════════
#  PAGE 5 — AIRLINE COMPARISON
# ══════════════════════════════════════════════
elif page == "🏢 Airline Comparison":

    st.title("🏢 Airline Comparison")
    st.caption("Head-to-head comparison across price, duration, class split, and market share")
    st.markdown("---")

    # Radar chart
    st.markdown("##### Multi-Metric Airline Comparison (Radar)")
    df = run_query("""
        SELECT airline,
               AVG(price)                                                    AS avg_price,
               CEIL(AVG(duration))                                           AS avg_duration,
               COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flight)              AS percentage_share,
               COUNT(*)                                                      AS flight_count,
               SUM(CASE WHEN class = 'Economy'  THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS economy_pct,
               SUM(CASE WHEN class = 'Business' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS business_pct
        FROM flight
        GROUP BY airline
    """)
    cols = ["avg_price", "avg_duration", "percentage_share",
            "flight_count", "economy_pct", "business_pct"]
    df_norm = df.copy()
    for col in cols:
        df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    df_long = df_norm.melt(id_vars="airline", var_name="category", value_name="value")
    fig = px.line_polar(df_long, r="value", theta="category",
                        color="airline", line_close=True,
                        color_discrete_sequence=PALETTE)
    fig.update_traces(fill="toself", opacity=0.7)
    fig.update_layout(**PLOTLY_THEME, margin=dict(t=30, b=30))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Stops Distribution per Airline")
        df = run_query("""
            SELECT airline, stops, COUNT(*) AS no_of_flights
            FROM flight GROUP BY airline, stops
        """)
        pivot_df = pd.pivot(data=df, index="airline",
                            columns="stops", values="no_of_flights")
        fig, ax = styled_fig(7, 4)
        pivot_df.plot(kind="bar", stacked=True,
                      color=PALETTE[:len(pivot_df.columns)], ax=ax)
        ax.set_xlabel("Airline", fontsize=10)
        ax.set_ylabel("Flights", fontsize=10)
        ax.legend(facecolor="#1e2535", edgecolor="#2a3550", labelcolor="#c5cde8")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown("##### Economy vs Business Split per Airline")
        df = run_query("""
            SELECT class, airline, COUNT(*) AS no_of_flights
            FROM flight GROUP BY class, airline
        """)
        pivot_df = pd.pivot(data=df, index="airline",
                            columns="class", values="no_of_flights")
        fig, ax = styled_fig(7, 4)
        pivot_df.plot(kind="bar",
                      color=PALETTE[:len(pivot_df.columns)], ax=ax)
        ax.set_xlabel("Airline", fontsize=10)
        ax.set_ylabel("Flights", fontsize=10)
        ax.legend(facecolor="#1e2535", edgecolor="#2a3550", labelcolor="#c5cde8")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")
    st.markdown("##### Avg Duration per Airline")
    df = run_query("""
        SELECT airline, AVG(duration) AS avg_duration
        FROM flight GROUP BY airline
    """)
    fig, ax = styled_fig(10, 4)
    sns.barplot(x=df["airline"], y=df["avg_duration"], palette=PALETTE, ax=ax)
    ax.set_xlabel("Airline", fontsize=10)
    ax.set_ylabel("Avg Duration (hrs)", fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")
    st.markdown("##### 📊 Airline Summary Table")
    df = run_query("""
        SELECT airline,
               COUNT(*)                                                            AS total_flights,
               ROUND(AVG(price))                                                   AS avg_price,
               FLOOR(AVG(duration))                                                AS avg_duration,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flight), 2)          AS market_share_pct,
               ROUND(SUM(CASE WHEN class='Economy'  THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS economy_pct,
               ROUND(SUM(CASE WHEN class='Business' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS business_pct,
               MAX(price)                                                           AS max_price,
               MIN(price)                                                           AS min_price
        FROM flight
        GROUP BY airline
    """)
    df = df.rename(columns={
        "airline":          "Airline",
        "total_flights":    "Total Flights",
        "avg_price":        "Avg Price (₹)",
        "avg_duration":     "Avg Duration (hrs)",
        "market_share_pct": "Market Share %",
        "economy_pct":      "Economy %",
        "business_pct":     "Business %",
        "max_price":        "Max Price (₹)",
        "min_price":        "Min Price (₹)",
    })
    st.dataframe(df, use_container_width=True)


# ══════════════════════════════════════════════
#  PAGE 6 — DATA EXPLORER
# ══════════════════════════════════════════════
elif page == "🔍 Data Explorer":

    st.title("🔍 Data Explorer")
    st.caption("Filter, explore, and download the raw flight data")
    st.markdown("---")

    st.subheader("Filters")

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        df_opt = run_query("SELECT DISTINCT airline FROM flight")
        airline = st.multiselect("Airline", df_opt["airline"].unique(), key="de_airline")
    with fc2:
        df_opt = run_query("SELECT DISTINCT source_city FROM flight")
        source = st.multiselect("Source City", df_opt["source_city"].unique(), key="de_source")
    with fc3:
        df_opt = run_query("SELECT DISTINCT destination_city FROM flight")
        destination = st.multiselect("Destination City", df_opt["destination_city"].unique(), key="de_destination")
    with fc4:
        df_opt = run_query("SELECT DISTINCT departure_time FROM flight")
        departure_time = st.multiselect("Departure Time", df_opt["departure_time"].unique(), key="de_departure")

    fc5, fc6, fc7, fc8 = st.columns(4)
    with fc5:
        df_opt = run_query("SELECT DISTINCT stops FROM flight")
        stops = st.multiselect("Stops", df_opt["stops"].unique(), key="de_stops")
    with fc6:
        df_opt = run_query("SELECT DISTINCT arrival_time FROM flight")
        arrival_time = st.multiselect("Arrival Time", df_opt["arrival_time"].unique(), key="de_arrival")
    with fc7:
        df_opt = run_query("SELECT DISTINCT class FROM flight")
        flight_class = st.multiselect("Class", df_opt["class"].unique(), key="de_class")
    with fc8:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Filters", key="de_clear"):
            for k in ["de_airline","de_source","de_destination","de_departure",
                      "de_stops","de_arrival","de_class"]:
                st.session_state[k] = []
            max_p = int(run_query("SELECT MAX(price) FROM flight").iloc[0,0])
            min_p = int(run_query("SELECT MIN(price) FROM flight").iloc[0,0])
            max_d = int(run_query("SELECT MAX(days_left) FROM flight").iloc[0,0])
            min_d = int(run_query("SELECT MIN(days_left) FROM flight").iloc[0,0])
            st.session_state["de_price"] = (min_p, max_p)
            st.session_state["de_days"]  = (min_d, max_d)
            st.rerun()

    sl1, sl2 = st.columns(2)
    with sl1:
        max_p = int(run_query("SELECT MAX(price) FROM flight").iloc[0, 0])
        min_p = int(run_query("SELECT MIN(price) FROM flight").iloc[0, 0])
        price_range = st.slider("Price Range (₹)", min_value=min_p, max_value=max_p,
                                 value=(min_p, max_p), key="de_price")
    with sl2:
        max_d = int(run_query("SELECT MAX(days_left) FROM flight").iloc[0, 0])
        min_d = int(run_query("SELECT MIN(days_left) FROM flight").iloc[0, 0])
        days_range = st.slider("Days Left to Departure", min_value=min_d, max_value=max_d,
                                value=(min_d, max_d), key="de_days")

    st.markdown("---")

    # Build WHERE
    wh = build_where({
        "airline":           airline,
        "source_city":       source,
        "destination_city":  destination,
        "departure_time":    departure_time,
        "stops":             stops,
        "arrival_time":      arrival_time,
        "class":             flight_class,
        "price":             price_range,
        "days_left":         days_range,
    })

    df = run_query(f"SELECT * FROM flight {wh}")

    # Summary mini-metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Flights Found",   f"{len(df):,}")
    m2.metric("Avg Price",       f"₹{int(df['price'].mean()):,}"    if len(df) else "—")
    m3.metric("Min Price",       f"₹{int(df['price'].min()):,}"     if len(df) else "—")
    m4.metric("Max Price",       f"₹{int(df['price'].max()):,}"     if len(df) else "—")

    st.markdown("---")
    st.dataframe(df, use_container_width=True)

    data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Filtered Data as CSV",
        data=data,
        file_name="flights_filtered.csv",
        mime="text/csv",
    )


# import streamlit as st
# from db import run_query
# import seaborn as sns
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# import plotly.express as px
# import pandas as pd

# # ─────────────────────────────────────────────
# #  PAGE CONFIG
# # ─────────────────────────────────────────────
# st.set_page_config(
#     page_title="Airlines Dashboard",
#     layout="wide",
#     page_icon="✈️"
# )

# # ─────────────────────────────────────────────
# #  GLOBAL STYLE
# # ─────────────────────────────────────────────
# st.markdown("""
# <style>
#     @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

#     html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

#     .stApp { background-color: #0f1117; color: #e8eaf0; }

#     [data-testid="stSidebar"] {
#         background-color: #161b27;
#         border-right: 1px solid #1e2535;
#     }

#     [data-testid="stMetric"] {
#         background: linear-gradient(135deg, #1a2035, #1e2840);
#         border: 1px solid #2a3550;
#         border-radius: 12px;
#         padding: 16px 20px;
#     }
#     [data-testid="stMetricLabel"] { color: #7b8db0 !important; font-size: 12px; }
#     [data-testid="stMetricValue"] { color: #e8eaf0 !important; font-size: 24px; font-weight: 600; }

#     h1 { color: #ffffff !important; font-weight: 600; letter-spacing: -0.5px; }
#     h2 { color: #c5cde8 !important; font-weight: 500; }
#     h3 { color: #a0aec8 !important; font-weight: 500; font-size: 15px; }

#     hr { border-color: #1e2535 !important; }

#     [data-baseweb="tag"] {
#         background-color: #2a4080 !important;
#         border-radius: 6px !important;
#     }

#     .stButton > button {
#         background: linear-gradient(135deg, #2a4080, #1e5fa8);
#         color: white;
#         border: none;
#         border-radius: 8px;
#         padding: 8px 20px;
#         font-family: 'DM Sans', sans-serif;
#         font-size: 13px;
#         transition: opacity 0.2s;
#     }
#     .stButton > button:hover { opacity: 0.85; }

#     .insight-card {
#         background: linear-gradient(135deg, #1a2035, #1a2840);
#         border: 1px solid #2a3550;
#         border-left: 3px solid #3a7bd5;
#         border-radius: 10px;
#         padding: 14px 18px;
#         margin-bottom: 10px;
#         font-size: 14px;
#         color: #c5cde8;
#         line-height: 1.6;
#     }
#     .insight-card span { color: #5ba3f5; font-weight: 600; }

#     [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
# </style>
# """, unsafe_allow_html=True)


# # ─────────────────────────────────────────────
# #  CHART HELPERS
# # ─────────────────────────────────────────────
# PALETTE = ["#3a7bd5", "#00c9a7", "#f7971e", "#e040fb", "#ff6b6b", "#4ecdc4"]

# PLOTLY_THEME = dict(
#     paper_bgcolor="#161b27",
#     plot_bgcolor="#161b27",
#     font=dict(color="#c5cde8", family="DM Sans"),
#     colorway=PALETTE,
# )

# def set_chart_style():
#     """Apply dark theme to all matplotlib/seaborn charts."""
#     mpl.rcParams.update({
#         "figure.facecolor": "#161b27",
#         "axes.facecolor":   "#161b27",
#         "axes.edgecolor":   "#2a3550",
#         "axes.labelcolor":  "#7b8db0",
#         "xtick.color":      "#7b8db0",
#         "ytick.color":      "#7b8db0",
#         "grid.color":       "#1e2535",
#         "grid.linestyle":   "--",
#         "grid.alpha":       0.5,
#         "text.color":       "#c5cde8",
#         "font.family":      "DejaVu Sans",
#     })
#     # Set palette globally — avoids passing palette= per chart (deprecated in newer seaborn)
#     sns.set_palette(PALETTE)

# def styled_fig(w=8, h=4):
#     """Return a dark-themed (fig, ax) pair."""
#     set_chart_style()
#     fig, ax = plt.subplots(figsize=(w, h))
#     ax.grid(axis="y", alpha=0.3)
#     return fig, ax


# # ─────────────────────────────────────────────
# #  WHERE CLAUSE BUILDER
# # ─────────────────────────────────────────────
# def build_where(filters: dict) -> str:
#     """
#     Build a SQL WHERE clause from a filters dict.

#     Supported keys:
#         airline, source_city, destination_city, departure_time,
#         stops, arrival_time, class  →  list of selected values
#         price, days_left            →  (min, max) tuple
#     Returns empty string if no active filters.
#     """
#     conditions = []

#     list_cols = [
#         "airline", "source_city", "destination_city",
#         "departure_time", "stops", "arrival_time", "class",
#     ]
#     for col in list_cols:
#         vals = filters.get(col, [])
#         if vals:
#             escaped = ", ".join(f"'{v}'" for v in vals)
#             conditions.append(f"{col} IN ({escaped})")

#     if "price" in filters:
#         lo, hi = filters["price"]
#         conditions.append(f"price BETWEEN {lo} AND {hi}")

#     if "days_left" in filters:
#         lo, hi = filters["days_left"]
#         conditions.append(f"days_left BETWEEN {lo} AND {hi}")

#     return ("WHERE " + " AND ".join(conditions)) if conditions else ""


# # ─────────────────────────────────────────────
# #  SIDEBAR
# # ─────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("## ✈️ Airlines Dashboard")
#     st.markdown("---")
#     page = st.radio(
#         "Navigate",
#         [
#             "🏠 Overview",
#             "💰 Price Analysis",
#             "✈️ Route & City",
#             "🕐 Time Patterns",
#             "🏢 Airline Comparison",
#             "🔍 Data Explorer",
#         ],
#         label_visibility="collapsed",
#     )
#     st.markdown("---")
#     st.success("🟢 Database Connected")
#     st.caption("Indian Airline Flights Dataset")


# # ══════════════════════════════════════════════
# #  PAGE 1 — OVERVIEW
# # ══════════════════════════════════════════════
# if page == "🏠 Overview":

#     st.title("🏠 Overview")
#     st.caption("High-level summary of the entire flight dataset")
#     st.markdown("---")

#     # KPI Cards
#     st.subheader("Key Metrics")
#     c1, c2, c3, c4, c5, c6 = st.columns(6)

#     with c1:
#         val = run_query("SELECT COUNT(*) FROM flight").iloc[0, 0]
#         st.metric("Total Flights", f"{val:,}")
#     with c2:
#         val = run_query("SELECT COUNT(DISTINCT airline) FROM flight").iloc[0, 0]
#         st.metric("Airlines", val)
#     with c3:
#         val = run_query("SELECT ROUND(AVG(price)) FROM flight").iloc[0, 0]
#         st.metric("Avg Ticket Price", f"₹{val:,}")
#     with c4:
#         val = run_query("SELECT MAX(price) FROM flight").iloc[0, 0]
#         st.metric("Most Expensive", f"₹{val:,}")
#     with c5:
#         val = run_query("SELECT MIN(price) FROM flight").iloc[0, 0]
#         st.metric("Cheapest Ticket", f"₹{val:,}")
#     with c6:
#         val = run_query("SELECT ROUND(AVG(duration)) FROM flight").iloc[0, 0]
#         st.metric("Avg Duration (hrs)", val)

#     st.markdown("---")

#     # Insights
#     st.subheader("📌 Key Insights")
#     insights = [
#         ("Business class tickets cost roughly <span>3–5× more</span> than Economy — "
#          "yet only a small fraction of travellers book them, making Economy the true "
#          "volume driver for every airline."),

#         ("Prices <span>drop sharply when booked 30+ days early</span>. "
#          "Last-minute bookings (under 7 days) can be 40–60% more expensive — "
#          "booking early is the single biggest money-saving lever."),

#         ("<span>Vistara and Air India</span> consistently command the highest average fares, "
#          "while IndiGo and SpiceJet anchor the budget end — "
#          "reflecting their distinct positioning in the Indian market."),

#         ("Routes involving <span>Mumbai and Delhi</span> dominate both flight count and revenue, "
#          "confirming these two metros as the backbone of domestic air travel in India."),

#         ("Flights with <span>zero stops</span> are priced higher on average than one-stop flights "
#          "— travellers pay a clear premium for convenience, not just distance."),
#     ]
#     for text in insights:
#         st.markdown(f'<div class="insight-card">💡 {text}</div>', unsafe_allow_html=True)

#     st.markdown("---")

#     # Charts
#     st.subheader("Flight Distribution")
#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown("##### Total Flights per Route")
#         df = run_query("""
#             SELECT CONCAT(source_city, ' → ', destination_city) AS route,
#                    COUNT(*) AS no_of_flights
#             FROM flight
#             GROUP BY source_city, destination_city
#             ORDER BY no_of_flights DESC
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="route", y="no_of_flights", data=df, ax=ax)
#         ax.set_xlabel("Route", fontsize=10)
#         ax.set_ylabel("Flights", fontsize=10)
#         plt.xticks(rotation=45, ha="right", fontsize=8)
#         plt.tight_layout()
#         st.pyplot(fig)

#     with col2:
#         st.markdown("##### Avg Price by Airline")
#         df = run_query("""
#             SELECT airline, ROUND(AVG(price)) AS price
#             FROM flight
#             GROUP BY airline
#             ORDER BY price DESC
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="airline", y="price", data=df, ax=ax)
#         ax.set_xlabel("Airline", fontsize=10)
#         ax.set_ylabel("Avg Price (₹)", fontsize=10)
#         plt.xticks(rotation=30, ha="right", fontsize=9)
#         plt.tight_layout()
#         st.pyplot(fig)

#     col3, col4 = st.columns(2)

#     with col3:
#         st.markdown("##### Avg Price vs Days Left to Departure")
#         df = run_query("""
#             SELECT days_left, ROUND(AVG(price)) AS price
#             FROM flight
#             GROUP BY days_left
#             ORDER BY days_left
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.lineplot(x="days_left", y="price", data=df,
#                      color=PALETTE[0], linewidth=2, ax=ax)
#         ax.set_xlabel("Days Left", fontsize=10)
#         ax.set_ylabel("Avg Price (₹)", fontsize=10)
#         plt.tight_layout()
#         st.pyplot(fig)

#     with col4:
#         st.markdown("##### Market Share by Airline")
#         df = run_query("""
#             SELECT airline,
#                    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flight) AS percentage_share
#             FROM flight
#             GROUP BY airline
#         """)
#         fig = px.pie(df, names="airline", values="percentage_share",
#                      color_discrete_sequence=PALETTE, hole=0.4)
#         fig.update_layout(**PLOTLY_THEME, margin=dict(t=10, b=10, l=10, r=10))
#         st.plotly_chart(fig, use_container_width=True)


# # ══════════════════════════════════════════════
# #  PAGE 2 — PRICE ANALYSIS
# # ══════════════════════════════════════════════
# elif page == "💰 Price Analysis":

#     st.title("💰 Price Analysis")
#     st.caption("Explore how price varies across airlines, routes, stops, and booking time")
#     st.markdown("---")

#     # Filters
#     st.subheader("Filters")
#     fc1, fc2, fc3, fc4 = st.columns(4)
#     with fc1:
#         airline = st.multiselect("Airline",
#             run_query("SELECT DISTINCT airline FROM flight")["airline"].unique(),
#             key="pa_airline")
#     with fc2:
#         source = st.multiselect("Source City",
#             run_query("SELECT DISTINCT source_city FROM flight")["source_city"].unique(),
#             key="pa_source")
#     with fc3:
#         destination = st.multiselect("Destination City",
#             run_query("SELECT DISTINCT destination_city FROM flight")["destination_city"].unique(),
#             key="pa_destination")
#     with fc4:
#         departure_time = st.multiselect("Departure Time",
#             run_query("SELECT DISTINCT departure_time FROM flight")["departure_time"].unique(),
#             key="pa_departure")

#     fc5, fc6, fc7, fc8 = st.columns(4)
#     with fc5:
#         stops = st.multiselect("Stops",
#             run_query("SELECT DISTINCT stops FROM flight")["stops"].unique(),
#             key="pa_stops")
#     with fc6:
#         arrival_time = st.multiselect("Arrival Time",
#             run_query("SELECT DISTINCT arrival_time FROM flight")["arrival_time"].unique(),
#             key="pa_arrival")
#     with fc7:
#         flight_class = st.multiselect("Class",
#             run_query("SELECT DISTINCT class FROM flight")["class"].unique(),
#             key="pa_class")
#     with fc8:
#         st.markdown("<br>", unsafe_allow_html=True)
#         if st.button("🗑️ Clear Filters", key="pa_clear"):
#             for k in ["pa_airline", "pa_source", "pa_destination", "pa_departure",
#                       "pa_stops", "pa_arrival", "pa_class"]:
#                 st.session_state[k] = []
#             st.rerun()

#     st.markdown("---")

#     # Build WHERE clause
#     wh = build_where({
#         "airline":           airline,
#         "source_city":       source,
#         "destination_city":  destination,
#         "departure_time":    departure_time,
#         "stops":             stops,
#         "arrival_time":      arrival_time,
#         "class":             flight_class,
#     })

#     # Charts
#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown("##### Price Distribution by Airline")
#         df = run_query(f"SELECT airline, price FROM flight {wh}")
#         fig, ax = styled_fig(7, 4)
#         sns.boxplot(x="airline", y="price", data=df, ax=ax)
#         ax.set_xlabel("Airline", fontsize=10)
#         ax.set_ylabel("Price (₹)", fontsize=10)
#         plt.xticks(rotation=30, ha="right", fontsize=9)
#         plt.tight_layout()
#         st.pyplot(fig)

#     with col2:
#         st.markdown("##### Overall Price Distribution")
#         df = run_query(f"SELECT price FROM flight {wh}")
#         fig, ax = styled_fig(7, 4)
#         sns.histplot(x="price", data=df, bins=30, kde=True, color=PALETTE[0], ax=ax)
#         ax.set_xlabel("Price (₹)", fontsize=10)
#         ax.set_ylabel("Count", fontsize=10)
#         plt.tight_layout()
#         st.pyplot(fig)

#     col3, col4 = st.columns(2)

#     with col3:
#         st.markdown("##### Avg Price by Number of Stops")
#         df = run_query(f"""
#             SELECT stops, ROUND(AVG(price)) AS avg_price
#             FROM flight {wh}
#             GROUP BY stops
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="stops", y="avg_price", data=df, ax=ax)
#         ax.set_xlabel("Stops", fontsize=10)
#         ax.set_ylabel("Avg Price (₹)", fontsize=10)
#         plt.tight_layout()
#         st.pyplot(fig)

#     with col4:
#         st.markdown("##### Duration vs Price")
#         df = run_query(f"SELECT duration, price FROM flight {wh}")
#         fig, ax = styled_fig(7, 4)
#         sns.scatterplot(x="duration", y="price", data=df,
#                         alpha=0.4, color=PALETTE[0], ax=ax)
#         ax.set_xlabel("Duration (hrs)", fontsize=10)
#         ax.set_ylabel("Price (₹)", fontsize=10)
#         plt.tight_layout()
#         st.pyplot(fig)

#     # Days Left — Economy vs Business line chart
#     st.markdown("##### Avg Price vs Days Left (Economy vs Business)")

#     # base filters without class — class handled separately per line
#     filters_base = {
#         "airline":           airline,
#         "source_city":       source,
#         "destination_city":  destination,
#         "departure_time":    departure_time,
#         "stops":             stops,
#         "arrival_time":      arrival_time,
#     }

#     fig, ax = styled_fig(12, 4)

#     if not flight_class or "Economy" in flight_class:
#         eco_wh = build_where({**filters_base, "class": ["Economy"]})
#         df1 = run_query(f"""
#             SELECT days_left, AVG(price) AS avg_price
#             FROM flight {eco_wh}
#             GROUP BY days_left ORDER BY days_left
#         """)
#         sns.lineplot(x="days_left", y="avg_price", data=df1,
#                      label="Economy", color=PALETTE[0], linewidth=2, ax=ax)

#     if not flight_class or "Business" in flight_class:
#         bus_wh = build_where({**filters_base, "class": ["Business"]})
#         df2 = run_query(f"""
#             SELECT days_left, AVG(price) AS avg_price
#             FROM flight {bus_wh}
#             GROUP BY days_left ORDER BY days_left
#         """)
#         sns.lineplot(x="days_left", y="avg_price", data=df2,
#                      label="Business", color=PALETTE[2], linewidth=2, ax=ax)

#     ax.set_xlabel("Days Left to Departure", fontsize=10)
#     ax.set_ylabel("Avg Price (₹)", fontsize=10)
#     ax.legend(facecolor="#1e2535", edgecolor="#2a3550", labelcolor="#c5cde8")
#     plt.tight_layout()
#     st.pyplot(fig)

#     # Route price heatmap
#     st.markdown("##### Avg Price: Source × Destination Heatmap")
#     df = run_query(f"""
#         SELECT source_city, destination_city, ROUND(AVG(price)) AS avg_price
#         FROM flight {wh}
#         GROUP BY source_city, destination_city
#     """)
#     pivot_df = pd.pivot(data=df, index="source_city",
#                         columns="destination_city", values="avg_price")
#     fig, ax = styled_fig(10, 5)
#     sns.heatmap(pivot_df, annot=True, fmt=".0f", cmap="Blues",
#                 linewidths=0.5, ax=ax)
#     plt.tight_layout()
#     st.pyplot(fig)


# # ══════════════════════════════════════════════
# #  PAGE 3 — ROUTE & CITY
# # ══════════════════════════════════════════════
# elif page == "✈️ Route & City":

#     st.title("✈️ Route & City Analysis")
#     st.caption("Which routes are busiest, most expensive, and longest?")
#     st.markdown("---")

#     st.markdown("##### Number of Flights: Source × Destination")
#     df = run_query("""
#         SELECT source_city, destination_city, COUNT(*) AS count
#         FROM flight
#         GROUP BY source_city, destination_city
#     """)
#     pivot_df = pd.pivot(data=df, index="source_city",
#                         columns="destination_city", values="count")
#     fig, ax = styled_fig(10, 5)
#     sns.heatmap(pivot_df, annot=True, fmt=".0f", cmap="YlOrBr",
#                 linewidths=0.5, ax=ax)
#     plt.tight_layout()
#     st.pyplot(fig)

#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown("##### Top 10 Routes by Avg Price")
#         df = run_query("""
#             SELECT ROUND(AVG(price)) AS avg_price,
#                    CONCAT(source_city, ' → ', destination_city) AS route
#             FROM flight
#             GROUP BY source_city, destination_city
#             ORDER BY avg_price DESC LIMIT 10
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="avg_price", y="route", data=df, ax=ax)
#         ax.set_xlabel("Avg Price (₹)", fontsize=10)
#         ax.set_ylabel("")
#         plt.tight_layout()
#         st.pyplot(fig)

#     with col2:
#         st.markdown("##### Top 10 Routes by Flight Count")
#         df = run_query("""
#             SELECT COUNT(*) AS count,
#                    CONCAT(source_city, ' → ', destination_city) AS route
#             FROM flight
#             GROUP BY source_city, destination_city
#             ORDER BY count DESC LIMIT 10
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="count", y="route", data=df, ax=ax)
#         ax.set_xlabel("Number of Flights", fontsize=10)
#         ax.set_ylabel("")
#         plt.tight_layout()
#         st.pyplot(fig)

#     col3, col4 = st.columns(2)

#     with col3:
#         st.markdown("##### Avg Duration per Route")
#         df = run_query("""
#             SELECT FLOOR(AVG(duration)) AS avg_duration,
#                    CONCAT(source_city, ' → ', destination_city) AS route
#             FROM flight
#             GROUP BY source_city, destination_city
#             ORDER BY avg_duration DESC
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="route", y="avg_duration", data=df, ax=ax)
#         ax.set_xlabel("Route", fontsize=10)
#         ax.set_ylabel("Avg Duration (hrs)", fontsize=10)
#         plt.xticks(rotation=45, ha="right", fontsize=8)
#         plt.tight_layout()
#         st.pyplot(fig)

#     with col4:
#         st.markdown("##### Stops Breakdown")
#         df = run_query("SELECT stops, COUNT(*) AS count FROM flight GROUP BY stops")
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="stops", y="count", data=df, ax=ax)
#         ax.set_xlabel("Stops", fontsize=10)
#         ax.set_ylabel("Number of Flights", fontsize=10)
#         plt.tight_layout()
#         st.pyplot(fig)


# # ══════════════════════════════════════════════
# #  PAGE 4 — TIME PATTERNS
# # ══════════════════════════════════════════════
# elif page == "🕐 Time Patterns":

#     st.title("🕐 Time Patterns")
#     st.caption("When do people fly, and does timing affect price?")
#     st.markdown("---")

#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown("##### Flights by Departure Time Slot")
#         df = run_query("SELECT departure_time, COUNT(*) AS count FROM flight GROUP BY departure_time")
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="departure_time", y="count", data=df, ax=ax)
#         ax.set_xlabel("Departure Time", fontsize=10)
#         ax.set_ylabel("Flights", fontsize=10)
#         plt.xticks(rotation=30, ha="right")
#         plt.tight_layout()
#         st.pyplot(fig)

#     with col2:
#         st.markdown("##### Avg Price by Departure Time Slot")
#         df = run_query("""
#             SELECT departure_time, ROUND(AVG(price)) AS avg_price
#             FROM flight GROUP BY departure_time
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="departure_time", y="avg_price", data=df, ax=ax)
#         ax.set_xlabel("Departure Time", fontsize=10)
#         ax.set_ylabel("Avg Price (₹)", fontsize=10)
#         plt.xticks(rotation=30, ha="right")
#         plt.tight_layout()
#         st.pyplot(fig)

#     st.markdown("##### Departure × Arrival Time — Flight Count Heatmap")
#     df = run_query("""
#         SELECT departure_time, arrival_time, COUNT(*) AS count
#         FROM flight GROUP BY departure_time, arrival_time
#     """)
#     pivot_df = pd.pivot(data=df, index="departure_time",
#                         columns="arrival_time", values="count")
#     fig, ax = styled_fig(10, 5)
#     sns.heatmap(pivot_df, annot=True, fmt=".0f", cmap="Blues",
#                 linewidths=0.5, ax=ax)
#     plt.tight_layout()
#     st.pyplot(fig)

#     col3, col4 = st.columns(2)

#     with col3:
#         st.markdown("##### Avg Price by Arrival Time Slot")
#         df = run_query("""
#             SELECT arrival_time, ROUND(AVG(price)) AS avg_price
#             FROM flight GROUP BY arrival_time
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="arrival_time", y="avg_price", data=df, ax=ax)
#         ax.set_xlabel("Arrival Time", fontsize=10)
#         ax.set_ylabel("Avg Price (₹)", fontsize=10)
#         plt.xticks(rotation=30, ha="right")
#         plt.tight_layout()
#         st.pyplot(fig)

#     with col4:
#         st.markdown("##### Departure Time Breakdown per Airline")
#         df = run_query("""
#             SELECT COUNT(*) AS count,
#                    CONCAT(airline, ' — ', departure_time) AS airline_time
#             FROM flight
#             GROUP BY departure_time, airline
#         """)
#         fig, ax = styled_fig(7, 4)
#         sns.barplot(x="airline_time", y="count", data=df, ax=ax)
#         ax.set_xlabel("")
#         ax.set_ylabel("Flights", fontsize=10)
#         plt.xticks(rotation=45, ha="right", fontsize=7)
#         plt.tight_layout()
#         st.pyplot(fig)


# # ══════════════════════════════════════════════
# #  PAGE 5 — AIRLINE COMPARISON
# # ══════════════════════════════════════════════
# elif page == "🏢 Airline Comparison":

#     st.title("🏢 Airline Comparison")
#     st.caption("Head-to-head comparison across price, duration, class split, and market share")
#     st.markdown("---")

#     # Radar chart
#     st.markdown("##### Multi-Metric Airline Comparison (Radar)")
#     df = run_query("""
#         SELECT airline,
#                AVG(price)                                                              AS avg_price,
#                CEIL(AVG(duration))                                                     AS avg_duration,
#                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flight)                       AS percentage_share,
#                COUNT(*)                                                                AS flight_count,
#                SUM(CASE WHEN class = 'Economy'  THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS economy_pct,
#                SUM(CASE WHEN class = 'Business' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS business_pct
#         FROM flight
#         GROUP BY airline
#     """)
#     metric_cols = ["avg_price", "avg_duration", "percentage_share",
#                    "flight_count", "economy_pct", "business_pct"]

#     # Min-Max normalize so all metrics sit on the same 0–1 scale
#     df_norm = df.copy()
#     for col in metric_cols:
#         col_min, col_max = df[col].min(), df[col].max()
#         df_norm[col] = (df[col] - col_min) / (col_max - col_min)

#     df_long = df_norm.melt(id_vars="airline", var_name="category", value_name="value")
#     fig = px.line_polar(df_long, r="value", theta="category",
#                         color="airline", line_close=True,
#                         color_discrete_sequence=PALETTE)
#     fig.update_traces(fill="toself", opacity=0.7)
#     fig.update_layout(**PLOTLY_THEME, margin=dict(t=30, b=30))
#     st.plotly_chart(fig, use_container_width=True)

#     st.markdown("---")
#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown("##### Stops Distribution per Airline (Stacked)")
#         df = run_query("SELECT airline, stops, COUNT(*) AS no_of_flights FROM flight GROUP BY airline, stops")
#         pivot_df = pd.pivot(data=df, index="airline",
#                             columns="stops", values="no_of_flights")
#         fig, ax = styled_fig(7, 4)
#         pivot_df.plot(kind="bar", stacked=True,
#                       color=PALETTE[:len(pivot_df.columns)], ax=ax)
#         ax.set_xlabel("Airline", fontsize=10)
#         ax.set_ylabel("Flights", fontsize=10)
#         ax.legend(facecolor="#1e2535", edgecolor="#2a3550", labelcolor="#c5cde8")
#         plt.xticks(rotation=30, ha="right")
#         plt.tight_layout()
#         st.pyplot(fig)

#     with col2:
#         st.markdown("##### Economy vs Business Split per Airline")
#         df = run_query("SELECT class, airline, COUNT(*) AS no_of_flights FROM flight GROUP BY class, airline")
#         pivot_df = pd.pivot(data=df, index="airline",
#                             columns="class", values="no_of_flights")
#         fig, ax = styled_fig(7, 4)
#         pivot_df.plot(kind="bar", color=PALETTE[:len(pivot_df.columns)], ax=ax)
#         ax.set_xlabel("Airline", fontsize=10)
#         ax.set_ylabel("Flights", fontsize=10)
#         ax.legend(facecolor="#1e2535", edgecolor="#2a3550", labelcolor="#c5cde8")
#         plt.xticks(rotation=30, ha="right")
#         plt.tight_layout()
#         st.pyplot(fig)

#     st.markdown("---")
#     st.markdown("##### Avg Duration per Airline")
#     df = run_query("SELECT airline, AVG(duration) AS avg_duration FROM flight GROUP BY airline")
#     fig, ax = styled_fig(10, 4)
#     sns.barplot(x="airline", y="avg_duration", data=df, ax=ax)
#     ax.set_xlabel("Airline", fontsize=10)
#     ax.set_ylabel("Avg Duration (hrs)", fontsize=10)
#     plt.tight_layout()
#     st.pyplot(fig)

#     st.markdown("---")
#     st.markdown("##### 📊 Airline Summary Table")
#     df = run_query("""
#         SELECT airline,
#                COUNT(*)                                                                   AS total_flights,
#                ROUND(AVG(price))                                                          AS avg_price,
#                FLOOR(AVG(duration))                                                       AS avg_duration,
#                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flight), 2)                AS market_share_pct,
#                ROUND(SUM(CASE WHEN class='Economy'  THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS economy_pct,
#                ROUND(SUM(CASE WHEN class='Business' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS business_pct,
#                MAX(price)                                                                  AS max_price,
#                MIN(price)                                                                  AS min_price
#         FROM flight
#         GROUP BY airline
#     """)
#     df = df.rename(columns={
#         "airline":          "Airline",
#         "total_flights":    "Total Flights",
#         "avg_price":        "Avg Price (₹)",
#         "avg_duration":     "Avg Duration (hrs)",
#         "market_share_pct": "Market Share %",
#         "economy_pct":      "Economy %",
#         "business_pct":     "Business %",
#         "max_price":        "Max Price (₹)",
#         "min_price":        "Min Price (₹)",
#     })
#     st.dataframe(df, use_container_width=True)


# # ══════════════════════════════════════════════
# #  PAGE 6 — DATA EXPLORER
# # ══════════════════════════════════════════════
# elif page == "🔍 Data Explorer":

#     st.title("🔍 Data Explorer")
#     st.caption("Filter, explore, and download the raw flight data")
#     st.markdown("---")

#     st.subheader("Filters")

#     fc1, fc2, fc3, fc4 = st.columns(4)
#     with fc1:
#         airline = st.multiselect("Airline",
#             run_query("SELECT DISTINCT airline FROM flight")["airline"].unique(),
#             key="de_airline")
#     with fc2:
#         source = st.multiselect("Source City",
#             run_query("SELECT DISTINCT source_city FROM flight")["source_city"].unique(),
#             key="de_source")
#     with fc3:
#         destination = st.multiselect("Destination City",
#             run_query("SELECT DISTINCT destination_city FROM flight")["destination_city"].unique(),
#             key="de_destination")
#     with fc4:
#         departure_time = st.multiselect("Departure Time",
#             run_query("SELECT DISTINCT departure_time FROM flight")["departure_time"].unique(),
#             key="de_departure")

#     fc5, fc6, fc7, fc8 = st.columns(4)
#     with fc5:
#         stops = st.multiselect("Stops",
#             run_query("SELECT DISTINCT stops FROM flight")["stops"].unique(),
#             key="de_stops")
#     with fc6:
#         arrival_time = st.multiselect("Arrival Time",
#             run_query("SELECT DISTINCT arrival_time FROM flight")["arrival_time"].unique(),
#             key="de_arrival")
#     with fc7:
#         flight_class = st.multiselect("Class",
#             run_query("SELECT DISTINCT class FROM flight")["class"].unique(),
#             key="de_class")
#     with fc8:
#         st.markdown("<br>", unsafe_allow_html=True)
#         if st.button("🗑️ Clear Filters", key="de_clear"):
#             for k in ["de_airline", "de_source", "de_destination", "de_departure",
#                       "de_stops", "de_arrival", "de_class"]:
#                 st.session_state[k] = []
#             min_p = int(run_query("SELECT MIN(price) FROM flight").iloc[0, 0])
#             max_p = int(run_query("SELECT MAX(price) FROM flight").iloc[0, 0])
#             min_d = int(run_query("SELECT MIN(days_left) FROM flight").iloc[0, 0])
#             max_d = int(run_query("SELECT MAX(days_left) FROM flight").iloc[0, 0])
#             st.session_state["de_price"] = (min_p, max_p)
#             st.session_state["de_days"]  = (min_d, max_d)
#             st.rerun()

#     sl1, sl2 = st.columns(2)
#     with sl1:
#         min_p = int(run_query("SELECT MIN(price) FROM flight").iloc[0, 0])
#         max_p = int(run_query("SELECT MAX(price) FROM flight").iloc[0, 0])
#         price_range = st.slider("Price Range (₹)",
#                                  min_value=min_p, max_value=max_p,
#                                  value=(min_p, max_p), key="de_price")
#     with sl2:
#         min_d = int(run_query("SELECT MIN(days_left) FROM flight").iloc[0, 0])
#         max_d = int(run_query("SELECT MAX(days_left) FROM flight").iloc[0, 0])
#         days_range = st.slider("Days Left to Departure",
#                                 min_value=min_d, max_value=max_d,
#                                 value=(min_d, max_d), key="de_days")

#     st.markdown("---")

#     # Build WHERE clause
#     wh = build_where({
#         "airline":           airline,
#         "source_city":       source,
#         "destination_city":  destination,
#         "departure_time":    departure_time,
#         "stops":             stops,
#         "arrival_time":      arrival_time,
#         "class":             flight_class,
#         "price":             price_range,
#         "days_left":         days_range,
#     })

#     df = run_query(f"SELECT * FROM flight {wh}")

#     # Mini summary metrics based on filtered data
#     m1, m2, m3, m4 = st.columns(4)
#     m1.metric("Flights Found", f"{len(df):,}")
#     m2.metric("Avg Price",     f"₹{int(df['price'].mean()):,}"  if len(df) else "—")
#     m3.metric("Min Price",     f"₹{int(df['price'].min()):,}"   if len(df) else "—")
#     m4.metric("Max Price",     f"₹{int(df['price'].max()):,}"   if len(df) else "—")

#     st.markdown("---")
#     st.dataframe(df, use_container_width=True)

#     st.download_button(
#         label="⬇️ Download Filtered Data as CSV",
#         data=df.to_csv(index=False).encode("utf-8"),
#         file_name="flights_filtered.csv",
#         mime="text/csv",
#     )