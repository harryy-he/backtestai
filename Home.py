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

    llm_key = st.text_input("Please enter your Google Gemini API key: ")

    messages = st.container(height=300)
    if prompt := st.chat_input("What strategy would you like to backtest?"):
        messages.chat_message("user").write(prompt)


# ----

if prompt:
    with st.spinner("Loading..."):
        bt = BacktestAI('AIzaSyDH_grQD_PxWbrtEHP4qWuWaEH7auCFngw')
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

else:

    st.header("Welcome to BacktestAI")
    st.write("Get started by selecting your desired company, timeframe, and providing a Google Gemini API key!")

    url = "https://ai.google.dev/gemini-api/docs/api-key"
    st.write("A completely free to use Gemini API Key can be generated [here](%s)." % url)

    st.write("**Note:** BacktestAI is currently in beta, so you will very likely encounter some bugs.")
    st.divider()
    st.write("**We are looking for contributors and developers! If you are interested "
             "please...**")
