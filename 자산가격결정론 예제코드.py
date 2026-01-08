# Define the inputs
net_income = 1000 # net income in dollars
cost_of_equity = 0.1 # cost of equity in percentage
book_value = 5000 # book value of equity in dollars
growth_rate = 0.05 # growth rate of residual income in percentage
discount_rate = 0.08 # discount rate in percentage

# Calculate the residual income for the first year
residual_income_1 = net_income - cost_of_equity * book_value

# Calculate the intrinsic value of equity using a single-stage model
intrinsic_value = book_value + residual_income_1 / (discount_rate - growth_rate)

# Print the results
print("Residual income for the first year: $", round(residual_income_1, 2))
print("Intrinsic value of equity: $", round(intrinsic_value, 2))










# Define variables
book_value = [1000000, 1200000, 1400000, 1600000, 1800000]
required_rate_of_return = 0.1
expected_earnings = 150000
growth_rate = 0.05

# Calculate residual income for each year
residual_income = []
for bv in book_value:
    residual_income.append(expected_earnings - (required_rate_of_return * bv))

# Calculate terminal value
terminal_value = (residual_income[-1] * (1 + growth_rate)) / (required_rate_of_return - growth_rate)

# Calculate total equity value



total_equity_value = sum(book_value) + terminal_value

# Print result
print("Total Equity Value: $", round(total_equity_value, 2))



# Detail https://hbsp.harvard.edu/product/122070-PDF-ENG 
# Define variables
B = [1] # book value normalized to one to compute PBR
div = 0
alpha = [.04, .06, .01, .01, .01] # r in excess of investors' required return
re = .1 # required_rate_of_return
ROE = [x + re for x in alpha]
g = .01 # permanent growth rate of residual income
# 0 means no sustainable competitive advantage
RI = [] # residual income
dRI = [] # discounted residual income
for i in range(len(alpha)):
   B.append((1+ROE[i])*B[i] - div)
   RI.append((ROE[i] - re)*B[i])
   dRI.append(RI[-1]/(1+re)**(i+1))

TV = RI[-1]*(1+g)/(re-g) # terminal value
V = B[0] + sum(dRI) + TV # Total equity value
print("Evolution of book values:", [round(b,4) for b in B])
print("Residual incomes:", [round(b,4) for b in RI])
print("Terminal value:", round(TV,4))
print("Total equity value:", round(V,4))


import numpy as np
import pandas as pd

# Create a DataFrame with the financial metrics for each company
data = {
    'Metric': ['Revenue', 'EBITDA', 'Net Income', 'EPS', 'P/E Ratio', 'EV/EBITDA', 'Debt/Equity'],
    'AAPL': [274.5, 82.4, 57.4, 3.31, 31.3, 21.4, 0.94],
    'GOOGL': [182.5, 57.9, 34.3, 49.16, 27.4, 18.8, 0.02],
    'MSFT': [168.1, 68.2, 51.3, 6.62, 32.1, 19.7, 0.67]
}
df = pd.DataFrame(data).set_index('Metric')

# Invert the P/E ratio and EV/EBITDA
df.loc['E/P Ratio'] = 1 / df.loc['P/E Ratio']
df.loc['EBITDA/EV'] = 1 / df.loc['EV/EBITDA']

# Calculate the median and average for each financial metric
df['Median'] = df.loc[:, ['AAPL', 'GOOGL', 'MSFT']].median(axis=1)
df['Average'] = df.loc[:, ['AAPL', 'GOOGL', 'MSFT']].mean(axis=1)

# Calculate the average of the inverted P/E ratio and EV/EBITDA
inverted_pe = df.loc['E/P Ratio', ['AAPL', 'GOOGL', 'MSFT']].mean()
inverted_evebitda = df.loc['EBITDA/EV', ['AAPL', 'GOOGL', 'MSFT']].mean()

# Print the results
print(df)
print(f'Average inverted E/P Ratio: {1/inverted_pe:.2f}')
print(f'Average inverted EBITDA/EV: {1/inverted_evebitda:.2f}')
print(f'Average P/E Ratio: {df.loc["P/E Ratio", "Average"]:.2f}')
print(f'Average EV/EBITDA: {df.loc["EV/EBITDA", "Average"]:.2f}')



import numpy as np
import pandas as pd

class FinancialMetrics:
    def __init__(self, data):
        self.df = pd.DataFrame(data).set_index('Metric')
        self.inverted_pe = None
        self.inverted_evebitda = None
        
    def invert_ratios(self):
        # Invert the P/E ratio and EV/EBITDA
        self.df.loc['E/P Ratio'] = 1 / self.df.loc['P/E Ratio']
        self.df.loc['EBITDA/EV'] = 1 / self.df.loc['EV/EBITDA']
        
    def calculate_metrics(self):
        # Calculate the median and average for each financial metric
        self.df['Median'] = self.df.loc[:, ['AAPL', 'GOOGL', 'MSFT']].median(axis=1)
        self.df['Average'] = self.df.loc[:, ['AAPL', 'GOOGL', 'MSFT']].mean(axis=1)

        # Calculate the average of the inverted P/E ratio and EV/EBITDA
        self.inverted_pe = self.df.loc['E/P Ratio', ['AAPL', 'GOOGL', 'MSFT']].mean()
        self.inverted_evebitda = self.df.loc['EBITDA/EV', ['AAPL', 'GOOGL', 'MSFT']].mean()
        
    def print_results(self):
        # Print the results
        print(self.df)
        print(f'Average inverted E/P Ratio: {1/self.inverted_pe:.2f}')
        print(f'Average inverted EBITDA/EV: {1/self.inverted_evebitda:.2f}')
        print(f'Average P/E Ratio: {self.df.loc["P/E Ratio", "Average"]:.2f}')
        print(f'Average EV/EBITDA: {self.df.loc["EV/EBITDA", "Average"]:.2f}')

data = {
    'Metric': ['Revenue', 'EBITDA', 'Net Income', 'EPS', 'P/E Ratio', 'EV/EBITDA', 'Debt/Equity'],
    'AAPL': [274.5, 82.4, 57.4, 3.31, 31.3, 21.4, 0.94],
    'GOOGL': [182.5, 57.9, 34.3, 49.16, 27.4, 18.8, 0.02],
    'MSFT': [168.1, 68.2, 51.3, 6.62, 32.1, 19.7, 0.67]
}

fm = FinancialMetrics(data)
fm.invert_ratios()
fm.calculate_metrics()
fm.print_results()















