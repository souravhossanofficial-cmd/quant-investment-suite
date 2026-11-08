<div align="center">

# ⚡ Institutional Quantitative Investment Suite
### *Production-Grade Multi-Platform Quantitative & Valuation Platform*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://quant-investment-suite.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)]()

</div>

---

## 🌟 Overview

The **Institutional Quantitative Investment Suite** is an elite, high-performance financial engineering and portfolio management application. Designed with the architectural rigor of top-tier asset management firms (such as BlackRock's Aladdin and JPMorgan Chase), it combines institutional financial modeling principles—including **Joel Greenblatt’s Magic Formula**, **McKinsey Key Value Driver DCF**, **Economic Value Added (EVA)**, **Momentum Filter Rules**, and **Kelly Criterion Sizing**—into an immersive, 3D glassmorphic web terminal accessible across all devices.

---

## 🚀 Key Architectural Features

* **🌐 Global Portfolio Telemetry Bar**: Real-time tracking of Assets Under Management (AUM), Value-at-Risk (VaR), Sharpe Ratios, and Active Risk Exposure.
* **✨ 3D Glassmorphic UI & Background Canvas**: Immersive dark-mode obsidian aesthetic featuring dynamic particle-net background animations, translucent blurred cards, and hover elevation shadows.
* **🛡️ Defensive Data Hygiene & Caching**: Robust Yahoo Finance API ingestion with built-in TTL caching (`1-hour`) to prevent rate-limiting, paired with alias-based financial statement row-matching and auditable skip logs.
* **📱 Cross-Platform Accessibility**: Instant deployment on Streamlit Community Cloud with Progressive Web App (PWA) support for native-feeling mobile and desktop execution.

---

## 📊 Core Quantitative Modules

### 1. Joel Greenblatt’s Magic Formula Screener
* Ranks equity universes quantitatively on **Earnings Yield** ($EBIT / Enterprise\ Value$) and **Return on Capital** ($EBIT / Net\ Working\ Capital + Net\ Fixed\ Assets$).
* Enforces institutional sector exclusions (Financial Services & Utilities) and outputs dual-audited tables for ranked companies and skipped exceptions.

### 2. McKinsey Key Value Driver & DCF Valuation Model
* Implements McKinsey's core valuation formula linking operational cash flow, perpetuity growth ($g$), Return on New Invested Capital (RONIC), and Weighted Average Cost of Capital (WACC).
* Features an interactive **3D Surface Topology Plot** and color-coded sensitivity matrices evaluating Enterprise Value across varying macro scenarios.

### 3. Economic Profitability & EVA Dashboard
* Computes real-time Economic Value Added ($\text{EVA} = (\text{ROIC} - \text{WACC}) \times \text{Invested Capital}$) and economic spreads.
* Displays conditional status alerts validating whether a company is actively creating or destroying shareholder value.

### 4. Momentum & Filter Rule Strategy Scanner
* Executes percentage-based filter rule scans over 1-year adjusted daily price histories, tracking running pivot troughs and peaks to generate systematic Long/Cash signals.
* Includes interactive Plotly price-action trend inspection charts.

### 5. Kelly Criterion Portfolio Sizing Engine
* Calculates optimal geometric compounding allocation fractions ($f^*$) based on win probability ($p$) and win/loss ratios ($b$).
* Provides both **Full Kelly** and institutional **Half Kelly** allocations to mitigate destructive drawdown volatility.

---

## 🛠️ Tech Stack

* **Core Language**: Python 3.10+
* **Framework**: Streamlit (Reactive UI & Routing)
* **Data Ingestion**: `yfinance` (Yahoo Finance Market Data)
* **Mathematical Modeling**: `NumPy`, `Pandas`
* **Visualization**: `Plotly` (Interactive 2D/3D Surface & Scatter Plots)
* **Styling**: HTML5/JavaScript Canvas & Custom CSS Glassmorphism

---

## 🚀 Local Installation & Execution

To run the suite locally on your machine:

1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/souravhossanofficial-cmd/quant-investment-suite.git](https://github.com/souravhossanofficial-cmd/quant-investment-suite.git)
   cd quant-investment-suite
