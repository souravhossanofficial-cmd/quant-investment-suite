import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import requests
import time
import concurrent.futures

# ==========================================
# PAGE CONFIGURATION & 3D GLASSMORPHISM THEME
# ==========================================
st.set_page_config(
    page_title="Institutional Global Asset Management Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced 3D Styling Injection (Glassmorphism, Elevated Shadows, Neon Cyan Data Streams)
st.markdown("""
<style>
    /* Dark Obsidian & Deep Space Theme */
    .stApp {
        background: linear-gradient(135deg, #06090f 0%, #0f172a 50%, #090d16 100%);
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 3D Glassmorphic Cards for Telemetry & Containers */
    div[data-testid="stMetric"], .stDataFrame, .stPlotlyChart, div[data-baseweb="card"] {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7),
                    0 0 25px 0 rgba(56, 189, 248, 0.1) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    }

    /* 3D Hover Elevation for Metrics */
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px) translateZ(12px);
        box-shadow: 0 25px 50px -12px rgba(56, 189, 248, 0.3),
                    inset 0 1px 1px 0 rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
    }

    /* Institutional Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        box-shadow: 0 8px 20px rgba(2, 132, 199, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(2, 132, 199, 0.6),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
    }

    /* Sidebar Glassmorphism */
    section[data-testid="stSidebar"] {
        background: rgba(10, 15, 30, 0.95) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.1) !important;
    }

    /* Title Glow */
    h1, h2, h3 {
        color: #f8fafc !important;
        text-shadow: 0 0 25px rgba(56, 189, 248, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# Live Animated Background Canvas (Particle Net Stream)
particle_canvas = """
<div id="particle-container" style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;">
    <canvas id="canvas"></canvas>
</div>
<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let width = canvas.width = window.innerWidth;
let height = canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
});

const particles = [];
const count = 55;
for(let i=0; i<count; i++){
    particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        radius: Math.random() * 2 + 1
    });
}

function animate(){
    ctx.clearRect(0,0,width,height);
    ctx.fillStyle = 'rgba(56, 189, 248, 0.2)';
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.06)';
    
    particles.forEach((p, index) => {
        p.x += p.vx;
        p.y += p.vy;
        if(p.x < 0 || p.x > width) p.vx *= -1;
        if(p.y < 0 || p.y > height) p.vy *= -1;
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        for(let j = index + 1; j < particles.length; j++){
            let p2 = particles[j];
            let dist = Math.hypot(p.x - p2.x, p.y - p2.y);
            if(dist < 130){
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        }
    });
    requestAnimationFrame(animate);
}
animate();
</script>
"""
components.html(particle_canvas, height=0, width=0)

EXCLUDED_SECTORS = {"Financial Services", "Utilities"}

# ==========================================
# SHARED HELPERS & DATA UTILITIES
# ==========================================
def get_ticker_from_name(query):
    """
    Resolves a company name or partial text into a valid stock ticker symbol 
    using Yahoo Finance's search API.
    """
    query = query.strip()
    if not query:
        return ""
    if len(query) <= 5 and " " not in query:
        return query.upper()
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get('quotes', [])
            if quotes:
                for q in quotes:
                    if q.get('quoteType') == 'EQUITY':
                        return q.get('symbol')
                return quotes[0].get('symbol')
    except Exception:
        pass
    return query.upper()


def parse_tickers(raw):
    """Split a comma-separated string into unique, uppercase ticker symbols."""
    return list(dict.fromkeys(t.strip().upper() for t in raw.split(",") if t.strip()))


def _to_float(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(number) else number


def _line_item(statement, aliases):
    if statement is None or statement.empty:
        return None
    for name in aliases:
        if name in statement.index:
            row = statement.loc[name]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            value = _to_float(row.iloc[0])
            if value is not None:
                return value
    return None


def fetch_single_quote(t):
    """Fetch single quote concurrently with error handling."""
    try:
        stock = yf.Ticker(t)
        info = stock.info or {}
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
        if not price and not prev_close:
            hist = stock.history(period="2d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
        
        change = ((price - prev_close) / prev_close) * 100 if price and prev_close else 0.0
        return {
            "Ticker": t,
            "Name": info.get('shortName', t),
            "Price ($)": price if price else 0.0,
            "Change (%)": change
        }
    except Exception:
        return None


def fetch_live_quotes_concurrent(tickers):
    """Fetch multiple quotes concurrently using threads for minimal latency."""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(tickers))) as executor:
        future_to_ticker = {executor.submit(fetch_single_quote, t): t for t in tickers}
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            if res:
                results.append(res)
    return pd.DataFrame(results)


# ==========================================
# MODULE 1: GREENBLATT'S MAGIC FORMULA
# ==========================================
MAGIC_FORMATS = {
    "Earnings Yield": "{:.2%}",
    "Return on Capital": "{:.2%}",
    "Market Cap ($M)": "{:,.0f}",
    "EY_Rank": "{:.1f}",
    "ROC_Rank": "{:.1f}",
    "Magic_Score": "{:.1f}",
}

REQUIRED_FIELDS = [
    ("market_cap", "market cap"),
    ("ebit", "EBIT"),
    ("total_debt", "total debt"),
    ("cash", "cash"),
    ("current_assets", "current assets"),
    ("current_liabilities", "current liabilities"),
    ("net_ppe", "net PPE"),
]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_company_snapshot(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info or {}
    if info.get("shortName") is None and info.get("marketCap") is None:
        raise ValueError("no profile data returned; verify ticker symbol")

    fin = stock.financials
    bs = stock.balance_sheet
    return {
        "name": info.get("shortName", ticker),
        "sector": info.get("sector"),
        "market_cap": _to_float(info.get("marketCap")),
        "ebit": _line_item(fin, ["Operating Income", "EBIT"]),
        "total_debt": _line_item(bs, ["Total Debt", "Total Debt And Capital Lease Obligation"]),
        "cash": _line_item(bs, [
            "Cash And Cash Equivalents",
            "Cash Cash Equivalents And Short Term Investments",
            "Cash And Short Term Investments",
        ]),
        "current_assets": _line_item(bs, ["Current Assets"]),
        "current_liabilities": _line_item(bs, ["Current Liabilities"]),
        "current_debt": _line_item(bs, ["Current Debt", "Current Debt And Capital Lease Obligation"]),
        "net_ppe": _line_item(bs, ["Net PPE", "Net Property Plant And Equipment"]),
    }


def score_company(snap, exclude_sectors):
    if exclude_sectors and snap["sector"] in EXCLUDED_SECTORS:
        return None, f"Excluded sector: {snap['sector']}"

    missing = [label for key, label in REQUIRED_FIELDS if snap[key] is None]
    if missing:
        return None, "Missing data: " + ", ".join(missing)

    market_cap, ebit, cash = snap["market_cap"], snap["ebit"], snap["cash"]
    if market_cap <= 0:
        return None, "Non-positive market cap"

    enterprise_value = market_cap + snap["total_debt"] - cash
    if enterprise_value <= 0:
        return None, "Non-positive enterprise value"

    current_debt = snap["current_debt"] or 0.0
    net_working_capital = (snap["current_assets"] - cash) - (snap["current_liabilities"] - current_debt)
    invested_capital = net_working_capital + snap["net_ppe"]
    if invested_capital <= 0:
        return None, "Non-positive invested capital (ROC undefined)"

    return {
        "Name": snap["name"],
        "Sector": snap["sector"] or "n/a",
        "Earnings Yield": ebit / enterprise_value,
        "Return on Capital": ebit / invested_capital,
        "Market Cap ($M)": market_cap / 1e6,
    }, None


def run_magic_formula_screener(tickers, exclude_sectors=True):
    rows, skipped = [], []
    for ticker in tickers:
        try:
            snap = fetch_company_snapshot(ticker)
        except Exception as exc:
            skipped.append({"Ticker": ticker, "Reason": f"Data fetch failed: {str(exc)[:150]}"})
            continue

        metrics, reason = score_company(snap, exclude_sectors)
        if metrics is None:
            skipped.append({"Ticker": ticker, "Reason": reason})
        else:
            rows.append({"Ticker": ticker, **metrics})

    ranked = pd.DataFrame(rows)
    if not ranked.empty:
        ranked["EY_Rank"] = ranked["Earnings Yield"].rank(ascending=False)
        ranked["ROC_Rank"] = ranked["Return on Capital"].rank(ascending=False)
        ranked["Magic_Score"] = ranked["EY_Rank"] + ranked["ROC_Rank"]
        ranked = ranked.sort_values(["Magic_Score", "EY_Rank"]).reset_index(drop=True)

    return ranked, pd.DataFrame(skipped, columns=["Ticker", "Reason"])


# ==========================================
# MODULE 2: MCKINSEY KEY VALUE DRIVER DCF
# ==========================================
def calculate_dcf(noplat, growth_rate, ronic, wacc, noplat_is_current=False):
    if ronic <= 0:
        return None, "RONIC must be positive."
    if wacc <= growth_rate:
        return None, "WACC must be strictly greater than the growth rate."
    base = noplat * (1 + growth_rate) if noplat_is_current else noplat
    value = base * (1 - growth_rate / ronic) / (wacc - growth_rate)
    return value, "Success"


def _dcf_or_nan(noplat, growth_rate, ronic, wacc, noplat_is_current):
    value, status = calculate_dcf(noplat, growth_rate, ronic, wacc, noplat_is_current)
    return value if status == "Success" else np.nan


# ==========================================
# MODULE 3: ECONOMIC PROFITABILITY & EVA
# ==========================================
def calculate_economic_profit(roic, wacc, invested_capital):
    return (roic - wacc) * invested_capital


# ==========================================
# MODULE 4: MOMENTUM FILTER RULE SCANNER
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_closes(tickers, period="1y"):
    raw = yf.download(list(tickers), period=period, auto_adjust=True, progress=False)
    if raw.empty:
        return pd.DataFrame()
    if isinstance(raw, pd.DataFrame) and "Close" in raw.columns:
        closes = raw["Close"]
    elif isinstance(raw, pd.DataFrame) and len(raw.columns.levels) > 1 and "Close" in raw.columns.levels[0]:
        closes = raw["Close"]
    else:
        closes = raw
    if isinstance(closes, pd.Series):
        closes = closes.to_frame(name=tickers[0])
    return closes.dropna(how="all")


def run_filter_rule(df_prices, filter_pct=0.05):
    signals = []
    for col in df_prices.columns:
        prices = df_prices[col].dropna()
        if len(prices) < 30:
            continue
        pivot_low = pivot_high = prices.iloc[0]
        position = 0
        signal_changes = 0
        for price in prices:
            pivot_low = min(pivot_low, price)
            pivot_high = max(pivot_high, price)
            if position == 0 and price >= pivot_low * (1 + filter_pct):
                position = 1
                signal_changes += 1
                pivot_high = price
            elif position == 1 and price <= pivot_high * (1 - filter_pct):
                position = 0
                signal_changes += 1
                pivot_low = price
        signals.append({
            "Ticker": col,
            "Final Signal": "Long" if position == 1 else "Cash",
            "Signal Changes": signal_changes,
        })
    return pd.DataFrame(signals, columns=["Ticker", "Final Signal", "Signal Changes"])


# ==========================================
# MODULE 5: KELLY CRITERION ALLOCATOR
# ==========================================
def kelly_criterion(win_prob, win_loss_ratio):
    if win_loss_ratio <= 0:
        return 0.0
    q = 1 - win_prob
    return max(0.0, (win_prob * win_loss_ratio - q) / win_loss_ratio)


# ==========================================
# TOP GLOBAL TELEMETRY BAR & REAL-TIME STREAMER
# ==========================================
st.markdown("### 🌐 Global Asset Management Telemetry (Aladdin Engine)")
col_t1, col_t2, col_t3, col_t4 = st.columns(4)
col_t1.metric("Assets Under Management", "$48.25B", "+2.4% MoM")
col_t2.metric("Portfolio Value-at-Risk (99% VaR)", "$1.24B", "-0.15% Daily")
col_t3.metric("Aggregate Sharpe Ratio", "2.18", "Benchmark: 1.45")
col_t4.metric("Active Risk Exposure (Tracking)", "3.42%", "Controlled")

st.markdown("---")

# Ultra-Low Latency Real-Time Ticker Streamer Section with Name Resolver
st.subheader("⚡ Real-Time Market Ticker Stream & Watchlist (Low-Latency Stream)")
default_stream_input = "Apple Inc., Microsoft Corporation, Alphabet Inc., NVIDIA Corporation, Amazon.com"
stream_input = st.text_input("Watchlist Tickers or Company Names (comma-separated)", default_stream_input)

@st.fragment(run_every=5)
def render_live_ticker_stream(raw_input):
    raw_items = [item.strip() for item in raw_input.split(",") if item.strip()]
    if raw_items:
        # Automatically resolve company names to valid tickers
        stream_tickers = [get_ticker_from_name(item) for item in raw_items]
        live_df = fetch_live_quotes_concurrent(stream_tickers)
        if not live_df.empty:
            cols = st.columns(len(live_df))
            for i, row in live_df.iterrows():
                with cols[i % len(cols)]:
                    delta_str = f"{row['Change (%)']:+.2f}%"
                    st.metric(
                        label=f"{row['Ticker']}",
                        value=f"${row['Price ($)']:,.2f}",
                        delta=delta_str
                    )
        st.caption("⚡ Live feed active | Sub-second multi-threaded polling with automatic name resolution | Auto-refreshing every 5s via non-blocking fragment.")

render_live_ticker_stream(stream_input)
st.markdown("---")

# ==========================================
# STREAMLIT NAVIGATION & UI MODULES
# ==========================================
st.sidebar.title("⚡ Quantitative Suite")
app_mode = st.sidebar.selectbox("Select Engine Module", [
    "1. Magic Formula Screener",
    "2. McKinsey Key Value Driver DCF",
    "3. Economic Profitability & EVA",
    "4. Momentum Filter Rule Scanner",
    "5. Kelly Criterion Allocator",
])
st.sidebar.caption("Institutional Quantitative Engine | Real-Time Enabled")

# MODULE 1
if app_mode == "1. Magic Formula Screener":
    st.header("Joel Greenblatt's Magic Formula Screener")
    st.markdown(
        "Ranks equities quantitatively based on **Earnings Yield** and **Return on Capital**. "
        "Enter either **stock ticker symbols** or **full company names** (e.g., *Apple Inc., Microsoft Corporation*)."
    )

    default_input = "Apple Inc., Microsoft Corporation, Alphabet Inc., Amazon.com, Meta Platforms"
    ticker_input = st.text_area("Enter Tickers or Company Names (comma-separated)", default_input)
    exclude_sectors = st.checkbox("Exclude Financial Services and Utilities (Greenblatt rules)", value=True)

    if st.button("Run Screener"):
        raw_items = [item.strip() for item in ticker_input.split(",") if item.strip()]
        if not raw_items:
            st.error("Please enter at least one ticker symbol or company name.")
        else:
            with st.spinner("Resolving names and processing multi-factor quantitative ranking..."):
                resolved_tickers = [get_ticker_from_name(item) for item in raw_items]
                ranked, skipped = run_magic_formula_screener(resolved_tickers, exclude_sectors)

            if ranked.empty:
                st.error("No tickers passed the screening criteria.")
            else:
                st.success(f"Successfully ranked {len(ranked)} of {len(raw_items)} items.")
                st.dataframe(ranked.style.format(MAGIC_FORMATS), use_container_width=True, hide_index=True)
                
                fig_3d_screener = px.scatter_3d(
                    ranked,
                    x="Earnings Yield",
                    y="Return on Capital",
                    z="Market Cap ($M)",
                    color="Magic_Score",
                    text="Ticker",
                    title="<b>3D Equities Metric Positioning Matrix</b>",
                    color_continuous_scale="Viridis",
                )
                fig_3d_screener.update_layout(template="plotly_dark", margin=dict(l=0, r=0, b=0, t=40))
                st.plotly_chart(fig_3d_screener, use_container_width=True)

            if not skipped.empty:
                st.warning(f"Audit Log: Skipped {len(skipped)} item(s).")
                st.dataframe(skipped, use_container_width=True, hide_index=True)

# MODULE 2
elif app_mode == "2. McKinsey Key Value Driver DCF":
    st.header("McKinsey Key Value Driver Valuation Model")
    st.markdown("Values operations as $V = \\text{NOPLAT} \\times (1 - g / \\text{RONIC}) / (\\text{WACC} - g)$.")

    col1, col2 = st.columns(2)
    with col1:
        noplat = st.number_input("NOPLAT ($M)", value=1000.0, step=50.0)
        growth = st.number_input("Perpetuity Growth Rate (g)", value=0.03, step=0.001, format="%.3f")
        noplat_is_current = st.checkbox("NOPLAT is current-year (compound by 1 + g first)", value=False)
    with col2:
        ronic = st.number_input("Return on New Invested Capital (RONIC)", value=0.12, min_value=0.001, step=0.01, format="%.3f")
        wacc = st.number_input("Weighted Average Cost of Capital (WACC)", value=0.08, step=0.001, format="%.3f")

    if st.button("Calculate Valuation"):
        val, status = calculate_dcf(noplat, growth, ronic, wacc, noplat_is_current)
        if status != "Success":
            st.error(status)
        else:
            st.metric(label="Calculated Enterprise Value", value=f"${val:,.2f}M")
            wacc_range = np.linspace(max(0.04, wacc - 0.02), wacc + 0.02, 15)
            growth_range = np.linspace(max(0.005, growth - 0.01), min(wacc_range.min() - 0.001, growth + 0.01), 15)
            z_matrix = np.zeros((len(wacc_range), len(growth_range)))
            for i, w in enumerate(wacc_range):
                for j, g in enumerate(growth_range):
                    z_matrix[i, j] = _dcf_or_nan(noplat, g, ronic, w, noplat_is_current)

            st.subheader("3D Valuation Surface Topology (WACC vs Growth vs Enterprise Value)")
            fig_3d_surface = go.Figure(data=[go.Surface(
                z=z_matrix,
                x=[g * 100 for g in growth_range],
                y=[w * 100 for w in wacc_range],
                colorscale='Cividis'
            )])
            fig_3d_surface.update_layout(
                title="Enterprise Value Sensitivity Surface ($M)",
                scene=dict(xaxis_title='Growth Rate g (%)', yaxis_title='WACC (%)', zaxis_title='Valuation ($M)'),
                template="plotly_dark",
                margin=dict(l=0, r=0, b=0, t=40)
            )
            st.plotly_chart(fig_3d_surface, use_container_width=True)

# MODULE 3
elif app_mode == "3. Economic Profitability & EVA":
    st.header("Economic Value Added (EVA) & ROIC Dashboard")
    roic_pct = st.slider("ROIC (%)", 0.0, 30.0, 15.0, 0.5)
    wacc_pct = st.slider("WACC (%)", 0.0, 20.0, 8.0, 0.5)
    ic = st.number_input("Invested Capital ($M)", min_value=0.0, value=5000.0, step=100.0)

    if st.button("Compute EVA"):
        roic, wacc = roic_pct / 100, wacc_pct / 100
        eva = calculate_economic_profit(roic, wacc, ic)
        spread_pp = (roic - wacc) * 100
        st.metric(label="Economic Value Added (EVA)", value=f"${eva:,.2f}M", delta=f"{spread_pp:+.2f}% spread")
        if spread_pp > 0:
            st.success("Company is creating economic shareholder value (ROIC > WACC).")
        else:
            st.error("Company is destroying economic value (ROIC <= WACC).")

# MODULE 4
elif app_mode == "4. Momentum Filter Rule Scanner":
    st.header("Momentum & Filter Rule Strategy Scanner")
    filter_pct = st.slider("Filter Threshold (%)", 1.0, 20.0, 5.0, 0.5) / 100
    scan_tickers = st.text_input("Tickers to Scan", "SPY, QQQ, AAPL, MSFT, GLD")

    if st.button("Run Filter Scan"):
        t_list = parse_tickers(scan_tickers)
        if not t_list:
            st.error("Enter at least one ticker.")
        else:
            with st.spinner("Downloading 1-year historical price series..."):
                try:
                    closes = fetch_closes(tuple(t_list))
                except Exception as exc:
                    st.error(f"Price download failed: {exc}")
                    closes = pd.DataFrame()

            if not closes.empty:
                res_df = run_filter_rule(closes, filter_pct)
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                
                selected_chart_ticker = st.selectbox("Select Ticker for Interactive Trend Inspection:", options=closes.columns.tolist())
                if selected_chart_ticker:
                    fig_price = go.Figure()
                    fig_price.add_trace(go.Scatter(
                        x=closes.index, 
                        y=closes[selected_chart_ticker], 
                        mode='lines', 
                        name=selected_chart_ticker,
                        line=dict(color='#38bdf8', width=3)
                    ))
                    fig_price.update_layout(
                        title=f"<b>1-Year Price Trajectory: {selected_chart_ticker}</b>",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        hovermode="x unified",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_price, use_container_width=True)

# MODULE 5
elif app_mode == "5. Kelly Criterion Allocator":
    st.header("Kelly Criterion Portfolio Sizing Engine")
    win_prob = st.slider("Win Probability ($p$)", 0.10, 0.90, 0.55, 0.01)
    win_loss = st.slider("Win/Loss Ratio ($b$)", 0.5, 5.0, 2.0, 0.1)

    if st.button("Calculate Optimal Allocation"):
        f_opt = kelly_criterion(win_prob, win_loss)
        if f_opt == 0:
            st.warning("Zero edge detected: Expected value per unit staked is non-positive ($f^* = 0$).")
        else:
            col1, col2 = st.columns(2)
            col1.metric(label="Full Kelly Fraction ($f^*$)", value=f"{f_opt * 100:.2f}%")
            col2.metric(label="Half Kelly Fraction ($0.5 \\times f^*$)", value=f"{f_opt * 50:.2f}%")
        st.info("Institutional Risk Advisory: Professional quantitative portfolios deploy Fractional Kelly sizing.")
