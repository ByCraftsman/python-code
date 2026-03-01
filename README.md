# Financial Risk & Data Analysis Projects

## Overview
This repository contains personal projects aimed at strengthening my skills in financial risk management and data analysis.

본 레포지토리는 금융 리스크 관리 및 데이터 분석 역량 강화를 위해 개인적으로 작성한 코드들을 정리한 것입니다.

## Repository Structure
The codebase is organized into two branches:

- **main**: Code developed with practical, real-world applications in mind.
- (실무 적용을 목적으로 한 코드)
- **fundamentals**: Foundational Python and SQL code used for learning and practice.
- (기초 파이썬 및 SQL 학습 코드)



## Main Branch Projects

### 1. Risk Measurement (VaR & ES)
 - **File:** [`VaR_ES_Framework.py`](./VaR_ES_Framework.py)
- Implements parametric, historical, and Monte Carlo VaR/ES

- Performs regulatory-style backtesting:
  - Kupiec unconditional coverage test
  - Christoffersen independence test
  - Conditional coverage test
- Identifies model limitations such as fat tails and violation clustering
- Extends static models to dynamic volatility approaches:
  - EWMA (RiskMetrics)
  - GARCH (planned)
  - Filtered Historical Simulation (planned)
- Demonstrates practical risk-model validation aligned with Basel principles

### 2. Financial Data ETL Pipeline
- **Files:**
 - [`Building_an_ETL_Data_Pipeline_for_Korean_Listed_Stocks.py`](./Building_an_ETL_Data_Pipeline_for_Korean_Listed_Stocks.py)
 - [`Korean_Equity_Price_FS_ETL.py`](./Korean_Equity_Price_FS_ETL.py)
 - [`Generate_Value_Factors.py`](./Generate_Value_Factors.py)
- Extracts, transforms, and loads Korean equity market data
- Generates value factors for quantitative analysis


  
