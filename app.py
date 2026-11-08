import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

# ==========================================
# PAGE CONFIGURATION & THEME STYLING
# ==========================================
st.set_page_config(
    page_title="Institutional Quantitative Investment Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Yahoo sector labels excluded by Greenblatt's traditional screener rules
EXCLUDED_SECTORS = {"Financial Services", "Utilities"}


# ==========================================
# SHARED HELPERS & DATA UTILITIES
# ==========================================
def parse_tickers(raw):
    """Split a comma-separated string into unique, uppercase ticker symbols."""
    return list(dict.fromkeys(t.strip().upper() for t in raw.split(",") if t.strip()))


def _to_float(value):
    """Safely convert financial statement items to float, returning None on failure."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(number) else number


def _line_item(statement, aliases):
    """Retrieve the most recent value of the first matching alias from a yfinance statement."""
    if statement is None or statement.empty:
        return None
    for name in aliases:
        if name in statement.index:
            row = statement.loc[name]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            value = _to_float(row.iloc[0])  # Column 0 represents the most recent period
            if value is not None:
                return value
    return None


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
    """Pull raw financial inputs for a single ticker with caching to prevent API rate limits."""
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
    """Evaluate financial metrics for a company snapshot; return metrics or skip reason."""
    if exclude_sectors and snap["sector"] in EXCLUDED_SECTORS:
        return None, f"Excluded sector: {snap['sector']}"

    missing = [label for key, label in REQUIRED_FIELDS if snap[key] is None]
    if missing:
        return None, "Missing data: " + ", ".join(missing)

    market_cap, ebit, cash = snap["market_cap"], snap["ebit"], snap["cash"]
    if market_cap <= 0:
        return None, "Non-positive market cap"

    # Enterprise Value = Market Cap + Total Debt - Cash
    enterprise_value = market_cap + snap["total_debt"] - cash
    if enterprise_value <= 0:
        return None, "Non-positive enterprise value"

    # NWC = (Current Assets - Cash) - (Current Liabilities - Current Debt)
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
    """Execute screener across a universe, separating valid results from audit skips."""
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
    """McKinsey Key Value Driver Formula valuation engine."""
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
    """Economic Value Added (EVA) calculation."""
    return (roic - wacc) * invested_capital


# ==========================================
# MODULE 4: MOMENTUM FILTER RULE SCANNER
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_closes(tickers, period="1y"):
    """Fetch daily adjusted close prices for quantitative momentum scanning."""
    raw = yf.download(list(tickers), period=period, auto_adjust=True, progress=False)
    if raw.empty:
        return pd.DataFrame()
    
    # Handle yfinance multi-index vs single dataframe structures
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
    """Execute percentage-based filter rule tracking pivot troughs and peaks."""
    signals = []
    for col in df_prices.columns:
        prices = df_prices[col].dropna()
        if len(prices) < 30:
            continue
        pivot_low = pivot_high = prices.iloc[0]
        position = 0  # 0: Cash, 1: Long
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
    """Calculate optimal Kelly fraction ($f^*$), floored at zero for negative edge."""
    if win_loss_ratio <= 0:
        return 0.0
    q = 1 - win_prob
    return max(0.0, (win_prob * win_loss_ratio - q) / win_loss_ratio)


# ==========================================
# STREAMLIT USER INTERFACE & NAVIGATION
# ==========================================
st.sidebar.title("⚡ Quantitative Engine")
app_mode = st.sidebar.selectbox("Select Tool Module", [
    "1. Magic Formula Screener",
    "2. McKinsey Key Value Driver DCF",
    "3. Economic Profitability & EVA",
    "4. Momentum Filter Rule Scanner",
    "5. Kelly Criterion Allocator",
])
st.sidebar.caption("Data: Yahoo Finance via yfinance. Institutional Research & Quantitative Modeling.")

if app_mode == "1. Magic Formula Screener":
    st.header("Joel Greenblatt's Magic Formula Screener")
    st.markdown(
        "Ranks equities quantitatively based on **Earnings Yield** ($EBIT / Enterprise\ Value$) and "
        "**Return on Capital** ($EBIT / Net\ Working\ Capital + Net\ Fixed\ Assets$), computing a composite score."
    )

    default_tickers = "AAPL, MSFT, GOOGL, AMZN, META, BRK-B, JNJ, V, PG, UNH, HD, MA, DIS, ADBE, NFLX"
    ticker_input = st.text_area("Enter Tickers (comma-separated)", default_tickers)
    exclude_sectors = st.checkbox(
        "Exclude Financial Services and Utilities (Greenblatt criteria)",
        value=True,
    )

    if st.button("Run Screener"):
        tickers = parse_tickers(ticker_input)
        if not tickers:
            st.error("Please enter at least one valid ticker symbol.")
        else:
            with st.spinner("Ingesting financial statements and ranking universe..."):
                ranked, skipped = run_magic_formula_screener(tickers, exclude_sectors)

            if ranked.empty:
                st.error("No tickers passed the screening criteria. Review skipped audit logs below.")
            else:
                st.success(f"Successfully ranked {len(ranked)} of {len(tickers)} tickers.")
                st.dataframe(ranked.style.format(MAGIC_FORMATS), use_container_width=True, hide_index=True)

            if not skipped.empty:
                st.warning(f"Audit Log: Skipped {len(skipped)} ticker(s) due to missing data or sector rules.")
                st.dataframe(skipped, use_container_width=True, hide_index=True)

elif app_mode == "2. McKinsey Key Value Driver DCF":
    st.header("McKinsey Key Value Driver Valuation Model")
    st.markdown(
        "Computes enterprise value via McKinsey's core formula linking operational cash flow, "
        "reinvestment rate, growth, and cost of capital."
    )

    col1, col2 = st.columns(2)
    with col1:
        noplat = st.number_input("NOPLAT ($M)", value=1000.0, step=50.0)
        growth = st.number_input("Perpetuity Growth Rate ($g$)", value=0.03, step=0.001, format="%.3f")
        noplat_is_current = st.checkbox(
            "NOPLAT is current-year (compound by $1 + g$ first)",
            value=False,
            help="The key value driver formula requires next year's NOPLAT projection.",
        )
    with col2:
        ronic = st.number_input(
            "Return on New Invested Capital (RONIC)", value=0.12, min_value=0.001, step=0.01, format="%.3f"
        )
        wacc = st.number_input("Weighted Average Cost of Capital (WACC)", value=0.08, step=0.001, format="%.3f")

    if st.button("Calculate Valuation"):
        val, status = calculate_dcf(noplat, growth, ronic, wacc, noplat_is_current)
        if status != "Success":
            st.error(status)
        else:
            st.metric(label="Calculated Enterprise Value", value=f"${val:,.2f}M")
            if growth / ronic >= 1:
                st.warning(
                    "Warning: Reinvestment rate ($g / RONIC$) is $\ge 100\%$, indicating growth consumes "
                    "more capital than the business generates."
                )

            st.subheader("WACC vs. Growth Sensitivity Matrix")
            wacc_range = np.linspace(wacc - 0.02, wacc + 0.02, 5)
            growth_range = np.linspace(growth - 0.01, growth + 0.01, 5)
            matrix = [
                [_dcf_or_nan(noplat, g, ronic, w, noplat_is_current) for g in growth_range]
                for w in wacc_range
            ]
            df_sens = pd.DataFrame(
                matrix,
                index=[f"WACC: {w:.3f}" for w in wacc_range],
                columns=[f"g: {g:.3f}" for g in growth_range],
            )
            st.dataframe(df_sens.style.format("${:,.2f}M", na_rep="n/a"), use_container_width=True)

elif app_mode == "3. Economic Profitability & EVA":
    st.header("Economic Value Added (EVA) & ROIC Dashboard")
    roic_pct = st.slider("ROIC (%)", 0.0, 30.0, 15.0, 0.5)
    wacc_pct = st.slider("WACC (%)", 0.0, 20.0, 8.0, 0.5)
    ic = st.number_input("Invested Capital ($M)", min_value=0.0, value=5000.0, step=100.0)

    if st.button("Compute EVA"):
        roic, wacc = roic_pct / 100, wacc_pct / 100
        eva = calculate_economic_profit(roic, wacc, ic)
        spread_pp = (roic - wacc) * 100
        st.metric(
            label="Economic Value Added (EVA)",
            value=f"${eva:,.2f}M",
            delta=f"{spread_pp:+.2f}% spread",
        )
        st.caption(f"Spread ($ROIC - WACC$): {spread_pp:+.2f} percentage points")
        if spread_pp > 0:
            st.success("Company is creating economic shareholder value ($ROIC > WACC$).")
        else:
            st.error("Company is destroying economic value ($ROIC \le WACC$).")

elif app_mode == "4. Momentum Filter Rule Scanner":
    st.header("Momentum & Filter Rule Strategy Scanner")
    st.markdown(
        "Executes systematic percentage filter rules on 1 year of adjusted daily closes. "
        "Triggers Long positions on trough breakouts and Cash exits on peak pullbacks."
    )
    filter_pct = st.slider("Filter Threshold (%)", 1.0, 20.0, 5.0, 0.5) / 100
    scan_tickers = st.text_input("Tickers to Scan", "SPY, QQQ, AAPL, MSFT, GLD")

    if st.button("Run Filter Scan"):
        t_list = parse_tickers(scan_tickers)
        if not t_list:
            st.error("Please enter at least one ticker symbol.")
        else:
            with st.spinner("Downloading historical price series..."):
                try:
                    closes = fetch_closes(tuple(t_list))
                except Exception as exc:
                    st.error(f"Price download failed: {exc}")
                    closes = pd.DataFrame()

            if closes.empty:
                st.error("No price data returned. Verify your ticker symbols.")
            else:
                res_df = run_filter_rule(closes, filter_pct)
                scanned = set(res_df["Ticker"])
                not_scanned = [t for t in t_list if t not in scanned]
                if not_scanned:
                    st.warning(
                        "Insufficient price history (<30 trading days): "
                        + ", ".join(not_scanned)
                    )
                if res_df.empty:
                    st.error("No valid tickers had sufficient history to scan.")
                else:
                    st.dataframe(res_df, use_container_width=True, hide_index=True)

elif app_mode == "5. Kelly Criterion Allocator":
    st.header("Kelly Criterion Portfolio Sizing Engine")
    st.markdown("Calculates optimal capital allocation fractions ($f^*$) to maximize long-term geometric compounding.")
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
        st.info(
            "Institutional Note: Professional portfolios apply Fractional Kelly sizing (e.g., Half Kelly) "
            "to mitigate destructive drawdown volatility caused by parameter estimation error."
        )