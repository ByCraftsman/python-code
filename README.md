# Financial Risk & Data Analysis Projects

## Overview
This repository contains personal projects focused on financial risk measurement, credit risk analysis, model validation, and financial data pipeline development.

## Repository Structure
The codebase is organized into two branches:

- **main**: Code developed with practical, real-world applications in mind.
- **fundamentals**: Foundational Python and SQL code used for learning and practice.

## Main Branch Projects

### 1. Market Risk Framework (VaR, ES, and Backtesting)
- **File:** [`Market_Risk_Framework.py`](./Market_Risk_Framework.py)

Built an end-to-end market risk framework in Python for multi-method VaR/ES estimation, rolling-window forecasting, backtesting, and volatility-based model extensions.

#### Portfolio Setting
The test portfolio is intentionally simplified as an equal-weighted cross-asset mix of:

- **KOSPI Composite Index**
- **Kosdaq Composite Index**
- **iShares 7–10 Year Treasury Bond ETF (IEF)**
- **S&P 500 Index**

This portfolio is intended for transparent model comparison rather than replicating an actual trading desk portfolio. 
The goal is to provide a clear setting for comparing model behavior, backtesting performance, and differences in tail-risk sensitivity across market risk approaches.

#### Key Features
- Implements **Historical, Parametric, and Monte Carlo VaR/ES**
- Uses a **rolling-window framework** to update VaR forecasts over time
- Applies a structured validation framework:
  - **Kupiec test** (unconditional coverage)
  - **Christoffersen independence test**
  - **Conditional coverage test**
  - **Basel-style traffic light interpretation**
- Compares **overlapping** and **non-overlapping** backtesting results
- Extends the framework with **EWMA, GARCH(1,1), and Filtered Historical Simulation (FHS)**
- Includes supporting analysis such as:
  - Monte Carlo simulation convergence checks
  - interpretation of tail-risk underestimation
  - analysis of overlap-induced violation clustering

#### Main Insight
Within this portfolio and sample setting, Historical VaR appears to be the best-calibrated model among the baseline models, while Parametric and Monte Carlo VaR tend to underestimate tail risk under normality-based assumptions.

Non-overlapping tests further suggest that part of the observed violation clustering is mechanically induced by overlapping forward PnL construction, leading to a cleaner interpretation of independence and conditional coverage results.

Among the volatility-based extensions, FHS shows the strongest performance, materially improving tail-risk calibration relative to EWMA and standard GARCH.

Overall, Historical VaR remains the strongest model in this framework, with FHS emerging as the most effective volatility-based extension.

#### Project Evolution
This project began as a basic implementation of three VaR methods: Historical, Parametric, and Monte Carlo.

As the framework expanded, the focus moved beyond point estimation toward model validation and backtesting.  
This led to several important extensions:

- moving from single VaR estimates to rolling VaR series
- constructing forward PnL for proper backtesting alignment
- distinguishing estimation inputs from realized backtesting targets
- comparing overlapping and non-overlapping samples
- identifying how overlapping forward PnL can mechanically distort independence test results
- extending static models into volatility-updating and filtered simulation frameworks

Through this process, the project evolved from a basic VaR implementation into a broader market risk validation framework.

#### Modeling Assumptions
- The project is designed for risk-model comparison and interpretation
- The framework uses a 5-day holding period and 99% confidence level
- Mean returns are assumed to be zero for short-horizon parametric and simulation-based VaR
- FX risk is excluded for analytical clarity, although the portfolio includes both Korean and US market instruments

### 2. Credit Risk Analysis for KOSPI Large-Cap Non-Financial Firms
- **Files:**
 - [`Credit_Risk_Preprocessing.py`](./Credit_Risk_Preprocessing.py)
 - [`Credit_Risk_Feature_Engineering.py`](./Credit_Risk_Feature_Engineering.py)
 - [`Credit_Risk_Analysis.py`](./Credit_Risk_Analysis.py)

Built a financial statement-based credit risk analysis framework for large-cap non-financial KOSPI firms using DART financial statement data.

The project constructs a firm-year panel, standardizes key financial statement accounts, calculates core credit-risk ratios, and applies a rule-based screening framework to identify relative financial vulnerability across firms and fiscal years.

#### Sample Construction
The analysis universe is constructed from:

- **KOSPI-listed common stocks**
- **Non-financial firms only**
- **Top 100 firms by market capitalization**
- **Annual consolidated financial statements**
- **Fiscal years 2019–2025**

After excluding firms without full annual financial statement availability over the sample period, the final analysis sample consists of **83 firms over 7 fiscal years**, resulting in a balanced firm-year panel for first-stage credit risk analysis.

#### Key Features
- Builds a firm-year panel from raw DART financial statement data
- Uses standardized IFRS/DART account IDs for financial statement mapping
- Handles IS/CIS overlap through a statement-priority rule
- Calculates core credit-risk ratios across:
  - liquidity
  - leverage
  - profitability
  - finance cost coverage
  - operating cash flow
- Performs ratio summary and extreme value inspection
- Analyzes year-by-year median ratio trends
- Constructs weak-signal indicators for credit vulnerability
- Assigns rule-based risk buckets
- Identifies vulnerable firms for follow-up qualitative review

#### Credit Risk Indicators
The analysis uses the following core ratios:

- **Leverage**: liabilities-to-assets, equity ratio

- **Liquidity**: current ratio, quick ratio, cash ratio

- **Profitability**: ROA, ROE, operating margin

- **Coverage**: finance cost coverage

- **Cash Flow**: CFO-to-assets, CFO-to-liabilities

#### Rule-Based Screening Framework
The project converts individual weak signals into broader credit-risk dimensions:

- **Liquidity weakness**
- **High leverage**
- **Profitability weakness**
- **Weak finance cost coverage**
- **Negative operating cash flow**

Each firm-year observation is assigned a distress flag count based on the number of weak dimensions.  
The final risk bucket is assigned as follows:

- **Low**: 0 weak dimensions
- **Watch**: 1 weak dimension
- **Moderate**: 2 weak dimensions
- **High**: 3 or more weak dimensions

This classification is not intended to represent an official credit rating or default probability model.  
Instead, it is designed as an interpretable first-stage credit risk screening framework.

#### Main Insight
The overall large-cap non-financial KOSPI sample shows relatively stable median credit profiles over 2019–2025.

An additional empirical observation is that the median current ratio of large-cap non-financial KOSPI firms remained around 1.3–1.4, while the median quick ratio was close to 1.0. This suggests that the traditional 2.0 current-ratio benchmark may be too conservative as a mechanical cutoff for this sample, and liquidity should be interpreted relative to firm size, industry characteristics, and cash-flow stability.

However, weak-signal analysis identifies a persistent vulnerable subset of firms, especially in liquidity, finance cost coverage, and cash-flow-related metrics.

Because the sample consists of large listed firms rather than distressed borrowers, the project focuses on **relative vulnerability screening** rather than direct default prediction.

#### Limitations
- The current framework is rule-based and does not estimate default probabilities.
- The sample focuses on large-cap KOSPI non-financial firms, so results should be interpreted as relative vulnerability screening within a generally healthy universe.
- Industry-specific thresholds are not yet fully incorporated.
- Finance cost coverage uses finance costs as a practical proxy for interest-related burden.

### 3. Financial Data ETL Pipeline
- **Files:**
 - [`Building_an_ETL_Data_Pipeline_for_Korean_Listed_Stocks.py`](./Building_an_ETL_Data_Pipeline_for_Korean_Listed_Stocks.py)
 - [`Korean_Equity_Price_FS_ETL.py`](./Korean_Equity_Price_FS_ETL.py)
 - [`Generate_Value_Factors.py`](./Generate_Value_Factors.py)

Built a multi-step data pipeline for Korean listed equities, covering data collection, preprocessing, database loading, and valuation factor generation.

#### Key Features
- Organizes Korean equity data into separate MySQL tables for prices, financial statements, and valuation factors.
- Cleans and normalizes raw equity data, including stock-type classification
- Stores structured datasets in MySQL using UPSERT logic
- Collects adjusted daily price data and annual/quarterly financial statements
- Transforms financial statement data into analysis-ready format
- Generates valuation factors such as PER, PBR, PCR, PSR, and DY
- Applies a TTM approach based on quarterly financial statements

#### Planned Improvements
- Refactor the current Korean equity ETL workflow into a more structured design:
  - an initial full-load pipeline for historical database construction
  - a maintenance pipeline for recurring updates
- Replace some upstream data sources to improve robustness and maintainability
- Reduce duplicated logic by modularizing shared preprocessing steps
  
