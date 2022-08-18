import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
#import matplotlib.pyplot as plt
import plotly.express as px
import yfinance as yf


st.set_page_config(page_title=" portfolio optimizer",
                   page_icon="📈", layout="wide", initial_sidebar_state="auto")


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)
    
st.markdown("<h1 style='text-align: center; color: #61a5c2;'>INVESTMENT PORTFOLIO OPTIMISER</h1>", unsafe_allow_html=True)
# st.title('INVESTMENT PORTFOLIO OPTIMISER')

options = st.multiselect(
    'Choose the stocks',
    ['AAPL', 'GOOG', 'TSLA', 'C'], ['AAPL', 'GOOG', 'TSLA', 'C'])




def download_prices(tickers):

    df = yf.download(tickers.split(), '2020-1-1')['Adj Close']

    df = df[-253:]

    return df



def calculate_variables(df):

    daily_ret = df.pct_change()

    NUM_DAYS = daily_ret.count()

    annual_ret = daily_ret.mean() * NUM_DAYS

    cov_daily = daily_ret.cov()

    cov_annual = cov_daily * NUM_DAYS

    return annual_ret, cov_annual


def calculate_eff_frontier(df, annual_ret, cov_annual):

    NUM_ASSETS = len(df.columns)
    NUM_PORTFOLIOS = 50000

    # empty lists to store returns, volatility and weights of imiginary portfolios
    port_returns = []
    port_volatility = []
    stock_weights = []
    sharpe_ratio = []

    # populate the empty lists with each portfolios returns,risk and weights
    for portfolio in range(NUM_PORTFOLIOS):

        weights = np.random.random(NUM_ASSETS)
        weights /= np.sum(weights)

        returns = np.dot(weights, annual_ret)

        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))

        sharpe = returns / volatility
        sharpe_ratio.append(sharpe)

        port_returns.append(returns)
        port_volatility.append(volatility)
        stock_weights.append(weights)

    # Create a dictionary for Returns and Risk values of each portfolio
    portfolio = {'Returns': port_returns,
                 'Volatility': port_volatility, 'Sharpe Ratio': sharpe_ratio}

    # extend original dictionary to accomodate each ticker and weight in the portfolio
    assets = df.columns

    for counter, asset in enumerate(assets):
        portfolio[asset+' Weight'] = [Weight[counter]
                                      for Weight in stock_weights]

    # make a nice dataframe of the extended dictionary
    df_portfolio = pd.DataFrame(portfolio)

    return df_portfolio

    

def optimize(tickers):

    df = download_prices(tickers)

    annual_ret, cov_annual = calculate_variables(df)

    df_portfolio = calculate_eff_frontier(df, annual_ret, cov_annual)

    # find min Volatility & max sharpe values in the dataframe
    is_min_vol = df_portfolio['Volatility'] == df_portfolio['Volatility'].min()
    is_max_sharpe = df_portfolio['Sharpe Ratio'] == df_portfolio['Sharpe Ratio'].max(
    )

    # use the min, max values to locate and create the two special portfolios
    max_sharpe_port = df_portfolio.loc[is_max_sharpe]
    min_vol_port = df_portfolio.loc[is_min_vol]

    return min_vol_port, max_sharpe_port



# tickers = 'META BTC-USD AMZN NFLX GOOGL TSLA F JPM GLD'

# print(len(options))

if (len(options) < 2):
    st.write('Please select at least two stocks')
else:
    tickers = ' '.join(options)
    min_risk, max_return = optimize(tickers)
    
    st.markdown("<h2 style='text-align: center; color: #c89f9c;'>Stock Performance Analysis</h2>", unsafe_allow_html=True)
    # st.subheader('Stock Performance Analysis')
    
    df = yf.download(tickers.split(), '2020-1-1')['Adj Close']
    df = df[-253:]
    print(options)
    if 'AAPL' in options:
        fig1=px.line(data_frame = df,  y = 'AAPL')
        
        st.subheader('Line Chart : AAPL Weight vs Date ')
        st.plotly_chart(fig1)
        st.subheader('Bar Chart : AAPL Weight vs Date ')
        st.bar_chart(data=df, y='AAPL', use_container_width=True)
        
    if 'GOOG' in options:
        fig2=px.line(data_frame = df,  y = 'GOOG')
        st.subheader('Line Chart : GOOG Weight vs Date ')
        st.plotly_chart(fig2)
        
        st.subheader('Bar Chart : GOOG Weight vs Date ')
        st.bar_chart(data=df, y='GOOG', use_container_width=True)
    if 'TSLA' in options:    
        fig3=px.line(data_frame = df,  y = 'TSLA')
        st.subheader('Line Chart : TSLA Weight vs Date ')
        st.plotly_chart(fig3)
        
        st.subheader('Bar Chart : TSLA Weight vs Date ')
        st.bar_chart(data=df, y='TSLA', use_container_width=True)
    if 'C' in options:
        fig4=px.line(data_frame = df,  y = 'C')
        st.subheader('Line Chart : C Weight vs Date')
        st.plotly_chart(fig4)
        
        st.subheader('Bar Chart : C Weight vs Date ')
        st.bar_chart(data=df, y='C', use_container_width=True)
        
    number = st.number_input('Enter the amount of money to invest')
    
    st.markdown("<h3 style='text-align: center; color: #c7f9cc;'> Minimum Risk</h3>", unsafe_allow_html=True)
    # st.subheader(' Minimum Risk')
    st.table(min_risk)
    st.markdown("<h3 style='text-align: center; color: #c7f9cc;'> Maximum Return</h3>", unsafe_allow_html=True)
    # st.subheader(' Maximum Return')
    st.table(max_return)


# The plot

chartValues = min_risk.columns[3:].values.tolist()
# chartValues = ['AAPL Weight', 'GOOG Weight', 'TSLA Weight', 'C Weight']
print(chartValues)
chartInfo = min_risk.iloc[0, 3:].values.tolist()
# chartInfo = [33, 44, 21, 0]
print(chartInfo)



# The plot
fig = go.Figure(
    go.Pie(
        labels=chartValues,
        values=chartInfo,
        hoverinfo="label+percent",
        textinfo="value"
    ))

st.subheader("Pie chart : Min Risk")
st.plotly_chart(fig)

if ['AAPL'] or ['C'] or ['GOOG'] or ['TSLA'] in options:
    figure = go.Figure(data=[go.Scatter(
    x= ['AAPL','C','GOOG','TSLA'],
    y=chartInfo,
    mode='markers',
    marker=dict(color=['rgb(93, 164, 214)', 'rgb(255, 144, 14)',
               'rgb(44, 160, 101)', 'rgb(255, 65, 54)'],
                size=30)
    )
    ])
    st.subheader('Bubble Chart : Min Risk')
    st.plotly_chart(figure)
    
    

chartValues = max_return.columns[3:].values.tolist()
# chartValues = ['AAPL Weight', 'GOOG Weight', 'TSLA Weight', 'C Weight']
print(chartValues)
chartInfo = max_return.iloc[0, 3:].values.tolist()
# chartInfo = [33, 44, 21, 0]
print(chartInfo)



# The plot
fig = go.Figure(
    go.Pie(
        labels=chartValues,
        values=chartInfo,
        hoverinfo="label+percent",
        textinfo="value"
    ))

st.subheader("Pie chart : Max Return")
st.plotly_chart(fig)

if ['AAPL'] or ['C'] or ['GOOG'] or ['TSLA'] in options:
    figure = go.Figure(data=[go.Scatter(
    x=['AAPL','C','GOOG','TSLA'],
    y= chartInfo,
    mode='markers',
    marker=dict(color=['rgb(93, 164, 214)', 'rgb(255, 144, 14)',
               'rgb(44, 160, 101)', 'rgb(255, 65, 54)'],
                size=30)
    )
    ])
    st.subheader('Bubble Chart : Max Return')
    st.plotly_chart(figure)
    
    


    


    

