import re

with open('try2_real.py', 'r', encoding='utf-8') as f:
    code = f.read()

css_start = code.find('st.markdown("""\n<style>')
css_end = code.find('</style>\n""", unsafe_allow_html=True)') + len('</style>\n""", unsafe_allow_html=True)')

if css_start == -1 or css_end < css_start:
    print("Could not find CSS block!")
    exit(1)

new_css = """
theme_mode = st.sidebar.radio("UI Theme", ["Dark Mode", "Light Mode"], horizontal=True)

if theme_mode == "Light Mode":
    BG = "#F8F9FA"
    BG_SIDEBAR_START = "#F3F4F6"
    BG_SIDEBAR_END = "#E5E7EB"
    TEXT = "#1F2937"
    MUTED = "#6B7280"
    CARD_START = "#FFFFFF"
    CARD_END = "#F8F9FA"
    BORDER = "#E5E7EB"
    BORDER_HOVER = "#D9480F"
    ORANGE = "#D9480F"
    GREEN = "#16A34A"
    RED = "#DC2626"
    TEAL = "#0F766E"
    BLUE = "#2563EB"
    AMBER = "#D97706"
    TABLE_HEADER_BG = "#F3F4F6"
    TABLE_ROW_EVEN = "#F9FAFB"
    TABLE_ROW_HOVER = "rgba(217,72,15,0.06)"
    CHART_BG = "#FFFFFF"
    CHART_PAPER = "#F8F9FA"
    GRAY = "#E5E7EB"
    INPUT_BG = "#FFFFFF"
    INPUT_BORDER = "#D1D5DB"
else:
    BG = "#0D1117"
    BG_SIDEBAR_START = "#111827"
    BG_SIDEBAR_END = "#0D1117"
    TEXT = "#E6EDF3"
    MUTED = "#8B949E"
    CARD_START = "#161B22"
    CARD_END = "#1C2128"
    BORDER = "#30363D"
    BORDER_HOVER = "#E8611A"
    ORANGE = "#E8611A"
    GREEN = "#3FB950"
    RED = "#F85149"
    TEAL = "#0D9488"
    BLUE = "#388BFD"
    AMBER = "#F5A623"
    TABLE_HEADER_BG = "#1C2128"
    TABLE_ROW_EVEN = "#161B22"
    TABLE_ROW_HOVER = "rgba(232,97,26,0.06)"
    CHART_BG = "#161B22"
    CHART_PAPER = "#0D1117"
    GRAY = "#30363D"
    INPUT_BG = "#161B22"
    INPUT_BORDER = "#30363D"

st.markdown(f'''
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  /* ── Base ── */
  html, body, [class*="css"] {{
    font-family: 'Space Grotesk', sans-serif;
    background-color: {BG};
    color: {TEXT};
  }}
  .stApp {{ background: {BG}; }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {BG_SIDEBAR_START} 0%, {BG_SIDEBAR_END} 100%);
    border-right: 1px solid {BORDER};
  }}
  [data-testid="stSidebar"] .stMarkdown h1,
  [data-testid="stSidebar"] .stMarkdown h2,
  [data-testid="stSidebar"] .stMarkdown h3 {{
    color: {ORANGE};
  }}

  /* ── Metric cards ── */
  .metric-card {{
    background: linear-gradient(135deg, {CARD_START} 0%, {CARD_END} 100%);
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px 24px;
    margin: 6px 0;
    transition: border-color 0.2s;
  }}
  .metric-card:hover {{ border-color: {ORANGE}; }}
  .metric-value {{
    font-size: 2.2rem;
    font-weight: 700;
    color: {ORANGE};
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.1;
  }}
  .metric-label {{
    font-size: 0.78rem;
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
  }}
  .metric-delta-pos {{ color: {GREEN}; font-size: 0.85rem; font-weight: 600; }}
  .metric-delta-neg {{ color: {RED}; font-size: 0.85rem; font-weight: 600; }}

  /* ── Section headers ── */
  .section-header {{
    background: linear-gradient(90deg, {ORANGE} 0%, transparent 100%);
    padding: 10px 20px;
    border-radius: 6px;
    margin: 24px 0 16px 0;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: {TEXT} !important;
  }}

  /* ── Alert / callout boxes ── */
  .callout-orange {{
    background: rgba(232, 97, 26, 0.12);
    border-left: 4px solid {ORANGE};
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
  }}
  .callout-green {{
    background: rgba(63, 185, 80, 0.10);
    border-left: 4px solid {GREEN};
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
  }}
  .callout-red {{
    background: rgba(248, 81, 73, 0.10);
    border-left: 4px solid {RED};
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
  }}
  .callout-teal {{
    background: rgba(13, 148, 136, 0.10);
    border-left: 4px solid {TEAL};
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
  }}

  /* ── Title hero ── */
  .hero-title {{
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, {ORANGE} 0%, {AMBER} 60%, {TEXT} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    line-height: 1.05;
  }}
  .hero-sub {{
    color: {MUTED};
    font-size: 1rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 6px;
  }}
  .hero-tag {{
    display: inline-block;
    background: rgba(232, 97, 26, 0.15);
    border: 1px solid {ORANGE};
    color: {ORANGE};
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
    margin-right: 8px;
    margin-top: 12px;
  }}

  /* ── Table styling ── */
  .custom-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    margin: 12px 0;
  }}
  .custom-table th {{
    background: {TABLE_HEADER_BG};
    color: {ORANGE};
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-bottom: 2px solid {ORANGE};
  }}
  .custom-table td {{
    padding: 9px 14px;
    border-bottom: 1px solid {BORDER};
    color: {TEXT};
  }}
  .custom-table tr:nth-child(even) td {{ background: {TABLE_ROW_EVEN}; }}
  .custom-table tr:hover td {{ background: {TABLE_ROW_HOVER}; }}
  .td-green {{ color: {GREEN} !important; font-weight: 600; }}
  .td-orange {{ color: {ORANGE} !important; font-weight: 700; }}

  /* ── Plotly chart container ── */
  .chart-container {{
    background: {CARD_START};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 4px;
    margin: 8px 0;
  }}

  /* ── Phase badges ── */
  .phase-badge {{
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin: 3px 2px;
  }}
  .phase-0 {{ background: rgba(13,148,136,0.2); color: {TEAL}; border: 1px solid {TEAL}; }}
  .phase-1 {{ background: rgba(232,97,26,0.2); color: {ORANGE}; border: 1px solid {ORANGE}; }}
  .phase-2 {{ background: rgba(26,43,74,0.4); color: {BLUE}; border: 1px solid {BLUE}; }}
  .phase-3 {{ background: rgba(245,166,35,0.2); color: {AMBER}; border: 1px solid {AMBER}; }}

  /* ── Divider ── */
  .orange-divider {{
    height: 2px;
    background: linear-gradient(90deg, {ORANGE}, transparent);
    border: none;
    margin: 20px 0;
  }}

  /* ── Streamlit overrides ── */
  .stSlider > div > div > div > div {{ background: {ORANGE} !important; }}
  .stSelectbox > div > div {{ background: {INPUT_BG}; border-color: {INPUT_BORDER}; }}
  .stNumberInput > div > div > input {{ background: {INPUT_BG}; border-color: {INPUT_BORDER}; color: {TEXT}; }}
  div[data-testid="stMetric"] {{
    background: {CARD_START};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 14px;
  }}
  div[data-testid="stMetric"] label {{ color: {MUTED} !important; }}
  div[data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {ORANGE} !important; font-family: 'JetBrains Mono', monospace; }}
  .stButton > button {{
    background: linear-gradient(135deg, {ORANGE}, {AMBER});
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 10px 28px;
    transition: opacity 0.2s;
  }}
  .stButton > button:hover {{ opacity: 0.85; }}
  h1, h2, h3 {{ color: {TEXT} !important; }}
  .stTabs [data-baseweb="tab"] {{ color: {MUTED}; }}
  .stTabs [aria-selected="true"] {{ color: {ORANGE} !important; border-bottom-color: {ORANGE} !important; }}
</style>
''', unsafe_allow_html=True)
"""

code = code[:css_start] + new_css + code[css_end:]

# Now remove the old global variables
var_defs = [
    r'^CHART_BG\s*=\s*".*?"\s*\n',
    r'^CHART_PAPER\s*=\s*".*?"\s*\n',
    r'^ORANGE\s*=\s*".*?"\s*\n',
    r'^AMBER\s*=\s*".*?"\s*\n',
    r'^TEAL\s*=\s*".*?"\s*\n',
    r'^GREEN\s*=\s*".*?"\s*\n',
    r'^RED\s*=\s*".*?"\s*\n',
    r'^BLUE\s*=\s*".*?"\s*\n',
    r'^GRAY\s*=\s*".*?"\s*\n',
    r'^TEXT\s*=\s*".*?"\s*\n',
    r'^MUTED\s*=\s*".*?"\s*\n'
]
for pattern in var_defs:
    code = re.sub(pattern, '', code, flags=re.MULTILINE)
    
print('Replacing hardcoded colors in strings')

# Replace st.markdown(""" with st.markdown(f"""
# Wait, some strings are already f""" or f'''
# Using regex to target st.markdown(""" that are not already f
code = re.sub(r'st\.markdown\(\s*"""', 'st.markdown(f"""', code)
code = re.sub(r"st\.markdown\(\s*'''", "st.markdown(f'''", code)

# Clean up any ff""" mistakes
code = re.sub(r'ff"""', 'f"""', code)
code = re.sub(r"ff'''", "f'''", code)

color_replacements = {
    r'#E8611A': '{ORANGE}',
    r'#F5A623': '{AMBER}',
    r'#3FB950': '{GREEN}',
    r'#F85149': '{RED}',
    r'#0D9488': '{TEAL}',
    r'#388BFD': '{BLUE}',
    r'#8B949E': '{MUTED}',
    r'#C9D1D9': '{TEXT}',
    r'#E6EDF3': '{TEXT}',
    r'#21262D': '{BORDER}',
    r'#30363D': '{GRAY}',
    r'#161B22': '{CARD_START}',
    r'#1C2128': '{CARD_END}',
    r'#111827': '{BG_SIDEBAR_START}',
    r'#0D1117': '{BG}',
    r'#1C4B6B': '{BLUE}',
}

# The replacements need to happen inside f-strings and normal strings
# Python string `replace` doesn't know context, but it's safe to just replace hex codes globally in the file
for hc, vr in color_replacements.items():
    code = re.sub(hc, vr, code, flags=re.IGNORECASE)
    
with open('try2_real.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('Done applying regex replacements.')
