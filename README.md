# Financial Risk & Data Analysis Projects

## Overview
This repository contains personal projects focused on financial risk measurement, credit risk analysis, model validation, and financial data pipeline development.

## Repository Structure
The codebase is organized into two branches:

- **main**: Code developed with practical, real-world applications in mind.
- **fundamentals**: Foundational Python and SQL code used for learning and practice.

## Main Branch Projects

### 1. Market Risk Validation Framework

> **Dedicated repository:** [market-risk-validation-framework](https://github.com/ByCraftsman/market-risk-validation-framework)

An end-to-end Python framework for rolling VaR forecasting, forward-PnL backtesting, and comparative model validation.

The dedicated repository contains the current source code, reference data and outputs, figures, methodology, and full documentation. The version retained in this repository is part of the original project collection; future updates are maintained in the separate repository.

### 2. Credit Risk Analysis for KOSPI Large-Cap Non-Financial Firms

> **Dedicated repository:** [kospi-credit-risk-analysis](https://github.com/ByCraftsman/kospi-credit-risk-analysis)

A Python workflow for screening financial vulnerability among large non-financial KOSPI firms using annual consolidated financial statements from OpenDART.

The dedicated repository contains the current source code, saved results, figures, methodology, and limitations. It constructs a panel of 83 firms across 2019–2025, applies transparent screening rules across five financial dimensions, and traces changes in negative operating cash flow through firm transitions and industry counts.

The files retained in this repository reflect an earlier stage of the project. The dedicated repository contains the current version.

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
  
