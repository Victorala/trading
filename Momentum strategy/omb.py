import numpy as np
import pandas as pd
import requests
import math
from scipy import stats

stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

my_columns = [
    'Ticker',
    'Price',
    'One-Year price return',
    'Number of shares to buy'
]
final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(","):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['price'],
                    data[symbol]['stats']['year1ChangePercent'],
                    'N/A'
                ],
                index = my_columns
            ),ignore_index=True
        )

final_dataframe.sort_values('One-Year price return', ascending = False, inplace = True)
# Keep only the first 50 stocks
final_dataframe = final_dataframe[:50]
# Updates de index of each stock (1st column) based on the new order
final_dataframe.reset_index(inplace = True)

def portfolio_input():
    global portfolio_size
    portfolio_size = input('enter size: $ ')
    try:
        float(portfolio_size)
    except ValueError:
        print('not a number. \nplease try again')
        portfolio_size = input('enter size: $ ')

portfolio_input()

position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe)):
    final_dataframe.loc[i, 'Number of shares to buy'] = math.floor(position_size/final_dataframe.loc[i,'Price'])

print(final_dataframe)

