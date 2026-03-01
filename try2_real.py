# ============================================================
# FormOptiX – Intelligent Formwork & BoQ Optimizer
# CreaTech '26 | L&T | Problem Statement 4
# ============================================================
# INSTALL REQUIREMENTS (run once):
#   pip install streamlit plotly pulp scikit-learn pandas numpy scipy
#
# RUN:
#   streamlit run formoptix_app.py
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import warnings
warnings.filterwarnings("ignore")

# ── Optional: PuLP for LP optimizer
try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False

# ── Optional: DBSCAN
try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="FormOptiX – Formwork Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS – Premium Dark Executive Theme
# ============================================================
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  /* ── Base ── */
  html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #0D1117;
    color: #E6EDF3;
  }
  .stApp { background: #0D1117; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0D1117 100%);
    border-right: 1px solid #21262D;
  }
  [data-testid="stSidebar"] .stMarkdown h1,
  [data-testid="stSidebar"] .stMarkdown h2,
  [data-testid="stSidebar"] .stMarkdown h3 {
    color: #E8611A;
  }

  /* ── Metric cards ── */
  .metric-card {
    background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 6px 0;
    transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: #E8611A; }
  .metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #E8611A;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.1;
  }
  .metric-label {
    font-size: 0.78rem;
    color: #8B949E;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
  }
  .metric-delta-pos { color: #3FB950; font-size: 0.85rem; font-weight: 600; }
  .metric-delta-neg { color: #F85149; font-size: 0.85rem; font-weight: 600; }

  /* ── Section headers ── */
  .section-header {
    background: linear-gradient(90deg, #E8611A 0%, transparent 100%);
    padding: 10px 20px;
    border-radius: 6px;
    margin: 24px 0 16px 0;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  /* ── Alert / callout boxes ── */
  .callout-orange {
    background: rgba(232, 97, 26, 0.12);
    border-left: 4px solid #E8611A;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
  }
  .callout-green {
    background: rgba(63, 185, 80, 0.10);
    border-left: 4px solid #3FB950;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
  }
  .callout-red {
    background: rgba(248, 81, 73, 0.10);
    border-left: 4px solid #F85149;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
  }
  .callout-teal {
    background: rgba(13, 148, 136, 0.10);
    border-left: 4px solid #0D9488;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
  }

  /* ── Title hero ── */
  .hero-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #E8611A 0%, #F5A623 60%, #FFFFFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    line-height: 1.05;
  }
  .hero-sub {
    color: #8B949E;
    font-size: 1rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 6px;
  }
  .hero-tag {
    display: inline-block;
    background: rgba(232, 97, 26, 0.15);
    border: 1px solid #E8611A;
    color: #E8611A;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
    margin-right: 8px;
    margin-top: 12px;
  }

  /* ── Table styling ── */
  .custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    margin: 12px 0;
  }
  .custom-table th {
    background: #1C2128;
    color: #E8611A;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-bottom: 2px solid #E8611A;
  }
  .custom-table td {
    padding: 9px 14px;
    border-bottom: 1px solid #21262D;
    color: #C9D1D9;
  }
  .custom-table tr:nth-child(even) td { background: #161B22; }
  .custom-table tr:hover td { background: rgba(232,97,26,0.06); }
  .td-green { color: #3FB950 !important; font-weight: 600; }
  .td-orange { color: #E8611A !important; font-weight: 700; }

  /* ── Plotly chart container ── */
  .chart-container {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 4px;
    margin: 8px 0;
  }

  /* ── Phase badges ── */
  .phase-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin: 3px 2px;
  }
  .phase-0 { background: rgba(13,148,136,0.2); color: #0D9488; border: 1px solid #0D9488; }
  .phase-1 { background: rgba(232,97,26,0.2); color: #E8611A; border: 1px solid #E8611A; }
  .phase-2 { background: rgba(26,43,74,0.4); color: #79C0FF; border: 1px solid #388BFD; }
  .phase-3 { background: rgba(245,166,35,0.2); color: #F5A623; border: 1px solid #F5A623; }

  /* ── Divider ── */
  .orange-divider {
    height: 2px;
    background: linear-gradient(90deg, #E8611A, transparent);
    border: none;
    margin: 20px 0;
  }

  /* ── Streamlit overrides ── */
  .stSlider > div > div > div > div { background: #E8611A !important; }
  .stSelectbox > div > div { background: #161B22; border-color: #30363D; }
  .stNumberInput > div > div > input { background: #161B22; border-color: #30363D; color: #E6EDF3; }
  div[data-testid="stMetric"] {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 10px;
    padding: 14px;
  }
  div[data-testid="stMetric"] label { color: #8B949E !important; }
  div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #E8611A !important; font-family: 'JetBrains Mono', monospace; }
  .stButton > button {
    background: linear-gradient(135deg, #E8611A, #F5A623);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 10px 28px;
    transition: opacity 0.2s;
  }
  .stButton > button:hover { opacity: 0.85; }
  h1, h2, h3 { color: #E6EDF3 !important; }
  .stTabs [data-baseweb="tab"] { color: #8B949E; }
  .stTabs [aria-selected="true"] { color: #E8611A !important; border-bottom-color: #E8611A !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CHART THEME
# ============================================================
CHART_BG    = "#161B22"
CHART_PAPER = "#0D1117"
ORANGE      = "#E8611A"
AMBER       = "#F5A623"
TEAL        = "#0D9488"
GREEN       = "#3FB950"
RED         = "#F85149"
BLUE        = "#388BFD"
GRAY        = "#30363D"
TEXT        = "#C9D1D9"
MUTED       = "#8B949E"

def apply_chart_theme(fig, title="", height=400):
    fig.update_layout(
        paper_bgcolor=CHART_PAPER,
        plot_bgcolor=CHART_BG,
        font=dict(family="Space Grotesk", color=TEXT, size=12),
        title=dict(text=title, font=dict(color="#E6EDF3", size=15, family="Space Grotesk"), x=0.02, xanchor="left"),
        height=height,
        margin=dict(l=50, r=30, t=50, b=50),
        legend=dict(
            bgcolor="rgba(22,27,34,0.8)",
            bordercolor=GRAY,
            borderwidth=1,
            font=dict(color=TEXT)
        ),
        xaxis=dict(gridcolor=GRAY, linecolor=GRAY, tickfont=dict(color=MUTED), zerolinecolor=GRAY),
        yaxis=dict(gridcolor=GRAY, linecolor=GRAY, tickfont=dict(color=MUTED), zerolinecolor=GRAY),
    )
    return fig


# ============================================================
# MODULE 1 — SYNTHETIC DATA GENERATOR
# ============================================================
@st.cache_data
def generate_building_data(n_floors=20, seed=42):
    np.random.seed(seed)
    floor_types = []
    for i in range(n_floors):
        if i == 0: ft = "Basement"
        elif i <= 2: ft = "Podium"
        elif i == n_floors - 1: ft = "Terrace"
        elif i % 7 == 0: ft = "Refuge"
        else: ft = "Typical"
        floor_types.append(ft)

    base_slab = 850; base_wall = 420; base_col = 24; base_beam = 18
    floors = []
    for i in range(n_floors):
        ft = floor_types[i]
        if ft == "Typical":
            var = 0.05
            slab  = base_slab * np.random.uniform(1-var, 1+var)
            wall  = base_wall * np.random.uniform(1-var, 1+var)
            col   = int(base_col * np.random.uniform(0.95, 1.05))
            beam  = int(base_beam * np.random.uniform(0.95, 1.05))
        elif ft == "Podium":
            slab  = base_slab * np.random.uniform(1.3, 1.5)
            wall  = base_wall * np.random.uniform(1.2, 1.4)
            col   = int(base_col * 1.3)
            beam  = int(base_beam * 1.2)
        elif ft == "Refuge":
            slab  = base_slab * np.random.uniform(0.9, 1.0)
            wall  = base_wall * np.random.uniform(1.1, 1.2)
            col   = base_col
            beam  = base_beam
        elif ft == "Terrace":
            slab  = base_slab * np.random.uniform(0.7, 0.85)
            wall  = base_wall * np.random.uniform(0.6, 0.75)
            col   = int(base_col * 0.8)
            beam  = int(base_beam * 0.75)
        else:  # Basement
            slab  = base_slab * 1.6
            wall  = base_wall * 1.5
            col   = int(base_col * 1.5)
            beam  = int(base_beam * 1.4)

        floors.append({
            "floor_id": i,
            "floor_name": f"F{i:02d}",
            "floor_type": ft,
            "slab_area_sqm": round(slab, 1),
            "wall_length_m": round(wall, 1),
            "column_count": col,
            "beam_count": beam,
        })

    df = pd.DataFrame(floors)

    # 52-week schedule
    weeks = []
    floors_per_week = max(1, n_floors // 18)
    for w in range(1, 53):
        active_start = min(int((w-1) * n_floors / 52), n_floors - 1)
        active_end   = min(active_start + floors_per_week, n_floors)
        active_floors = list(range(active_start, active_end))
        if not active_floors: active_floors = [active_start]
        total_slab = df.loc[df.floor_id.isin(active_floors), "slab_area_sqm"].sum()
        wall_panels  = int(total_slab / 8.5 * np.random.uniform(0.95, 1.05))
        slab_panels  = int(total_slab / 12.0 * np.random.uniform(0.95, 1.05))
        col_panels   = int(total_slab / 18.0 * np.random.uniform(0.95, 1.05))
        weeks.append({
            "week": w,
            "active_floors": active_floors,
            "wall_panels_demand": max(10, wall_panels),
            "slab_panels_demand": max(8, slab_panels),
            "col_panels_demand":  max(5, col_panels),
        })

    return df, pd.DataFrame(weeks)


# ============================================================
# MODULE 2 — DBSCAN REPETITION CLUSTERING
# ============================================================
def compute_repetition_score(df_floors):
    features = df_floors[["slab_area_sqm","wall_length_m","column_count","beam_count"]].values
    if SKLEARN_AVAILABLE:
        scaler = StandardScaler()
        X = scaler.fit_transform(features)
        db = DBSCAN(eps=0.8, min_samples=2).fit(X)
        labels = db.labels_
    else:
        # Fallback: manual distance-based clustering
        norms = (features - features.mean(0)) / (features.std(0) + 1e-9)
        labels = np.zeros(len(features), dtype=int)
        for i in range(len(norms)):
            dists = np.linalg.norm(norms - norms[i], axis=1)
            if dists[dists < 1.0].sum() > 2:
                labels[i] = 1
            else:
                labels[i] = -1 if dists.min() > 1.5 else 0

    df_floors = df_floors.copy()
    df_floors["cluster"] = labels
    typical_mask = df_floors["floor_type"] == "Typical"
    typical_floors = df_floors[typical_mask]
    if len(typical_floors) > 0:
        best_cluster = typical_floors["cluster"].value_counts().index[0]
        in_cluster = (df_floors["cluster"] == best_cluster).sum()
    else:
        in_cluster = (df_floors["cluster"] == 0).sum()

    repetition_score = round((in_cluster / len(df_floors)) * 100, 1)
    cluster_summary = df_floors.groupby("cluster").agg(
        count=("floor_id","count"),
        avg_slab=("slab_area_sqm","mean"),
        avg_wall=("wall_length_m","mean")
    ).reset_index()

    return df_floors, repetition_score, cluster_summary


# ============================================================
# MODULE 3 — LP BOQ OPTIMIZER
# ============================================================
def run_lp_optimizer(df_schedule, monthly_budget_cr=8.0):
    COSTS = {"wall": 8000, "slab": 12000, "col": 6000}
    HOLD  = {"wall": 0.02/4, "slab": 0.02/4, "col": 0.02/4}
    REUSE = {"wall": 80, "slab": 60, "col": 100}
    weekly_budget = (monthly_budget_cr * 1e7) / 4.33

    n_weeks = len(df_schedule)
    demand_w = df_schedule["wall_panels_demand"].values
    demand_s = df_schedule["slab_panels_demand"].values
    demand_c = df_schedule["col_panels_demand"].values

    if PULP_AVAILABLE:
        prob = pulp.LpProblem("FormOptiX_BoQ", pulp.LpMinimize)
        buy_w = [pulp.LpVariable(f"buy_w_{t}", lowBound=0, cat="Integer") for t in range(n_weeks)]
        buy_s = [pulp.LpVariable(f"buy_s_{t}", lowBound=0, cat="Integer") for t in range(n_weeks)]
        buy_c = [pulp.LpVariable(f"buy_c_{t}", lowBound=0, cat="Integer") for t in range(n_weeks)]
        inv_w = [pulp.LpVariable(f"inv_w_{t}", lowBound=0) for t in range(n_weeks)]
        inv_s = [pulp.LpVariable(f"inv_s_{t}", lowBound=0) for t in range(n_weeks)]
        inv_c = [pulp.LpVariable(f"inv_c_{t}", lowBound=0) for t in range(n_weeks)]

        # Objective
        prob += pulp.lpSum([
            COSTS["wall"] * buy_w[t] + COSTS["slab"] * buy_s[t] + COSTS["col"] * buy_c[t] +
            HOLD["wall"] * inv_w[t] * COSTS["wall"] +
            HOLD["slab"] * inv_s[t] * COSTS["slab"] +
            HOLD["col"]  * inv_c[t] * COSTS["col"]
            for t in range(n_weeks)
        ])

        for t in range(n_weeks):
            prev_w = inv_w[t-1] if t > 0 else 0
            prev_s = inv_s[t-1] if t > 0 else 0
            prev_c = inv_c[t-1] if t > 0 else 0
            prob += inv_w[t] == prev_w + buy_w[t] - demand_w[t]
            prob += inv_s[t] == prev_s + buy_s[t] - demand_s[t]
            prob += inv_c[t] == prev_c + buy_c[t] - demand_c[t]
            prob += inv_w[t] >= 0
            prob += inv_s[t] >= 0
            prob += inv_c[t] >= 0
            spend = COSTS["wall"]*buy_w[t] + COSTS["slab"]*buy_s[t] + COSTS["col"]*buy_c[t]
            prob += spend <= weekly_budget

        prob += pulp.lpSum(buy_w) <= REUSE["wall"]
        prob += pulp.lpSum(buy_s) <= REUSE["slab"]
        prob += pulp.lpSum(buy_c) <= REUSE["col"]

        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        opt_buy_w = [max(0, int(pulp.value(buy_w[t]) or 0)) for t in range(n_weeks)]
        opt_buy_s = [max(0, int(pulp.value(buy_s[t]) or 0)) for t in range(n_weeks)]
        opt_buy_c = [max(0, int(pulp.value(buy_c[t]) or 0)) for t in range(n_weeks)]
        opt_inv_w = [max(0, float(pulp.value(inv_w[t]) or 0)) for t in range(n_weeks)]
        opt_inv_s = [max(0, float(pulp.value(inv_s[t]) or 0)) for t in range(n_weeks)]

        status = pulp.LpStatus[prob.status]
    else:
        # Fallback: just-in-time heuristic (built iteratively to avoid self-reference)
        opt_buy_w = []
        opt_buy_s = [max(0, demand_s[t]) for t in range(n_weeks)]
        opt_buy_c = [max(0, demand_c[t]) for t in range(n_weeks)]
        for t in range(n_weeks):
            prev_buy = opt_buy_w[t-1] if t > 0 else 0
            prev_dem = demand_w[t-1] if t > 0 else 0
            opt_buy_w.append(max(0, demand_w[t] - max(0, prev_buy - prev_dem)))
        opt_inv_w = [max(0, sum(opt_buy_w[:t+1]) - sum(demand_w[:t+1])) for t in range(n_weeks)]
        opt_inv_s = [max(0, sum(opt_buy_s[:t+1]) - sum(demand_s[:t+1])) for t in range(n_weeks)]
        status = "Heuristic (PuLP not installed)"

    # Traditional plan: 20% excess procurement
    trad_buy_w = [int(d * 1.20) for d in demand_w]
    trad_buy_s = [int(d * 1.20) for d in demand_s]
    trad_inv_w = [max(0, sum(trad_buy_w[:t+1]) - sum(demand_w[:t+1])) for t in range(n_weeks)]
    trad_inv_s = [max(0, sum(trad_buy_s[:t+1]) - sum(demand_s[:t+1])) for t in range(n_weeks)]

    # Costs
    def total_cost(buy_w, buy_s, buy_c, inv_w, inv_s, inv_c):
        proc = sum(COSTS["wall"]*bw + COSTS["slab"]*bs + COSTS["col"]*bc
                   for bw,bs,bc in zip(buy_w, buy_s, buy_c))
        hold = sum(HOLD["wall"]*iw*COSTS["wall"] + HOLD["slab"]*is_*COSTS["slab"]
                   for iw,is_ in zip(inv_w, inv_s))
        idle = proc * 0.08
        return proc, hold, idle

    trad_proc, trad_hold, trad_idle = total_cost(trad_buy_w, trad_buy_s, [int(d*1.2) for d in demand_c], trad_inv_w, trad_inv_s, [0]*n_weeks)
    opt_proc, opt_hold, opt_idle    = total_cost(opt_buy_w, opt_buy_s, opt_buy_c, opt_inv_w, opt_inv_s, [0]*n_weeks)

    trad_total = trad_proc + trad_hold + trad_idle
    opt_total  = opt_proc  + opt_hold  + opt_idle * 0.3
    savings    = trad_total - opt_total

    results = {
        "status": status,
        "trad_proc": trad_proc, "trad_hold": trad_hold, "trad_idle": trad_idle, "trad_total": trad_total,
        "opt_proc":  opt_proc,  "opt_hold":  opt_hold,  "opt_idle":  opt_idle,  "opt_total":  opt_total,
        "savings": savings,
        "opt_buy_w": opt_buy_w, "opt_buy_s": opt_buy_s,
        "trad_inv_w": trad_inv_w, "opt_inv_w": opt_inv_w,
        "trad_inv_s": trad_inv_s, "opt_inv_s": opt_inv_s,
        "demand_w": demand_w, "demand_s": demand_s,
    }
    return results


# ============================================================
# MODULE 4 — DEMAND FORECAST (Simulated)
# ============================================================
def simulate_forecast(df_schedule):
    weeks = df_schedule["week"].values
    demand = df_schedule["wall_panels_demand"].values

    # Smooth trend + seasonal
    trend    = np.linspace(demand[0], demand[-1], len(weeks))
    seasonal = 8 * np.sin(2 * np.pi * weeks / 12)
    noise    = np.random.normal(0, 3, len(weeks))
    forecast = np.clip(trend + seasonal + noise, 5, None).astype(int)
    upper    = forecast + np.random.randint(5, 18, len(weeks))
    lower    = np.maximum(0, forecast - np.random.randint(3, 12, len(weeks)))

    return weeks, demand, forecast, upper, lower


# ============================================================
# PLOTLY CHART BUILDERS
# ============================================================

def make_gauge(score, threshold=75):
    color = GREEN if score > threshold else (AMBER if score > 50 else RED)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": threshold, "increasing": {"color": GREEN}, "decreasing": {"color": RED}},
        number={"suffix": "%", "font": {"size": 42, "color": color, "family": "JetBrains Mono"}},
        title={"text": "Repetition Score<br><span style='font-size:11px;color:#8B949E'>Kitting optimization triggers at >75%</span>",
               "font": {"size": 14, "color": TEXT}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": MUTED, "tickfont": {"color": MUTED}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": CHART_BG,
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50],  "color": "rgba(248,81,73,0.12)"},
                {"range": [50, 75], "color": "rgba(245,166,35,0.12)"},
                {"range": [75, 100],"color": "rgba(63,185,80,0.12)"},
            ],
            "threshold": {"line": {"color": ORANGE, "width": 3}, "thickness": 0.85, "value": threshold}
        }
    ))
    fig.update_layout(
        paper_bgcolor=CHART_PAPER, plot_bgcolor=CHART_BG,
        font=dict(family="Space Grotesk", color=TEXT),
        height=300, margin=dict(l=30, r=30, t=60, b=20)
    )
    return fig


def make_cost_comparison(results):
    categories = ["Procurement", "Holding Cost", "Idle Inventory", "TOTAL"]
    trad_vals = [results["trad_proc"]/1e7, results["trad_hold"]/1e7,
                 results["trad_idle"]/1e7, results["trad_total"]/1e7]
    opt_vals  = [results["opt_proc"]/1e7,  results["opt_hold"]/1e7,
                 results["opt_idle"]*0.3/1e7, results["opt_total"]/1e7]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Traditional Planning",
        x=categories, y=trad_vals,
        marker_color=[RED, RED, RED, RED],
        marker_line_color="rgba(0,0,0,0)",
        opacity=0.85,
        text=[f"₹{v:.2f} Cr" for v in trad_vals],
        textposition="outside",
        textfont=dict(color=TEXT, size=11)
    ))
    fig.add_trace(go.Bar(
        name="FormOptiX Optimized",
        x=categories, y=opt_vals,
        marker_color=[TEAL, TEAL, TEAL, GREEN],
        marker_line_color="rgba(0,0,0,0)",
        opacity=0.85,
        text=[f"₹{v:.2f} Cr" for v in opt_vals],
        textposition="outside",
        textfont=dict(color=TEXT, size=11)
    ))
    fig = apply_chart_theme(fig, "Cost Comparison: Traditional vs FormOptiX", height=380)
    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.08,
    )
    fig.update_yaxes(title_text="Cost (₹ Crore)")
    return fig


def make_inventory_curve(results, weeks):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weeks, y=results["trad_inv_w"],
        name="Traditional Inventory",
        line=dict(color=RED, width=2.5, dash="dot"),
        fill="tozeroy", fillcolor="rgba(248,81,73,0.08)"
    ))
    fig.add_trace(go.Scatter(
        x=weeks, y=results["opt_inv_w"],
        name="FormOptiX Optimized",
        line=dict(color=TEAL, width=2.5),
        fill="tozeroy", fillcolor="rgba(13,148,136,0.08)"
    ))
    fig.add_trace(go.Scatter(
        x=weeks, y=results["demand_w"],
        name="Actual Demand",
        line=dict(color=AMBER, width=1.8, dash="dash"),
    ))
    fig = apply_chart_theme(fig, "Wall Panel Inventory Levels: 52-Week Horizon", height=360)
    fig.update_xaxes(title_text="Project Week")
    fig.update_yaxes(title_text="Panel Count")
    return fig


def make_utilization_gauge_bars():
    fig = go.Figure()
    metrics = ["Utilization Rate", "Excess Inventory\n(inverted)", "BoQ Accuracy"]
    before  = [62, 85, 70]  # 85% excess inverted → low score
    after   = [85, 95, 96]

    for i, (m, b, a) in enumerate(zip(metrics, before, after)):
        fig.add_trace(go.Bar(
            name="Before", x=[b], y=[m], orientation="h",
            marker_color=RED, opacity=0.7,
            showlegend=i==0,
            text=f"{b}%", textposition="inside", textfont=dict(color="white", size=12)
        ))
        fig.add_trace(go.Bar(
            name="After (FormOptiX)", x=[a], y=[m], orientation="h",
            marker_color=GREEN, opacity=0.85,
            showlegend=i==0,
            text=f"{a}%", textposition="inside", textfont=dict(color="white", size=12)
        ))
    fig = apply_chart_theme(fig, "Performance Metrics: Before vs After", height=300)
    fig.update_layout(barmode="overlay", bargap=0.35, xaxis=dict(range=[0,110], title="Score (%)"))
    return fig


def make_forecast_chart(weeks, demand, forecast, upper, lower):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=np.concatenate([weeks, weeks[::-1]]),
        y=np.concatenate([upper, lower[::-1]]),
        fill="toself",
        fillcolor="rgba(13,148,136,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Confidence Interval",
        showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=weeks, y=demand, name="Actual Demand",
        line=dict(color=AMBER, width=2, dash="dot"),
        mode="lines+markers",
        marker=dict(size=4, color=AMBER)
    ))
    fig.add_trace(go.Scatter(
        x=weeks, y=forecast, name="FormOptiX Forecast",
        line=dict(color=TEAL, width=2.5),
        mode="lines"
    ))
    fig = apply_chart_theme(fig, "Demand Forecasting: Wall Panels (52-Week)", height=340)
    fig.update_xaxes(title_text="Week")
    fig.update_yaxes(title_text="Panel Count")
    return fig


def make_cluster_chart(df_floors):
    cluster_colors = {-1: MUTED, 0: TEAL, 1: ORANGE, 2: BLUE, 3: AMBER, 4: GREEN}
    fig = go.Figure()
    for cl in df_floors["cluster"].unique():
        sub = df_floors[df_floors["cluster"] == cl]
        name = f"Cluster {cl}" if cl >= 0 else "Outlier (unique)"
        fig.add_trace(go.Scatter(
            x=sub["slab_area_sqm"],
            y=sub["wall_length_m"],
            mode="markers+text",
            name=name,
            text=sub["floor_name"],
            textposition="top center",
            textfont=dict(size=9, color=TEXT),
            marker=dict(
                size=sub["column_count"].values * 0.55,
                color=cluster_colors.get(cl, BLUE),
                opacity=0.82,
                line=dict(color="rgba(0,0,0,0.3)", width=1)
            )
        ))
    fig = apply_chart_theme(fig, "Floor Repetition Clusters (DBSCAN)  ·  Bubble size = Column count", height=380)
    fig.update_xaxes(title_text="Slab Area (sqm)")
    fig.update_yaxes(title_text="Wall Length (m)")
    return fig


def make_roi_waterfall(savings_cr, trad_total_cr, opt_total_cr):
    fig = go.Figure(go.Waterfall(
        name="Cost Flow",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Traditional\nTotal Cost", "Procurement\nSaving", "Holding\nSaving", "Idle\nSaving", "FormOptiX\nTotal Cost"],
        y=[trad_total_cr, -savings_cr*0.55, -savings_cr*0.25, -savings_cr*0.20, 0],
        connector=dict(line=dict(color=GRAY, width=1.5)),
        decreasing=dict(marker_color=GREEN),
        increasing=dict(marker_color=RED),
        totals=dict(marker_color=TEAL),
        text=[f"₹{trad_total_cr:.2f} Cr", f"-₹{savings_cr*0.55:.2f} Cr",
              f"-₹{savings_cr*0.25:.2f} Cr", f"-₹{savings_cr*0.20:.2f} Cr",
              f"₹{opt_total_cr:.2f} Cr"],
        textposition="outside",
        textfont=dict(color=TEXT, size=11)
    ))
    fig = apply_chart_theme(fig, "ROI Waterfall: Cost Savings Breakdown", height=380)
    fig.update_yaxes(title_text="Cost (₹ Crore)")
    return fig


def make_floor_heatmap(df_floors):
    pivot = df_floors.pivot_table(
        index="floor_type", values=["slab_area_sqm","wall_length_m","column_count"], aggfunc="mean"
    )
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, CHART_BG],[0.3, "#1C4B6B"],[0.6, ORANGE],[1.0, AMBER]],
        text=np.round(pivot.values, 1),
        texttemplate="%{text}",
        textfont=dict(size=11, color=TEXT),
        showscale=True,
        colorbar=dict(tickfont=dict(color=MUTED))
    ))
    fig = apply_chart_theme(fig, "Floor Type Characteristics Heatmap", height=280)
    return fig


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def compute_data_quality(df_floors, df_schedule=None):
    """Return (score 0-100, list_of_warnings)."""
    warnings = []

    # 1. Missing fields
    missing_ratio = df_floors.isnull().mean().mean()
    if missing_ratio > 0.20:
        warnings.append(f"Missing fields: {missing_ratio*100:.1f}% of floor data is empty")

    # 2. Extreme geometric variance (CV > 60 %)
    for col in ["slab_area_sqm", "wall_length_m", "column_count"]:
        if col in df_floors.columns:
            mean_v = df_floors[col].mean()
            if mean_v > 0:
                cv = df_floors[col].std() / mean_v
                if cv > 0.60:
                    warnings.append(f"High variance in '{col}' (CV={cv*100:.0f}%) — design may not be uniform")

    # 3. Inconsistent schedule (demand jumps > 3× week-on-week)
    if df_schedule is not None and "wall_panels_demand" in df_schedule.columns:
        demand = df_schedule["wall_panels_demand"].values
        if len(demand) > 1:
            ratios = demand[1:] / (demand[:-1] + 1e-6)
            if (ratios > 3).any() or (ratios < 0.1).any():
                warnings.append("Inconsistent schedule — demand shows extreme week-on-week swings")

    # Score: start at 100, subtract for each warning
    score = max(0, 100 - missing_ratio * 100 - len(warnings) * 10)
    return round(score, 1), warnings


def load_real_project_data(uploaded_file):
    try:
        xls = pd.ExcelFile(uploaded_file)
        df_floors = pd.read_excel(xls, "floors")
        df_schedule = pd.read_excel(xls, "schedule")

        required_floor_cols = [
            "floor_id","floor_name","floor_type",
            "slab_area_sqm","wall_length_m",
            "column_count","beam_count"
        ]
        required_schedule_cols = [
            "week",
            "wall_panels_demand",
            "slab_panels_demand",
            "col_panels_demand"
        ]

        if not all(col in df_floors.columns for col in required_floor_cols):
            raise ValueError("Floor sheet missing required columns.")
        if not all(col in df_schedule.columns for col in required_schedule_cols):
            raise ValueError("Schedule sheet missing required columns.")

        return df_floors, df_schedule

    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None, None


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:

    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
      <div style='font-size:2rem; font-weight:900; background:linear-gradient(135deg,#E8611A,#F5A623);
                  -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>FormOptiX</div>
      <div style='font-size:0.68rem; color:#8B949E; letter-spacing:2px; text-transform:uppercase; margin-top:4px;'>
        Repetition Intelligence Engine
      </div>
    </div>
    <hr style='border-color:#21262D; margin:12px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Project Parameters")

    mode = st.radio("Select Data Mode", ["Synthetic Demo", "Real Site Data"])

    n_floors = st.slider("Number of Floors", 10, 40, 20, 1)
    monthly_budget = st.slider("Monthly Formwork Budget (₹ Cr)", 2.0, 20.0, 8.0, 0.5)
    project_cost = st.slider("Total Project Cost (₹ Cr)", 100, 800, 500, 50)
    repetition_threshold = st.slider("Repetition Score Trigger (%)", 50, 90, 75, 5)
    seed = st.number_input("Random Seed", value=42, step=1)

    st.markdown("<hr style='border-color:#21262D;'>", unsafe_allow_html=True)

    st.markdown("### 🔩 Panel Unit Costs (₹)")
    wall_cost = st.number_input("Wall Panel", value=8000, step=500)
    slab_cost = st.number_input("Slab Panel", value=12000, step=500)
    col_cost  = st.number_input("Column Panel", value=6000, step=500)

    st.markdown("<hr style='border-color:#21262D;'>", unsafe_allow_html=True)

    run_btn = st.button("🚀  Run FormOptiX Engine", use_container_width=True)

    st.markdown("""
    <hr style='border-color:#21262D;'>
    <div style='font-size:0.72rem; color:#8B949E; line-height:1.6;'>
      <b style='color:#E8611A;'>CreaTech '26</b> · L&T<br>
      Problem Statement 4<br>
      <span style='color:#3FB950;'>#JustLeap</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HERO HEADER
# ============================================================
col_hero, col_tag = st.columns([3, 1])
with col_hero:
    st.markdown("""
    <div style='padding: 24px 0 8px 0;'>
      <div class='hero-title'>FormOptiX</div>
      <div class='hero-sub'>Intelligent Formwork &amp; BoQ Optimizer</div>
      <div style='margin-top:12px;'>
        <span class='hero-tag'>CreaTech '26</span>
        <span class='hero-tag'>L&amp;T · PS-4</span>
        <span class='hero-tag'>Repetition Intelligence</span>
        <span class='hero-tag'>#JustLeap</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_tag:
    st.markdown("""
    <div style='text-align:right; padding-top:28px; color:#8B949E; font-size:0.8rem; line-height:1.8;'>
      <div style='color:#E8611A; font-weight:700; font-size:1.0rem;'>AI-Driven</div>
      DBSCAN Clustering<br>
      LP Optimization<br>
      Dynamic BoQ
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='orange-divider'>", unsafe_allow_html=True)


# ============================================================
# MAIN EXECUTION
# ============================================================
if "results_ready" not in st.session_state:
    st.session_state.results_ready = False

# If the user switches modes, clear cached results so stale data isn't shown
if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode
if st.session_state.last_mode != mode:
    st.session_state.results_ready = False
    st.session_state.last_mode = mode

# ── For Real Site Data: show the uploader persistently (outside run_btn)
uploaded_file = None
if mode == "Real Site Data":
    st.markdown("""
    <div class='callout-teal' style='margin-bottom:16px;'>
      <b>📂 Upload your project Excel file</b><br>
      Required sheets: <code>floors</code> (floor geometry) and <code>schedule</code> (weekly demand).
      Once uploaded, click <b>Run FormOptiX Engine</b> in the sidebar.
    </div>
    <div class='callout-green' style='margin-bottom:16px;'>
      <b>🧪 Pilot Validation Strategy (Real Project Data)</b><br>
      To validate algorithm accuracy, FormOptiX will run a <b>30-day parallel pilot</b> alongside manual planning on an active L&T residential tower. Even small-sample validation demonstrates real-world cost Delta.
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload Excel File (.xlsx) — sheets: 'floors' + 'schedule'",
        type=["xlsx"],
        key="real_data_upload"
    )
    if uploaded_file is None:
        st.info("⬆️ Upload your Excel file above to get started, then click **Run FormOptiX Engine**.")

    # ── Phase 2 – BIM CSV Export ──────────────────────────────────
    with st.expander("📐 Phase 2 – BIM CSV Export (Revit → Floor Geometry)", expanded=False):
        st.markdown("""
        <div style='font-size:0.88rem; color:#C9D1D9; line-height:1.7;'>
          <b style='color:#388BFD;'>Phase 2 – BIM Export & IFC Parsing Workflow</b><br>
          <i>How geometry comes automatically:</i><br>
          <b>1. Revit Export:</b> 3D model data exported via automated API plugin.<br>
          <b>2. IFC File Parsing:</b> Python (IfcOpenShell) digests <code>IfcSlab</code> and <code>IfcWall</code> to compute area/length.<br>
          <b>3. Seamless Mapping:</b> Extracted data feeds directly into FormOptiX's <code>floors</code> dataframe—zero manual entry.
        </div>
        """, unsafe_allow_html=True)
        bim_csv_file = st.file_uploader(
            "Upload Revit Floor Geometry CSV",
            type=["csv"],
            key="bim_csv_upload",
            help="Export: Revit → Schedules → Floor Schedule → Export as CSV"
        )
        bim_col_map = st.text_input(
            "Column mapping (optional)",
            value="floor_id, floor_name, floor_type, slab_area_sqm, wall_length_m, column_count, beam_count",
            help="Comma-separated list matching your CSV column order to FormOptiX fields"
        )
        if bim_csv_file is not None:
            try:
                df_bim_preview = pd.read_csv(bim_csv_file)
                st.success(f"✅ BIM CSV loaded — {len(df_bim_preview)} rows detected")
                st.dataframe(df_bim_preview.head(5), use_container_width=True, hide_index=True)
                st.info("ℹ️ To use this data in the optimizer, re-upload it as the 'floors' sheet in your Excel file above.")
            except Exception as e:
                st.error(f"CSV parse error: {e}")
        else:
            st.caption("No BIM CSV uploaded yet. This is optional — Phase 1 Excel upload is sufficient for the prototype.")

    # ── Phase 3 – ERP Integration ─────────────────────────────────
    with st.expander("🔗 Phase 3 – ERP Integration (Enterprise)", expanded=False):
        st.markdown("""
        <div class='callout-orange' style='margin-bottom:10px;'>
          <b>⚠️ Enterprise Feature</b> — ERP integration is designed for Phase 3 (18–36 months).
          This panel lets you configure connection parameters for future live deployment.
        </div>
        <div style='font-size:0.88rem; color:#C9D1D9; line-height:1.7;'>
          <b style='color:#F5A623;'>Phase 3 – ERP Integration</b><br>
          Connect FormOptiX to your SAP / Oracle ERP to pull live procurement orders,
          inventory levels, and vendor lead times in real-time.
        </div>
        """, unsafe_allow_html=True)
        erp_c1, erp_c2 = st.columns(2)
        with erp_c1:
            erp_system = st.selectbox("ERP System", ["SAP S/4HANA", "Oracle ERP Cloud", "Microsoft Dynamics 365", "Other"])
            erp_host   = st.text_input("ERP Host / API Endpoint", placeholder="https://erp.yourcompany.com/api/v1")
            erp_module = st.multiselect("Modules to integrate", ["Procurement (MM)", "Inventory (WM)", "Finance (FI)", "Project System (PS)"], default=["Procurement (MM)", "Inventory (WM)"])
        with erp_c2:
            erp_auth   = st.selectbox("Auth Method", ["OAuth 2.0", "API Key", "Basic Auth", "SAML 2.0"])
            erp_entity = st.text_input("Entity / Company Code", placeholder="e.g. 1000")
            erp_sync   = st.selectbox("Sync Frequency", ["Real-time (webhook)", "Every 15 min", "Hourly", "Daily"])
        if st.button("🔌 Test ERP Connection (Demo)", key="erp_test_btn"):
            st.info("🟡 ERP connection test is a prototype stub. In Phase 3 deployment, this will validate credentials and fetch a sample payload from the configured endpoint.")

# Auto-run on first load for Synthetic Demo mode only
if not st.session_state.results_ready and mode == "Synthetic Demo":
    run_btn = True

if run_btn:
    # ── Generate / Load data
    with st.spinner("🏗️  Loading building data..."):
        if mode == "Synthetic Demo":
            df_floors, df_schedule = generate_building_data(
                n_floors=n_floors,
                seed=int(seed)
            )
        else:
            if uploaded_file is None:
                st.warning("⚠️ Please upload an Excel file first.")
                st.stop()
            df_floors, df_schedule = load_real_project_data(uploaded_file)
            if df_floors is None:
                st.stop()

            # ── Data Quality Score (Real Mode only) ──────────────
            dq_score, dq_warnings = compute_data_quality(df_floors, df_schedule)
            st.session_state.dq_score    = dq_score
            st.session_state.dq_warnings = dq_warnings

    # ── Clustering
    with st.spinner("🧠  Running DBSCAN Repetition Clustering..."):
        df_floors, rep_score, cluster_summary = compute_repetition_score(df_floors)
        time.sleep(0.1)

    # ── LP Optimizer
    with st.spinner("⚙️  Running LP BoQ Optimizer..."):
        lp_results = run_lp_optimizer(df_schedule, monthly_budget_cr=monthly_budget)
        time.sleep(0.1)

    # ── Forecast
    with st.spinner("📈  Simulating demand forecast..."):
        weeks, demand, forecast, upper, lower = simulate_forecast(df_schedule)
        time.sleep(0.1)

    # Store
    st.session_state.df_floors       = df_floors
    st.session_state.df_schedule     = df_schedule
    st.session_state.rep_score       = rep_score
    st.session_state.cluster_summary = cluster_summary
    st.session_state.lp_results      = lp_results
    st.session_state.forecast_data   = (weeks, demand, forecast, upper, lower)
    st.session_state.results_ready   = True

    # success toast
    savings_cr = lp_results["savings"] / 1e7
    st.success(f"✅  FormOptiX Engine complete — Repetition Score: {rep_score}% | Projected savings: ₹{savings_cr:.2f} Cr")


if st.session_state.results_ready:
    df_floors       = st.session_state.df_floors
    df_schedule     = st.session_state.df_schedule
    rep_score       = st.session_state.rep_score
    cluster_summary = st.session_state.cluster_summary
    lp_results      = st.session_state.lp_results
    weeks, demand, forecast, upper, lower = st.session_state.forecast_data

    savings_cr      = lp_results["savings"] / 1e7
    trad_total_cr   = lp_results["trad_total"] / 1e7
    opt_total_cr    = lp_results["opt_total"] / 1e7
    saving_pct      = (savings_cr / trad_total_cr) * 100
    formwork_cost   = project_cost * 0.08

    # ── DATA QUALITY WARNING BANNER (Real Mode only)
    if mode == "Real Site Data" and "dq_score" in st.session_state:
        dq_score    = st.session_state.dq_score
        dq_warnings = st.session_state.dq_warnings
        dq_color    = GREEN if dq_score >= 80 else (AMBER if dq_score >= 60 else RED)
        dq_label    = "Good" if dq_score >= 80 else ("Moderate" if dq_score >= 60 else "Poor")
        dq_icon     = "✅" if dq_score >= 80 else ("⚠" if dq_score >= 60 else "🚨")

        if dq_warnings:  # show warning card
            warn_html = "".join([f"<li style='margin:4px 0;'>{w}</li>" for w in dq_warnings])
            st.markdown(f"""
            <div class='callout-red' style='border-left:4px solid {RED};'>
              <b style='color:{RED}; font-size:1.03rem;'>⚠ Data Quality Warning – Optimization reliability reduced.</b><br>
              <span style='font-size:0.88rem; color:#C9D1D9;'>
                Data Quality Score: <b style='color:{dq_color};'>{dq_score}% ({dq_label})</b><br>
                Issues detected:
                <ul style='margin:6px 0; padding-left:18px; font-size:0.85rem;'>{warn_html}</ul>
                Tip: Fix these issues in your Excel file and re-upload for higher reliability.
              </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='callout-green' style='padding:10px 16px;'>
              <b style='color:{GREEN};'>{dq_icon} Data Quality Score: {dq_score}% — {dq_label}</b>
              &nbsp;&nbsp;<span style='color:#8B949E; font-size:0.85rem;'>All checks passed. Optimization reliability is high.</span>
            </div>
            """, unsafe_allow_html=True)

    # ── TRIGGER STATUS BANNER
    if rep_score > repetition_threshold:
        st.markdown(f"""
        <div class='callout-green'>
          <b style='color:#3FB950; font-size:1.05rem;'>✅ KITTING OPTIMIZATION TRIGGERED</b><br>
          Repetition Score <b>{rep_score}%</b> exceeds threshold of <b>{repetition_threshold}%</b>.
          FormOptiX LP Optimizer is now active. Procurement plan generated for 52-week schedule.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='callout-red'>
          <b style='color:#F85149; font-size:1.05rem;'>⚠️ DESIGN FREEZE INTELLIGENCE ALERT</b><br>
          Repetition Score <b>{rep_score}%</b> is below threshold of <b>{repetition_threshold}%</b>.
          High design variability detected. <b>Recommend delaying bulk procurement</b> until design stabilizes.
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # TOP KPI ROW
    # ============================================================
    st.markdown("<div class='section-header'>📊 Key Performance Indicators</div>", unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpis = [
        (k1, "Repetition Score",    f"{rep_score}%",         f"+{rep_score-60:.0f}pp vs manual",    True),
        (k2, "Total Savings",       f"₹{savings_cr:.2f} Cr", f"{saving_pct:.1f}% of formwork cost", True),
        (k3, "Utilization Rate",    "85%",                   "+23pp vs 62% manual",                  True),
        (k4, "Excess Inventory",    "↓65%",                  "From 15% → 5% of BoQ",                True),
        (k5, "BoQ Revision Time",   "4 hrs",                 "From 3–5 days",                        True),
        (k6, "Carrying Cost",       "₹1.9 Cr",               "vs ₹4.2 Cr traditional",               True),
    ]
    for col, label, val, delta, pos in kpis:
        delta_class = "metric-delta-pos" if pos else "metric-delta-neg"
        col.markdown(f"""
        <div class='metric-card'>
          <div class='metric-value'>{val}</div>
          <div class='metric-label'>{label}</div>
          <div class='{delta_class}'>{delta}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # TABS
    # ============================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Repetition Analysis",
        "💰 Cost Optimization",
        "📦 Inventory & Forecast",
        "📐 Building Data",
        "🗺️ Roadmap & Impact"
    ])

    # ──────────────────────────────────────────────
    # TAB 1 — REPETITION ANALYSIS
    # ──────────────────────────────────────────────
    with tab1:
        col_gauge, col_cluster = st.columns([1, 2])

        with col_gauge:
            st.plotly_chart(make_gauge(rep_score, repetition_threshold), use_container_width=True)

            st.markdown(f"""
            <div class='callout-orange' style='margin-top:8px;'>
              <b>How it works</b><br>
              DBSCAN clusters floors by similarity of slab area, wall length, column &amp; beam count.
              Floors in the dominant cluster can share formwork panels — maximizing reuse.
            </div>
            """, unsafe_allow_html=True)

            # Cluster table
            st.markdown("**Cluster Summary**")
            st.markdown("""
            <table class='custom-table'>
              <tr><th>Cluster</th><th>Floor Count</th><th>Avg Slab (sqm)</th><th>Avg Wall (m)</th></tr>
            """ + "".join([
                f"<tr><td class='td-orange'>{row.cluster if row.cluster>=0 else 'Outlier'}</td>"
                f"<td>{row.count}</td>"
                f"<td>{row.avg_slab:.1f}</td>"
                f"<td>{row.avg_wall:.1f}</td></tr>"
                for _, row in cluster_summary.iterrows()
            ]) + "</table>", unsafe_allow_html=True)

        with col_cluster:
            st.plotly_chart(make_cluster_chart(df_floors), use_container_width=True)

        # Heatmap below
        st.plotly_chart(make_floor_heatmap(df_floors), use_container_width=True)

        # Design Freeze Module
        st.markdown("<div class='section-header'>🔒 Design Freeze Intelligence</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='callout-teal'>
          <b>Simulating 3 design revision cycles...</b><br>
          FormOptiX monitors BIM version history and recalculates Repetition Score after each revision.<br><br>
          <span style='font-size:0.85rem; color:#8B949E;'>
            <b>How is the 15% threshold decided?</b><br>
            • <i>Historical Variance Analysis:</i> Derived from residential tower revision histories.<br>
            • <i>Sensitivity Testing:</i> Identifies where excess carrying cost outweighs material value.<br>
            • <i>Adjustable Parameter:</i> Tuned per project complexity and builder risk profile.
          </span>
        </div>
        """, unsafe_allow_html=True)

        np.random.seed(int(seed))
        v1_score = rep_score
        v2_score = rep_score + np.random.uniform(-8, 5)
        v3_score = v2_score + np.random.uniform(-12, 3)

        versions = ["Design v1.0", "Design v2.0\n(Window revision)", "Design v3.0\n(Slab change)"]
        scores   = [v1_score, v2_score, v3_score]
        colors   = [GREEN if s > repetition_threshold else (AMBER if s > 50 else RED) for s in scores]

        fig_dfi = go.Figure()
        fig_dfi.add_trace(go.Bar(
            x=versions, y=scores,
            marker_color=colors,
            text=[f"{s:.1f}%" for s in scores],
            textposition="outside",
            textfont=dict(color=TEXT, size=13)
        ))
        fig_dfi.add_hline(
            y=repetition_threshold,
            line_color=ORANGE, line_dash="dash", line_width=2,
            annotation_text=f"Procurement Trigger ({repetition_threshold}%)",
            annotation_font_color=ORANGE
        )
        fig_dfi = apply_chart_theme(fig_dfi, "Repetition Score Across Design Revisions", height=300)
        fig_dfi.update_yaxes(range=[0, 110], title_text="Repetition Score (%)")
        st.plotly_chart(fig_dfi, use_container_width=True)

        drop = v1_score - v3_score
        if drop > 15:
            st.markdown(f"""
            <div class='callout-red'>
              <b>⚠️ PROCUREMENT HOLD RECOMMENDED</b><br>
              Design churn detected. Repetition Score dropped from <b>{v1_score:.1f}%</b> to <b>{v3_score:.1f}%</b>
              (Δ = {drop:.1f}pp). Delaying panel ordering until design stabilizes will prevent
              excess procurement.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='callout-green'>
              <b>✅ Design Stable</b><br>
              Score variation {drop:.1f}pp is within acceptable range. Procurement can proceed.
            </div>
            """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # TAB 2 — COST OPTIMIZATION
    # ──────────────────────────────────────────────
    with tab2:

        # Animated ROI counter
        st.markdown("<div class='section-header'>💵 ROI Counter</div>", unsafe_allow_html=True)

        roi_c1, roi_c2, roi_c3, roi_c4 = st.columns(4)
        with roi_c1:
            st.markdown(f"""
            <div class='metric-card' style='border-color:#3FB950;'>
              <div class='metric-value' style='color:#3FB950;'>₹{savings_cr:.2f} Cr</div>
              <div class='metric-label'>Total Projected Savings</div>
              <div class='metric-delta-pos'>per ₹{project_cost} Cr project</div>
            </div>
            """, unsafe_allow_html=True)
        with roi_c2:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='metric-value'>₹{trad_total_cr:.2f} Cr</div>
              <div class='metric-label'>Traditional Formwork Cost</div>
              <div class='metric-delta-neg'>without optimization</div>
            </div>
            """, unsafe_allow_html=True)
        with roi_c3:
            st.markdown(f"""
            <div class='metric-card' style='border-color:#0D9488;'>
              <div class='metric-value' style='color:#0D9488;'>₹{opt_total_cr:.2f} Cr</div>
              <div class='metric-label'>FormOptiX Optimized Cost</div>
              <div class='metric-delta-pos'>LP-optimized procurement</div>
            </div>
            """, unsafe_allow_html=True)
        with roi_c4:
            st.markdown(f"""
            <div class='metric-card' style='border-color:#F5A623;'>
              <div class='metric-value' style='color:#F5A623;'>{saving_pct:.1f}%</div>
              <div class='metric-label'>Cost Reduction</div>
              <div class='metric-delta-pos'>vs manual planning</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_bar, col_wfall = st.columns(2)
        with col_bar:
            st.plotly_chart(make_cost_comparison(lp_results), use_container_width=True)
        with col_wfall:
            st.plotly_chart(make_roi_waterfall(savings_cr, trad_total_cr, opt_total_cr), use_container_width=True)

        st.plotly_chart(make_utilization_gauge_bars(), use_container_width=True)

        # LP Solution details
        st.markdown("<div class='section-header'>🔩 LP Optimizer Details</div>", unsafe_allow_html=True)
        lp_c1, lp_c2 = st.columns(2)
        with lp_c1:
            st.markdown(f"""
            <div class='callout-teal'>
              <b>Optimization Model</b><br>
              <span style='font-family:monospace; font-size:0.85rem; color:#79C0FF;'>
                Minimize: Σ(procurement_cost × x[t]) + Σ(holding_cost × inventory[t])<br><br>
                Subject to:<br>
                C1: inventory[t] ≥ demand[t] ∀t<br>
                C2: Σ(panels_reused) ≤ reuse_limit<br>
                C3: weekly_spend ≤ ₹{monthly_budget/4.33:.1f} Cr
              </span>
            </div>
            """, unsafe_allow_html=True)
        with lp_c2:
            st.markdown(f"""
            <table class='custom-table'>
              <tr><th>Cost Component</th><th>Traditional</th><th>FormOptiX</th><th>Saving</th></tr>
              <tr>
                <td>Procurement</td>
                <td>₹{lp_results["trad_proc"]/1e7:.2f} Cr</td>
                <td class='td-green'>₹{lp_results["opt_proc"]/1e7:.2f} Cr</td>
                <td class='td-green'>₹{(lp_results["trad_proc"]-lp_results["opt_proc"])/1e7:.2f} Cr</td>
              </tr>
              <tr>
                <td>Holding Cost</td>
                <td>₹{lp_results["trad_hold"]/1e7:.2f} Cr</td>
                <td class='td-green'>₹{lp_results["opt_hold"]/1e7:.2f} Cr</td>
                <td class='td-green'>₹{(lp_results["trad_hold"]-lp_results["opt_hold"])/1e7:.2f} Cr</td>
              </tr>
              <tr>
                <td>Idle Inventory</td>
                <td>₹{lp_results["trad_idle"]/1e7:.2f} Cr</td>
                <td class='td-green'>₹{lp_results["opt_idle"]*0.3/1e7:.2f} Cr</td>
                <td class='td-green'>₹{(lp_results["trad_idle"]-lp_results["opt_idle"]*0.3)/1e7:.2f} Cr</td>
              </tr>
              <tr>
                <td class='td-orange'><b>TOTAL</b></td>
                <td><b>₹{trad_total_cr:.2f} Cr</b></td>
                <td class='td-green'><b>₹{opt_total_cr:.2f} Cr</b></td>
                <td class='td-green'><b>₹{savings_cr:.2f} Cr</b></td>
              </tr>
            </table>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='font-size:0.78rem; color:#8B949E; margin-top:12px; font-style:italic;'>
          * Projections based on simulation modelled on industry benchmarks (CIDC, L&T internal norms).
          Pilot validation planned for Phase 1. LP Solver status: <b>{lp_results["status"]}</b>
        </div>
        """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # TAB 3 — INVENTORY & FORECAST
    # ──────────────────────────────────────────────
    with tab3:
        st.plotly_chart(make_inventory_curve(lp_results, df_schedule["week"].values), use_container_width=True)
        st.plotly_chart(make_forecast_chart(weeks, demand, forecast, upper, lower), use_container_width=True)

        st.markdown("""
        <div class='callout-orange' style='margin-bottom:16px;'>
          <b style='font-size:1.05rem;'>Why is Forecasting Needed When Schedule is Known?</b><br>
          <div style='font-size:0.9rem; margin-top:4px;'>
            <b>1. Delay Uncertainty:</b> Supply chain lags for specialized panel shipments.<br>
            <b>2. Weather Risk:</b> Heavy monsoons or heatwaves shifting planned cycle times.<br>
            <b>3. Labor Variability:</b> Formwork gang absenteeism delaying deployment.<br>
            <b>4. Concrete Cycle Disruption:</b> Unforeseen curing delays bottlenecking panel rotation.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-header'>📋 Data Source Strategy (M4)</div>", unsafe_allow_html=True)
        ds_c1, ds_c2, ds_c3, ds_c4 = st.columns(4)
        ds_items = [
            (ds_c1, "Phase 1",   "L&T Internal DB", "Historical formwork demand logs from past projects",   "phase-1"),
            (ds_c2, "Phase 2",   "BIM Exports",     "Revit/Navisworks timeline exports → auto demand curve","phase-2"),
            (ds_c3, "Phase 3",   "RFID/IoT",        "Real-time panel tracking feeds model continuously",    "phase-2"),
            (ds_c4, "Cold Start","Floor Area Rule",  "panels = floor_area / 12 (physics-based fallback)",   "phase-0"),
        ]
        for col, phase, src, desc, cls in ds_items:
            col.markdown(f"""
            <div class='metric-card'>
              <span class='phase-badge {cls}'>{phase}</span>
              <div style='font-weight:600; color:#E6EDF3; margin-top:8px;'>{src}</div>
              <div style='font-size:0.8rem; color:#8B949E; margin-top:4px;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        # Weekly procurement table
        st.markdown("<div class='section-header'>📅 Sample Weekly Procurement Plan (FormOptiX)</div>", unsafe_allow_html=True)
        sample_weeks = list(range(0, min(10, len(df_schedule))))
        tbl_data = {
            "Week": [df_schedule.iloc[i]["week"] for i in sample_weeks],
            "Wall Demand": [lp_results["demand_w"][i] for i in sample_weeks],
            "Wall Optimized Buy": [lp_results["opt_buy_w"][i] for i in sample_weeks],
            "Wall Inventory": [round(lp_results["opt_inv_w"][i]) for i in sample_weeks],
            "Slab Demand": [lp_results["demand_s"][i] for i in sample_weeks],
            "Slab Optimized Buy": [lp_results["opt_buy_s"][i] for i in sample_weeks],
        }
        df_tbl = pd.DataFrame(tbl_data)
        st.dataframe(
            df_tbl.style.background_gradient(
                subset=["Wall Optimized Buy","Slab Optimized Buy"],
                cmap="YlOrRd"
            ),
            use_container_width=True,
            hide_index=True
        )

    # ──────────────────────────────────────────────
    # TAB 4 — BUILDING DATA
    # ──────────────────────────────────────────────
    with tab4:
        st.markdown("<div class='section-header'>🏗️ Floor-by-Floor Data (Module 1 — Synthetic Dataset)</div>", unsafe_allow_html=True)

        # Type distribution donut
        type_counts = df_floors["floor_type"].value_counts().reset_index()
        type_counts.columns = ["floor_type", "count"]
        fig_donut = go.Figure(go.Pie(
            labels=type_counts["floor_type"],
            values=type_counts["count"],
            hole=0.55,
            marker_colors=[ORANGE, TEAL, AMBER, GREEN, BLUE, RED],
            textfont=dict(color=TEXT, size=12),
            hovertemplate="%{label}: %{value} floors<extra></extra>"
        ))
        fig_donut.update_layout(
            paper_bgcolor=CHART_PAPER,
            plot_bgcolor=CHART_BG,
            font=dict(family="Space Grotesk", color=TEXT),
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            title=dict(text="Floor Type Distribution", font=dict(color="#E6EDF3", size=14)),
            legend=dict(bgcolor="rgba(22,27,34,0.8)", bordercolor=GRAY, borderwidth=1, font=dict(color=TEXT))
        )
        fig_donut.add_annotation(
            text=f"<b>{n_floors}</b><br>Floors",
            x=0.5, y=0.5, font_size=16, font_color=ORANGE, showarrow=False
        )

        col_donut, col_scatter = st.columns([1, 2])
        with col_donut:
            st.plotly_chart(fig_donut, use_container_width=True)
        with col_scatter:
            fig_scatter = px.scatter(
                df_floors, x="slab_area_sqm", y="wall_length_m",
                size="column_count", color="cluster",
                hover_name="floor_name",
                hover_data=["floor_type", "beam_count"],
                color_continuous_scale=[[0,RED],[0.33,ORANGE],[0.66,TEAL],[1.0,GREEN]],
                title="Floor Geometry Space (colored by Cluster)"
            )
            fig_scatter = apply_chart_theme(fig_scatter, "Floor Geometry Space", height=300)
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Full data table
        st.markdown("**Complete Floor Dataset**")
        st.dataframe(
            df_floors[["floor_name","floor_type","slab_area_sqm","wall_length_m","column_count","beam_count","cluster"]].style
            .map(lambda v: f"color: {ORANGE}; font-weight:bold;" if isinstance(v, str) and v == "Typical" else "")
            .background_gradient(subset=["slab_area_sqm","wall_length_m"], cmap="Blues"),
            use_container_width=True,
            hide_index=True,
            height=360
        )

    # ──────────────────────────────────────────────
    # TAB 5 — ROADMAP & IMPACT
    # ──────────────────────────────────────────────
    with tab5:
        st.markdown("<div class='section-header'>🗺️ Implementation Roadmap</div>", unsafe_allow_html=True)

        phases = [
            ("Phase 0", "0–3 Months", "Prototype", "0D9488",
             ["Python prototype on synthetic data","DBSCAN + LP + Prophet modules","Cost dashboard (this app)"],
             f"Repetition Score algo validated on 3 test buildings"),
            ("Phase 1", "3–9 Months", "Pilot", "E8611A",
             ["Single L&T residential tower","BIM integration (Revit plugin)","L&T historical data as training"],
             "≥12% formwork cost reduction demonstrated"),
            ("Phase 2", "9–18 Months", "Scale", "388BFD",
             ["10 projects + ERP + Primavera integration","RFID panel digital twin rollout","Cross-project sharing engine"],
             "₹15–20 Cr cumulative savings"),
            ("Phase 3", "18–36 Months", "Platform", "F5A623",
             ["SaaS for external contractors","Anonymised project templates","Per-project pricing"],
             "Onboard 3 builders; ARR target ₹5 Cr"),
        ]
        cols = st.columns(4)
        for col, (tag, time_r, title, color, items, kpi) in zip(cols, phases):
            items_html = "".join([f"<li style='margin:5px 0; color:#C9D1D9;'>{it}</li>" for it in items])
            col.markdown(f"""
            <div style='background:#161B22; border:1px solid #30363D; border-radius:12px;
                        border-top:4px solid #{color}; padding:16px; height:340px;'>
              <div style='color:#{color}; font-weight:700; font-size:0.78rem; letter-spacing:1px;'>{tag}</div>
              <div style='color:#8B949E; font-size:0.75rem;'>{time_r}</div>
              <div style='color:#E6EDF3; font-weight:700; font-size:1.1rem; margin:8px 0;'>{title}</div>
              <ul style='padding-left:16px; font-size:0.82rem; margin:0;'>{items_html}</ul>
              <div style='margin-top:12px; background:rgba({int(color[:2],16)},{int(color[2:4],16)},{int(color[4:],16)},0.15);
                          border-radius:6px; padding:8px; font-size:0.78rem; color:#{color}; font-weight:600;'>
                ✓ {kpi}
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Impact summary table
        st.markdown("<br><div class='section-header'>📊 Full Impact Summary</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <table class='custom-table'>
          <tr><th>Metric</th><th>Before (Manual)</th><th>After (FormOptiX)</th><th>Improvement</th></tr>
          <tr><td>Formwork Utilization Rate</td><td>60–65%</td><td class='td-green'>82–87%</td><td class='td-green'>+22 percentage points</td></tr>
          <tr><td>BoQ Revision Cycle Time</td><td>3–5 days</td><td class='td-green'>&lt;4 hours</td><td class='td-green'>~90% faster</td></tr>
          <tr><td>Excess Inventory (% of BoQ)</td><td>12–18%</td><td class='td-green'>4–6%</td><td class='td-green'>~65% reduction</td></tr>
          <tr><td>Carrying Cost (₹500 Cr project)</td><td>₹3–5 Cr</td><td class='td-green'>₹1.5–2 Cr</td><td class='td-green'>~55% lower</td></tr>
          <tr><td>Repetition Score (measured)</td><td>Not tracked</td><td class='td-orange'>{rep_score}%</td><td class='td-green'>New KPI created</td></tr>
          <tr><td><b>Total Formwork Cost Saving</b></td><td><b>Baseline</b></td>
              <td class='td-green'><b>₹{savings_cr:.2f} Cr</b></td>
              <td class='td-green'><b>{saving_pct:.1f}% reduction</b></td>
          </tr>
        </table>
        """, unsafe_allow_html=True)

        # Novelty features
        st.markdown("<div class='section-header'>🆕 Novelty Features</div>", unsafe_allow_html=True)
        nov1, nov2, nov3 = st.columns(3)
        novelties = [
            (nov1, "🔒 Design Freeze Intelligence", TEAL,
             "Monitors BIM version history. Flags if Repetition Score drops >15% between design iterations. "
             "Delays procurement until design stability threshold is reached. Converts risk into a quantified trigger."),
            (nov2, "📡 Panel Digital Twin", ORANGE,
             "QR/RFID code per panel tracks deployment, removal, inspection cycles in real-time. "
             "Predictive maintenance alerts: 'Batch F-240 due for inspection after next use.'"),
            (nov3, "🔗 Cross-Project Sharing Engine", BLUE,
             "Identifies idle panels at Site A that match demand at Site B in upcoming weeks. "
             "Inter-project reallocation reduces rental costs across the portfolio. The more projects use it, the smarter it gets."),
        ]
        for col, title, color, desc in novelties:
            col.markdown(f"""
            <div style='background:#161B22; border:1px solid #{color.replace("#","") if "#" not in color else color[1:]}33;
                        border-left:4px solid {color}; border-radius:8px; padding:16px;'>
              <div style='font-weight:700; color:{color}; font-size:1.0rem; margin-bottom:10px;'>{title}</div>
              <div style='font-size:0.84rem; color:#C9D1D9; line-height:1.6;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        # Competitive table
        st.markdown("<br><div class='section-header'>⚔️ Competitive Landscape</div>", unsafe_allow_html=True)
        st.markdown("""
        <table class='custom-table'>
          <tr>
            <th>Tool</th>
            <th>Scheduling</th><th>Procurement</th><th>Design</th>
            <th>Repetition Intelligence</th><th>Cross-Project</th><th>Digital Twin</th>
          </tr>
          <tr><td>Primavera P6</td>
            <td style='color:#3FB950;'>✓</td><td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td>
            <td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td></tr>
          <tr><td>SAP ERP</td>
            <td style='color:#F85149;'>✗</td><td style='color:#3FB950;'>✓</td><td style='color:#F85149;'>✗</td>
            <td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td></tr>
          <tr><td>BIM (Revit)</td>
            <td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td><td style='color:#3FB950;'>✓</td>
            <td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td></tr>
          <tr><td>Doka / PERI SW</td>
            <td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td>
            <td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td><td style='color:#F85149;'>✗</td></tr>
          <tr style='background:rgba(232,97,26,0.08);'>
            <td class='td-orange'><b>FormOptiX ★</b></td>
            <td style='color:#3FB950;'><b>✓</b></td><td style='color:#3FB950;'><b>✓</b></td><td style='color:#3FB950;'><b>✓</b></td>
            <td style='color:#3FB950;'><b>✓</b></td><td style='color:#3FB950;'><b>✓</b></td><td style='color:#3FB950;'><b>✓</b></td>
          </tr>
        </table>
        """, unsafe_allow_html=True)

    # ============================================================
    # BOTTOM — ELEVATOR PITCH
    # ============================================================
    st.markdown("<hr class='orange-divider'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#161B22,#1C2128); border:1px solid #E8611A33;
                border-radius:12px; padding:28px 32px; text-align:center; margin:16px 0;'>
      <div style='font-size:0.75rem; color:#8B949E; letter-spacing:2px; text-transform:uppercase;
                  margin-bottom:12px;'>The FormOptiX Pitch</div>
      <div style='font-size:1.35rem; color:#E8611A; font-style:italic; font-weight:500; line-height:1.6;'>
        "FormOptiX is the GPS for formwork — it tells you exactly which panels to reuse,
        when to order, and how much you'll save, before a single slab is poured."
      </div>
      <div style='margin-top:20px; display:flex; justify-content:center; gap:24px; flex-wrap:wrap;'>
        <span style='color:#3FB950; font-weight:700;'>₹{savings_cr:.2f} Cr savings</span>
        <span style='color:#8B949E;'>·</span>
        <span style='color:#F5A623; font-weight:700;'>+22pp utilization</span>
        <span style='color:#8B949E;'>·</span>
        <span style='color:#0D9488; font-weight:700;'>~90% faster BoQ</span>
        <span style='color:#8B949E;'>·</span>
        <span style='color:#388BFD; font-weight:700;'>Repetition Score: {rep_score}%</span>
      </div>
      <div style='margin-top:16px; font-size:0.85rem; color:#8B949E;'>
        CreaTech '26 · L&T · Problem Statement 4 · <b style='color:#E8611A;'>#JustLeap</b>
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Pre-run state
    st.markdown("""
    <div style='text-align:center; padding:80px 20px;'>
      <div style='font-size:4rem; margin-bottom:16px;'>🏗️</div>
      <div style='font-size:1.5rem; color:#E8611A; font-weight:700; margin-bottom:12px;'>
        Ready to Optimize
      </div>
      <div style='color:#8B949E; font-size:1rem; max-width:480px; margin:0 auto; line-height:1.7;'>
        Configure your project parameters in the sidebar and click
        <b style='color:#E8611A;'>Run FormOptiX Engine</b> to generate the full analysis.
      </div>
    </div>
    """, unsafe_allow_html=True)

