import math
from scipy.stats import norm


#define variables
S = 45  # Underlying Price
K = 40  # Strike Price
T = 2   # Time to Expiration
r = 0.1 # Risk-Free Rate
vol = 0.1 # Volatility (σ)

d1 = (math.log(S/K) + (r + 0.5 * vol**2)*T ) / (vol * math.sqrt(T))

d2 = d1 - (vol * math.sqrt(T))

C = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

P = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

print('The value of d1 is: ', round(d1, 4))
print('The value of d2 is: ', round(d2, 4))
print('The price of the call option is: $', round(C, 2))
print('The price of the put option is: $', round(P, 2))


#시각화.
~


#옵션에서 핵심적인 이론이므로, 시간날 때 제대로 코드를 짜는 게 좋을듯.




