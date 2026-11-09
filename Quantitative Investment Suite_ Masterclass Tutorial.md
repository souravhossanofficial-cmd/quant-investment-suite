[Why](#why)[Audience](#who)[1 Setup](#m1)[2 Analytics](#m2)[3 Frontier](#m3)[4 VaR](#m4)[5 Black-Litterman](#m5)[6 Factors](#m6)[7 Monte Carlo](#m7)[8 Backtest](#m8)[9 ML](#m9)[10 Microstructure](#m10)[11 Derivatives](#m11)[12 Bonds](#m12)[13 DeFi](#m13)

Masterclass tutorial for the Quantitative Investment Suite

# From hypothesis to risk-controlled portfolio

Thirteen modules, thirteen tools. Each one explains the mathematics, animates it, and follows a real-world case from start to finish.

Course director: Ivy League fintech chair and academic director

## Why use this suite?

### Hypothesis to evidence in minutes

Test an idea on decades of data before any capital is at risk.

### The textbook, running

Every tool implements the formula you read, so theory and practice stay linked.

### The same result on every machine

Containerized environments make a desk, a classroom and a thesis reproduce identical numbers.

### See the exposure, not just the average

Charts show concentration, tail losses and sensitivity that one return figure hides.

## Who this is for

Portfolio analysts

Spot hidden concentration and co-movement across holdings.

Portfolio managers

Build efficient, defensible allocations and explain them.

Risk officers

Set limits with VaR and CVaR, then stress-test them.

Quant analysts and ML quants

Test factor and machine-learning signals without look-ahead bias.

Fintech developers

Ship reproducible analytics as a product, not a notebook.

Derivatives and fixed-income traders

Price, hedge and measure rate and volatility sensitivity.

Students

See each formula move next to a story you can remember.

1

## Setup and the devcontainer

Tool: reproducible workspace. Audience: fintech engineers.

Quant research often fails for a dull reason: the code runs on one laptop and nowhere else. A devcontainer packages Python, the libraries and the app into one Docker image, so every analyst gets identical results.

Docker image + devcontainer.json = one reproducible research environment

**Case: Jun Park, a new analyst at a Singapore hedge fund**

On day one his Python setup breaks on a library version mismatch and eats the morning. The team's devcontainer rebuilds the same environment automatically, so he spends the afternoon on his first real backtest.

**Why use it.** Reproducibility is a control. A result nobody can rerun is not a result.

- Onboard new analysts in a day
- Share research code that runs unchanged
- Reproduce any past model for audit

2

## Data engineering and asset analytics

Tool: correlation heatmap. Audience: portfolio analysts.

Prices become returns because returns are comparable across assets. Correlation then shows which holdings genuinely diversify and which only look different.

rt = ln(Pt / Pt−1) μ = E\[R\] × 252 σ = √Var(R) × √252

**Case: Helena Vance, senior strategist at Apex Capital**

Helena believed her three-stock tech sleeve was diversified. The heatmap showed the names moving together far more than she assumed. She rebalanced toward defensive equities and macro hedges, and the portfolio's real diversification improved.

**Why use it.** Concentration hides in correlation. Two holdings with a high correlation coefficient ρ are, for risk purposes, close to one bet.

- Spot hidden concentration
- Choose hedges that truly move differently
- Check that a diversified list is diversified

3

## Modern portfolio theory and the efficient frontier

Tool: efficient frontier and optimal weights. Audience: asset allocation portfolio managers.

For each level of risk there is a highest-return mix of assets. Those mixes form the efficient frontier. The tangency portfolio maximizes return per unit of risk above the risk-free rate.

Dots are random weight combinations. The curve is the frontier.

maxw (wTμ − rf) / √(wTΣw) subject to Σwi = 1, wi ≥ 0

**Case: Dr. Tariq Al-Mansoor, a $5 billion sovereign mandate**

He simulates 5,000 random weight combinations, plots each by risk and return, and locates the tangency portfolio. The chart shows the real trade-off: a slightly lower Sharpe ratio can buy a meaningfully smaller drawdown, which matters more at this size.

**Why use it.** It turns an allocation debate into a visible choice between risk and return.

- Strategic asset allocation
- Setting a risk budget
- Presenting trade-offs to an investment committee

4

## Risk analytics: VaR and CVaR

Tool: parametric and historical VaR, CVaR. Audience: risk officers.

Standard deviation treats gains and losses alike and assumes a bell curve. VaR answers how bad a normal bad day is. CVaR answers how bad the average outcome is once losses pass that line.

VaR95 = 1.645 × σ × V CVaR = E\[L | L ≥ VaR\]

**Case: Mei Lin, risk officer at a long/short equity fund**

The board limit is a one-day 95% VaR of $200,000 on a $10 million book. With 1% daily volatility, parametric VaR is $164,500, inside the limit. Her CVaR, about $206,000, averages the losses beyond the 95% line and sits above it. She reports both, and treats the historical tail as the stress test that matters.

**Why use it.** VaR says where bad days begin. CVaR says how bad they get, which is the question boards increasingly ask.

- Setting risk limits
- Stress testing
- Comparing parametric and historical estimates

5

## The Black-Litterman model

Tool: Black-Litterman posterior returns. Audience: global macro strategists.

Raw expected returns produce extreme, concentrated portfolios. Black and Litterman start from market equilibrium implied by capitalization, then blend in your explicit views, weighted by your confidence.

Grey: equilibrium prior. Amber: your view. Colored: the posterior.

Π = λΣwmkt E\[R\] = \[(τΣ)−1 + PᵀΩ−1P\]−1 \[(τΣ)−1Π + PᵀΩ−1Q\]

**Case: Lars Engström, global macro strategist**

He starts from equilibrium. His house view is that a large technology stock beats a defensive healthcare stock by 2% next year, with moderate confidence. The posterior tilts toward that view in proportion to his confidence. A weak view produces a small tilt, not an all-in bet.

**Why use it.** It converts a subjective view into a disciplined, diversified allocation and makes the confidence parameter explicit.

- Combine analyst views with market prices
- Avoid corner solutions
- Record which views drove which weights

6

## Factor investing and risk decomposition

Tool: factor betas and alpha by regression. Audience: quantitative analysts.

Returns are largely exposures to common factors: the market, company size and value. A regression separates what a manager earns from known factors from what remains as alpha.

Illustrative exposures. Bar height shows size. Red marks a negative tilt.

Ri − Rf = α + βMKT·MKT + βSMB·SMB + βHML·HML + ε

**Case: Kenji Sato, quant analyst at a pension consultancy**

A fund advertises 4% a year of alpha. Kenji regresses its returns on the three factors. The market beta is 1.2, the size tilt 0.4, and the value tilt is negative. Once those exposures are controlled for, the alpha falls to about 0.8%. Most of the apparent skill was factor exposure the pension could buy far more cheaply.

**Why use it.** Factor decomposition shows whether a manager adds value or repackages risk.

- Performance attribution
- Building factor tilts on purpose
- Testing whether a strategy survives factor adjustment

7

## Monte Carlo simulation with geometric Brownian motion

Tool: simulated price paths. Audience: financial planners.

One forecast is never enough. Geometric Brownian motion grows a price at an expected rate while random shocks scaled by volatility push it around. The percentiles of many simulated paths are what decision makers need.

Log scale. Each line is one simulated path.

St+Δt = St · exp\[(μ − σ²/2)Δt + σ√Δt · Z\], Z \~ N(0,1)

**Case: Amara Okafor, financial planner**

She models a $500,000 portfolio with a 7% expected return and 15% volatility over 30 years, running 10,000 paths. The median sits below the simple average projection, because volatility drags compounded growth. The 5th percentile makes the bad case concrete for her client.

**Why use it.** A single projection hides the range. Simulation shows the probability of outcomes you care about, such as running out of money.

- Retirement planning
- Option pricing
- Scenario analysis

8

## Algorithmic backtesting

Tool: strategy backtester with drawdown analysis. Audience: systematic traders.

A backtest replays a rule on history. A moving-average crossover goes long when the short average is above the long one. A good curve can come from overfitting or from ignoring costs, so always check drawdown and net returns.

Colored line: price. Grey: moving average. Green and red: signals.

Signalt = +1 if SMAshort > SMAlong MDD = mint (Vt / maxs≤t Vs − 1)

**Case: Leo Park, systematic trader**

He backtests a 50-day against 200-day crossover on a broad index over two decades. The rule sidesteps the deepest crashes but whipsaws in choppy markets. Add realistic transaction costs and much of the edge disappears. A strategy is only as good as its worst drawdown, net of costs.

**Why use it.** A backtest shows how a rule would have felt to live with, including the losing stretches that decide whether you keep following it.

- Strategy research
- Cost sensitivity
- Drawdown and recovery analysis

9

## Machine learning for alpha

Tool: machine-learning alpha signals with out-of-sample testing. Audience: ML quants.

Machine learning captures non-linear patterns that linear models miss. Its danger is memorizing noise. Penalties keep parameters small, and validation must respect time: train on the past, test on the future, never shuffle.

Illustrative values. The split keeps time order.

minΘ (1/N) Σ (yi − f(xi; Θ))² + λ‖Θ‖²2

**Case: Nadia Haddad, ML quant**

She trains a random forest on forty technical and macro features. In-sample, the strategy shows a Sharpe ratio of 3.1, which looks extraordinary. Walk-forward out-of-sample it falls to about 0.4. She rebuilds the pipeline with time-ordered splits and a purge gap, and the smaller number is the one she trusts.

**Why use it.** Out-of-sample testing is the one test a model cannot cheat on.

- Alpha signal generation
- Regime classification
- Volatility forecasting

10

## Microstructure and high-frequency analytics

Tool: spread, mid-price and volume imbalance. Audience: execution traders.

Microstructure explains how prices form, one order at a time. The spread is the cost of immediacy. Volume imbalance compares resting buy and sell interest and can hint at very short-term direction, though that edge decays fast.

Illustrative ladder. Bid depth 800 against ask depth 400.

St = Pask − Pbid VI = (Vbid − Vask) / (Vbid + Vask) ∈ \[−1, 1\]

**Case: Ravi Desai, execution trader**

He must sell 50,000 shares without moving the price. Imbalance is (800 − 400) / 1,200 = +0.33, so buyers are ready to absorb size. He posts passive sell orders on the ask side and works the order in pieces, instead of hitting the bid and paying the spread.

**Why use it.** Execution quality is measured in basis points. Knowing when liquidity is on your side saves real money.

- Execution timing
- Spread monitoring
- Liquidity diagnostics

11

## Derivatives pricing and the volatility surface

Tool: option pricing, Greeks and implied volatility smile. Audience: derivatives desks.

Options are priced by building a hedge. A call's value depends on spot, strike, time, rates and volatility. The Greeks measure sensitivity, and implied volatility plotted across strikes forms the smile.

C = S·N(d₁) − K·e−rT·N(d₂) d₁ = \[ln(S/K) + (r + σ²/2)T\] / (σ√T) d₂ = d₁ − σ√T

Δ = N(d₁) Γ = N′(d₁) / (Sσ√T) Vega = S√T·N′(d₁)

**Case: Sofia Marin, derivatives desk**

Spot and strike are both $100, the rate is 5%, volatility 20%, and maturity one year. The model prices the call at $10.45 and delta at 0.64. She buys 0.64 shares for every call she sold to stay hedged. Gamma tells her how fast that hedge drifts, so she rebalances as the stock moves.

**Why use it.** Pricing without hedge ratios is incomplete. The Greeks tell you what to trade to stay neutral.

- Option pricing
- Delta and gamma hedging
- Volatility surface analysis

12

## Fixed income: bond pricing and duration

Tool: bond pricing, Macaulay and modified duration. Audience: fixed-income portfolio managers.

A bond is a stream of cash flows discounted at its yield. Price and yield move in opposite directions along a convex curve. Modified duration gives the approximate percentage price change for a one-point move in yield.

P = Σt=1..n C/(1+y)t + F/(1+y)n Dmod = Dmac / (1+y)

**Case: Oliver Brandt, fixed-income manager at a pension fund**

He holds a 10-year bond with a 5% annual coupon and $100 face value, priced at a 4% yield. Its price is $108.11, Macaulay duration is 8.19 years and modified duration is 7.88. If yields rise one point, the price falls about 7.9%. Ahead of an expected rate rise, he shortens duration to cut that exposure.

**Why use it.** Duration turns a rate forecast into a dollar risk, the language of liability matching.

- Rate-risk management
- Immunizing liabilities
- Comparing bond portfolios

13

## Crypto and DeFi: automated market makers

Tool: impermanent loss calculator. Audience: DeFi liquidity providers.

Decentralized exchanges price tokens with a formula, not an order book. In a constant-product pool the product of reserves stays fixed, so the pool rebalances as prices move. Providers earn fees, but can end up worth less than if they had simply held.

x · y = k IL(r) = 2√r / (1 + r) − 1, where r = Pnew / Pinitial

**Case: Yusuf Rahman, DeFi liquidity provider**

He deposits $10,000 of ETH and $10,000 of USDC into a pool. ETH doubles. The pool is now worth $28,284, while simply holding would be worth $30,000. Impermanent loss is 5.7%, or $1,716. Fees must exceed that loss for providing liquidity to pay off, so he checks fee income against this break-even first.

**Why use it.** Liquidity provision is an options-like position. You need the loss formula to know whether fees are enough.

- Break-even analysis for pools
- Pool selection
- DeFi risk monitoring

## Before you trust a result

Backtests, simulations and models are instruments for thinking, not promises. Real trading adds transaction costs, data errors, regulation and regime change. The best quants ask what would make a result false, then test exactly that. This book is educational and is not investment advice.