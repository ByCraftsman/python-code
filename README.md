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

Built an end-to-end market risk framework in Python for VaR/ES estimation and backtesting.

#### Key Features
- Implements Historical, Parametric, and Monte Carlo VaR/ES
- Uses rolling-window estimation to reflect model recalibration over time
- Applies forward-looking backtesting
- Includes a full validation framework:
  - Kupiec test (unconditional coverage)
  - Christoffersen test (independence)
  - Conditional coverage test
  - Basel Traffic Light approach
- Evaluates model weaknesses such as:
  - tail-risk underestimation
  - violation clustering
- Compares overlapping and non-overlapping backtesting results to improve interpretation

#### Main Insight
Empirical results suggest that Parametric and Monte Carlo VaR tend to underestimate tail risk, while Historical VaR produces relatively more stable violation frequencies under the tested setting.

#### Extensions
- **EWMA (RiskMetrics)** extension included
- **GARCH** and **Filtered Historical Simulation (FHS)** planned

### 2. Financial Data ETL Pipeline
- **Files:**
 - [`Building_an_ETL_Data_Pipeline_for_Korean_Listed_Stocks.py`](./Building_an_ETL_Data_Pipeline_for_Korean_Listed_Stocks.py)
 - [`Korean_Equity_Price_FS_ETL.py`](./Korean_Equity_Price_FS_ETL.py)
 - [`Generate_Value_Factors.py`](./Generate_Value_Factors.py)

Built a multi-step data pipeline for Korean listed equities, covering universe construction, price/financial statement preprocessing, and valuation factor generation.

#### Key Features
- Builds a Korean equity master table using multiple domestic data sources
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
  
