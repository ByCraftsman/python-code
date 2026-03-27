# Financial Risk & Data Analysis Projects

## Overview
This repository contains personal projects focused on financial risk measurement, model validation, and financial data pipeline development.

## Repository Structure
The codebase is organized into two branches:

- **main**: Code developed with practical, real-world applications in mind.
- **fundamentals**: Foundational Python and SQL code used for learning and practice.

## Main Branch Projects

### 1. Market Risk Framework (VaR & ES)
 - **File:** [`VaR_ES_Framework.py`](./VaR_ES_Framework.py)

Built an end-to-end market risk framework in Python for multi-method VaR/ES estimation, rolling-window forecasting, and regulatory-style backtesting.

#### Key Features
- Implements **Historical, Parametric, and Monte Carlo VaR/ES**
- Uses a **rolling-window framework** to update VaR forecasts over time
- Applies a structured validation framework:
  - **Kupiec test** (unconditional coverage)
  - **Christoffersen independence test**
  - **Conditional coverage test**
  - **Basel Traffic Light approach**
- Compares **overlapping** and **non-overlapping** backtesting results
- Includes supporting analysis such as:
  - Monte Carlo simulation convergence checks
  - interpretation of tail-risk underestimation and violation clustering

#### Main Insight
Empirical results suggest that Historical VaR appears to be the best-calibrated model under the tested setting, while Parametric and Monte Carlo VaR tend to underestimate tail risk, especially in the overlapping backtesting sample.  
Additional non-overlapping tests show that part of the apparent violation clustering is mechanically induced by overlapping forward PnL construction, which improves the interpretation of independence and conditional coverage results.

#### Project Evolution
This project began as a basic implementation of three VaR methods: Historical, Parametric, and Monte Carlo.

As the framework expanded, the focus moved beyond point estimation toward model validation and backtesting.  
This led to several important extensions:

- moving from single VaR estimates to rolling VaR series
- constructing forward PnL for proper backtesting alignment
- distinguishing estimation inputs from realized backtesting targets
- comparing overlapping and non-overlapping samples
- identifying how overlapping forward PnL can mechanically distort independence test results

Through this process, the project evolved from a basic VaR implementation into a broader risk model validation framework.

#### Planned Extensions
- **EWMA (RiskMetrics)** backtesting logic under revision
- **GARCH** planned
- **Filtered Historical Simulation (FHS)** planned
  
### 2. Financial Data ETL Pipeline
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
  
