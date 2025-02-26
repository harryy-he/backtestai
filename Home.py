import streamlit as st
from ai_helper import BacktestAI

import requests
import pandas as pd

st.set_page_config(
    page_title="BacktestAI",
    layout="wide",
)

# ----------------------------------------------------------------------------
# ------ Home Page

url = "https://www.sec.gov/files/company_tickers_exchange.json"
headers = {"User-Agent": "YourName (your@email.com)", "Accept-Encoding": "gzip, deflate"}
response = requests.get(url, headers=headers)
response = response.json()["data"]

company_info = pd.DataFrame(response, columns=["CIK", "Company Name", "Ticker", "Exchange"])
company_info["Info"] = company_info["Ticker"] + " : " + company_info["Company Name"]

company_dict = dict(zip(company_info.Info, company_info.Ticker))

# ----

with st.sidebar:
    company_select = st.selectbox("Select company to analyse: ", options=company_info["Info"])
    timeframe = st.selectbox("Historical timeframe:", options=["1 year", "2 years", "3 years", "4 years", "5 years"])

    messages = st.container(height=300)
    if prompt := st.chat_input("What strategy would you like to backtest?"):
        messages.chat_message("user").write(prompt)


# ----

if prompt:
    with st.spinner("Loading..."):
        gemini_key = st.secrets["gemini_key"]
        bt = BacktestAI(gemini_key)
        bt.create_strategy(prompt)
        results = bt.run_strategy(f"Download {company_dict[company_select]} for the past {timeframe} on a daily interval.")

        final_val = results[0].round(0)
        pct_change = results[1]
        num_trades = results[2]
        winrate = results[3]
        data = results[4]
        fig = results[5]

        st.plotly_chart(fig)

        strategy_col, bah_col = st.columns(2)

        with strategy_col:
            st.write("Strategy Performance")
            st.metric("Final portfolio value", value=f'${final_val:,.0f}')
            st.metric("Percentage increase (%)", value=f'{(pct_change * 100):.2f}%')
            st.metric("Number of trades", value=num_trades)
            st.metric("Win rate of trades", value=f'{(winrate * 100):.0f}%')

        with bah_col:
            st.write("Buy and Hold Performance")

            final_bah_val = (data["bah_values"].iloc[-1]).round(0)
            pct_change_bah = ((data["bah_values"].iloc[-1]/data["bah_values"].iloc[0]) - 1)

            if pct_change_bah < 0:
                winrate_bah = 0
            else:
                winrate_bah = 100

            st.metric("Final portfolio value", value=f'${data["bah_values"].iloc[-1]:,.0f}')
            st.metric("Percentage increase", value=f'{(pct_change_bah * 100):.2f}%')
            st.metric("Number of trades", value=1)
            st.metric("Win rate of trades", value=f'{winrate_bah}%')

        st.divider()
        url = 'https://discord.gg/YDgu89fA'
        st.write("**We are looking for contributors and developers! If you are interested "
                 "please join my Discord [here](%s)** or contact me on Reddit u/Myztika!" % url)

else:

    st.title("Welcome to BacktestAI")
    st.write("Get started by selecting your desired company and timeframe.")
    st.write("**Note:** BacktestAI is currently in beta, so you will very likely encounter some bugs.")
    st.divider()
    st.subheader("Quick start guide")
    st.write("Try out the following strategy by copying and pasting it into the chat box input on the left:")
    st.code("Buy when RSI is below 40 and sell when RSI is above 60.", language=None)
    st.write("The currently supported indicators are **RSI, MACD, SMA, EMA, Bollinger Bands and OBV**. We also have support "
             "for trading around earnings (say you want to buy 30 days before earnings dates.)")
    st.divider()
    url = 'https://discord.gg/YDgu89fA'
    st.write("**We are looking for contributors and developers! If you are interested "
             "please join my Discord [here](%s) or contact me on Reddit u/Myztika!**" % url)
