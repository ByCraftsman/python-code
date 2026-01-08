import yfinance as yf
import statsmodels.api as sm
import getFamaFrenchFactors as gff
import pandas as pd
import numpy as np
import seaborn as sns
from statsmodels.graphics.regressionplots import plot_regress_exog
import matplotlib.pyplot as plt





#OLS Regression
ticker = '^GSPC'
start = '1928-1-1'
end = '2023-1-1'
SP500_data = yf.download(ticker, start, end, auto_adjust=True)
SP500_return = SP500_data['Close'].resample('ME').last().pct_change().dropna()
SP500_return.name = "Month_Rtn"

ff3_monthly = gff.famaFrench3Factor(frequency='m')
ff3_monthly.rename(columns={"date_ff_factors": 'Date'}, inplace=True)
ff3_monthly.set_index('Date', inplace=True)
ff_data = ff3_monthly.merge(SP500_return,on='Date')

X = ff_data[['Mkt-RF', 'SMB', 'HML']]
y = ff_data['Month_Rtn'] - ff_data['RF']
X = sm.add_constant(X)
ff_model = sm.OLS(y, X).fit()
print(ff_model.summary())





#Rolling Window Analysis
def rolling_window_analysis(ticker, start_date, end_date, window_size, stride):

    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    data_monthly = data.resample('M').last()
    monthly_returns = data_monthly['Close'].pct_change().dropna()
    monthly_returns.name = 'Month_Rtn'
    ff3_monthly = gff.famaFrench3Factor(frequency='m')
    ff3_monthly.rename(columns={'date_ff_factors': 'Date'}, inplace=True)
    ff3_monthly.set_index('Date', inplace=True)
    ff_data = ff3_monthly.merge(monthly_returns, on='Date')

    num_periods = int(np.ceil((len(ff_data) - window_size) / stride)) + 1
    results = []
    for i in range(num_periods):
        start = i * stride
        end = start + window_size
        if end > len(ff_data):
            break
        window_data = ff_data.iloc[start:end]
        X = window_data[['Mkt-RF', 'SMB', 'HML']]
        y = window_data['Month_Rtn'] - window_data['RF']
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        results.append((window_data.index[-1], model.rsquared, model.params['Mkt-RF'], model.params['SMB'], model.params['HML']))
    return results

ticker = '^GSPC'
start_date = '1928-01-01'
end_date = '2023-01-01'
window_size = 60
stride = 30

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)
rolling_results = rolling_window_analysis(ticker, start_date, end_date, window_size, stride)
result_df = pd.DataFrame(rolling_results, columns=['Date', 'R-squared', 'Mkt-RF', 'SMB', 'HML'])
print(result_df)





#Comparing Returns
intercept, b1, b2, b3 = ff_model.params
rf = ff_data['RF'].mean()
market_premium = ff3_monthly['Mkt-RF'].mean()
size_premium = ff3_monthly['SMB'].mean()
value_premium = ff3_monthly['HML'].mean()
expected_monthly_return = rf + b1 * market_premium + b2 * size_premium + b3 * value_premium 
expected_yearly_return = expected_monthly_return * 12

start_date = '1928-01-01'
end_date = '2023-01-01'
sp500 = yf.download('^GSPC', start=start_date, end=end_date)
annual_returns = (sp500['Adj Close'].resample('Y').last() / sp500['Adj Close'].resample('Y').first() - 1)
mean_annual_return = np.mean(annual_returns)

start_date = "1928-01-01"
end_date = "2023-01-01"
wilshire = yf.download("^W5000", start=start_date, end=end_date)
wilshire_annual_return = (wilshire["Adj Close"][-1] / wilshire["Adj Close"][0])**(1/(len(wilshire)/252)) - 1

start_date = '1987-01-01'
end_date = '2023-01-01'
russell = yf.download('^RUT', start=start_date, end=end_date)
russell_annual_return = (russell['Adj Close'].resample('Y').last() / russell['Adj Close'].resample('Y').first() - 1)
russell_mean_annual_return = np.mean(russell_annual_return)

start_date = '2008-01-01'
end_date = '2023-01-01'
acwi = yf.download('ACWI', start=start_date, end=end_date)
acwi_annual_return = (acwi['Adj Close'][-1] / acwi['Adj Close'][0])**(1/(len(acwi)/252)) - 1


print("Expected yearly return for fama-french 3 factor model(S&P): " + str(expected_yearly_return))
print("Expected yearly return for s&p500 index: " + str(mean_annual_return))
print("Expected yearly return for wilshire index: " + str(wilshire_annual_return))
print("Mean annual return for Russell 2000: " + str(russell_mean_annual_return))
print("Expected yearly return for MSCI ACWI: " + str(acwi_annual_return))





#Plots
X_correlation = X.drop('const', axis=1)
corr_matrix = X_correlation.corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')


fig = plot_regress_exog(ff_model, 'Mkt-RF', fig=plt.figure(figsize=(12,8)))
fig = plot_regress_exog(ff_model, 'SMB', fig=plt.figure(figsize=(12,8)))
fig = plot_regress_exog(ff_model, 'HML', fig=plt.figure(figsize=(12,8)))


expected_yearly_return = [
    expected_yearly_return,
    mean_annual_return,
    wilshire_annual_return,
    russell_mean_annual_return,
    acwi_annual_return,
]
index_names = [
    "Fama-French 3 Factor",
    "S&P500 Index",
    "Wilshire Index",
    "Russell 2000",
    "MSCI ACWI",
]
df = pd.DataFrame(
    {"Expected Yearly Return": expected_yearly_return},
    index=index_names,
)
ax = df.plot(kind="bar", legend=False, figsize=(10, 6))
ax.set_title("Comparison of Expected Yearly Returns")
ax.tick_params(axis="x", labelsize=12)
ax.tick_params(axis="y", labelsize=10)
ax.set_xticklabels(index_names, rotation=360)
plt.show()






