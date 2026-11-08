import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

# ... [KEEP YOUR SHARED HELPERS & MODULE 1 AS THEY ARE] ...

# ==========================================
# MODULE 2: MCKINSEY KEY VALUE DRIVER DCF (WITH PLOTLY HEATMAP)
# ==========================================
# [Inside your Module 2 UI section]:
elif app_mode == "2. McKinsey Key Value Driver DCF":
    st.header("McKinsey Key Value Driver Valuation Model")
    st.markdown(
        "Values operations as $V = \\text{NOPLAT} \\times (1 - g / \\text{RONIC}) / (\\text{WACC} - g)$, "
        "linking growth, return on new capital, and cost of capital."
    )

    col1, col2 = st.columns(2)
    with col1:
        noplat = st.number_input("NOPLAT ($M)", value=1000.0, step=50.0)
        growth = st.number_input("Perpetuity Growth Rate (g)", value=0.03, step=0.001, format="%.3f")
        noplat_is_current = st.checkbox(
            "NOPLAT is current-year (compound by 1 + g first)",
            value=False,
            help="The formula expects next year's NOPLAT. Check this if you entered current year's figure.",
        )
    with col2:
        ronic = st.number_input("Return on New Invested Capital (RONIC)", value=0.12, min_value=0.001, step=0.01, format="%.3f")
        wacc = st.number_input("Weighted Average Cost of Capital (WACC)", value=0.08, step=0.001, format="%.3f")

    if st.button("Calculate Valuation"):
        val, status = calculate_dcf(noplat, growth, ronic, wacc, noplat_is_current)
        if status != "Success":
            st.error(status)
        else:
            st.metric(label="Calculated Enterprise Value", value=f"${val:,.2f}M")
            if growth / ronic >= 1:
                st.warning("Reinvestment rate (g / RONIC) is at or above 100%. Check inputs.")

            st.subheader("WACC vs Growth Sensitivity Matrix")
            wacc_range = np.linspace(wacc - 0.02, wacc + 0.02, 5)
            growth_range = np.linspace(growth - 0.01, growth + 0.01, 5)
            
            matrix = [
                [_dcf_or_nan(noplat, g, ronic, w, noplat_is_current) for g in growth_range]
                for w in wacc_range
            ]
            
            df_sens = pd.DataFrame(
                matrix,
                index=[f"{w:.3f}" for w in wacc_range],
                columns=[f"{g:.3f}" for g in growth_range],
            )
            
            # --- PLOTLY INTERACTIVE HEATMAP UPGRADE ---
            fig_heatmap = px.imshow(
                df_sens,
                labels=dict(x="Perpetuity Growth Rate (g)", y="WACC", color="Enterprise Value ($M)"),
                x=[f"{g:.1%}" for g in growth_range],
                y=[f"{w:.1%}" for w in wacc_range],
                text_auto="${x:,.0f}M",
                color_continuous_scale="RdYlGn",
                title="<b>Enterprise Value Sensitivity Heatmap</b>"
            )
            fig_heatmap.update_layout(
                xaxis_title="Perpetuity Growth Rate (g)",
                yaxis_title="Weighted Average Cost of Capital (WACC)",
                font=dict(family="sans-serif", size=12),
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with st.expander("View Raw Sensitivity Table"):
                st.dataframe(df_sens.style.format("${:,.2f}M", na_rep="n/a"), use_container_width=True)


# ==========================================
# MODULE 4: MOMENTUM FILTER RULE SCANNER (WITH PLOTLY PRICE CHART)
# ==========================================
# [Inside your Module 4 UI section]:
elif app_mode == "4. Momentum Filter Rule Scanner":
    st.header("Momentum & Filter Rule Strategy Scanner")
    st.markdown(
        "A position turns long once price rises the filter % above its trough, and returns to cash "
        "once price falls the filter % below its peak."
    )
    filter_pct = st.slider("Filter Threshold (%)", 1.0, 20.0, 5.0, 0.5) / 100
    scan_tickers = st.text_input("Tickers to Scan", "SPY, QQQ, AAPL, MSFT, GLD")

    if st.button("Run Filter Scan"):
        t_list = parse_tickers(scan_tickers)
        if not t_list:
            st.error("Enter at least one ticker.")
        else:
            with st.spinner("Downloading price history..."):
                try:
                    closes = fetch_closes(tuple(t_list))
                except Exception as exc:
                    st.error(f"Price download failed: {exc}")
                    closes = pd.DataFrame()

            if closes.empty:
                st.error("No price data returned. Check symbols.")
            else:
                res_df = run_filter_rule(closes, filter_pct)
                scanned = set(res_df["Ticker"])
                not_scanned = [t for t in t_list if t not in scanned]
                if not_scanned:
                    st.warning("Insufficient history (<30 trading days): " + ", ".join(not_scanned))
                
                if not res_df.empty:
                    st.dataframe(res_df, use_container_width=True, hide_index=True)
                    
                    # --- PLOTLY INTERACTIVE PRICE CHART UPGRADE ---
                    st.subheader("Asset Price Action & Trend Inspection")
                    selected_chart_ticker = st.selectbox("Select ticker to inspect:", options=closes.columns.tolist())
                    
                    if selected_chart_ticker:
                        fig_price = go.Figure()
                        fig_price.add_trace(go.Scatter(
                            x=closes.index, 
                            y=closes[selected_chart_ticker], 
                            mode='lines', 
                            name=selected_chart_ticker,
                            line=dict(color='#0052cc', width=2)
                        ))
                        fig_price.update_layout(
                            title=f"<b>1-Year Adjusted Close: {selected_chart_ticker}</b>",
                            xaxis_title="Date",
                            yaxis_title="Price ($)",
                            hovermode="x unified",
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig_price, use_container_width=True)
