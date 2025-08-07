import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import argparse

def trading_bot(starting_cash=10000, time_period='1y', ticker='^GSPC'):
    '''
    Simple trading bot that operates on historical data. 
    The user specifies the ticker, time period and starting cash. 
    If not the default values are 10000$, 1y and S&P 500.
    Buys if the price hits a new low, sells if it hits a new high.
    '''
    stock_df = yf.download(ticker, period=time_period, auto_adjust=False)
    if stock_df.empty:
        print(f'No data found for ticker symbol {ticker}. It may be invalid or delisted')
        return

    stock_df = stock_df.xs(ticker, axis=1, level='Ticker')

    cash = starting_cash
    currentStock = 0
    portfolio_value = []
    index_array = []

    index = 0

    path_file = './portfolio_journal.txt'

    with open(path_file, 'w') as fileWrite:
        for date, value in stock_df['Adj Close'].items():
            if index == 0:
                max_price = value
                min_price = value
                index += 1
                continue
            else:
                # Strategy - buy if the price hits a new local minimum, sell if it hits a new local maximum
                if value < min_price:
                    if value < cash:
                        currentStock += 1 
                        cash -= value
                    min_price = value
                elif value > max_price:
                    if currentStock > 0:
                        currentStock -= 1
                        cash += value
                    max_price = value
                portfolio_value.append(cash + currentStock * value)
                index += 1
                index_array.append(index)
            
            fileWrite.write(f'Current Day is {date}, it is day {index} of trading. Portfolio has {currentStock} shares of {ticker} for {currentStock*value}. Cash is {cash}\n')
        fileWrite.write(f'Final Portfolio value is {portfolio_value[-1]}$')

    # Plotting the portfolio data    
    plt.figure(figsize=(12,8))
    plt.plot(index_array, portfolio_value, linewidth=3)
    plt.title(f'Portfolio Value of {ticker} stock over {time_period} of time excluding weekends', fontsize=18)
    plt.xlabel('Days', fontsize=14)
    plt.ylabel('Portfolio Value ($)', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.grid(True)
    plt.tight_layout()
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:,.0f}$'))
    plt.show()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trading Bot')
    parser.add_argument('--cash', type=float, default=10000, help='Staring cash value ex. 1000')
    parser.add_argument('--period', type=str, default='1y', help='Period of data (ex. 5d, 6mo, 1y, 5y)')
    parser.add_argument('--ticker', type=str, default='^GSPC', help='Ticker symbol ex. AAPL')

    args = parser.parse_args()

    try:
        trading_bot(starting_cash=args.cash, time_period=args.period, ticker=args.ticker)
    except Exception as e:
        print(f'There is an error: {e}')