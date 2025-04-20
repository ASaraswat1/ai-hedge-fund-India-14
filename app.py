
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backtester import Backtester

# Try to import all available agents
from agents.portfolio_manager import portfolio_management_agent
from agents.michael_burry import michael_burry_agent
from agents.peter_lynch import peter_lynch_agent
from agents.phil_fisher import phil_fisher_agent
from agents.cathie_wood import cathie_wood_agent
from agents.charlie_munger import charlie_munger_agent
from agents.bill_ackman import bill_ackman_agent
from agents.ben_graham import ben_graham_agent
from agents.warren_buffett import warren_buffett_agent
from agents.fundamentals import fundamentals_agent
from agents.technicals import technical_analyst_agent
from agents.valuation import valuation_agent
from agents.sentiment import sentiment_agent
from agents.risk_manager import risk_management_agent
from agents.simple_agent import simple_moving_average_agent
from agents.stanley_druckenmiller import stanley_druckenmiller_agent

# API Key setup
import openai
if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
    openai.api_key = st.secrets["openai"]["api_key"]
else:
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key

# Available agents
AGENTS = {
    "Fundamentals": fundamentals_agent,
    "Technicals": technical_analyst_agent,
    "Valuation": valuation_agent,
    "Sentiment": sentiment_agent,
    "Risk Manager": risk_management_agent,
    "Simple Agent (SMA)": simple_moving_average_agent,
    "Portfolio Manager (LangGraph)": portfolio_management_agent,
    "Michael Burry": michael_burry_agent,
    "Peter Lynch": peter_lynch_agent,
    "Phil Fisher": phil_fisher_agent,
    "Cathie Wood": cathie_wood_agent,
    "Charlie Munger": charlie_munger_agent,
    "Bill Ackman": bill_ackman_agent,
    "Ben Graham": ben_graham_agent,
    "Warren Buffett": warren_buffett_agent,
    "Stanley Druckenmiller": stanley_druckenmiller_agent
}

st.set_page_config(page_title="AI Hedge Fund (India)", layout="wide")
st.title("🤖📈 AI Hedge Fund Simulator for Indian Stocks 🇮🇳")

with st.sidebar:
    st.header("Configuration")
    ticker = st.text_input("Indian Stock Ticker (Yahoo format)", value="RELIANCE.NS")
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
    end_date = st.date_input("End Date", value=datetime.now())
    agent_choices = st.multiselect("Select Strategy Agent(s)", list(AGENTS.keys()), default=["Portfolio Manager (LangGraph)"])
    initial_capital = st.number_input("Initial Capital (INR)", min_value=10000, value=100000)

if st.button("Run Backtest"):
    with st.spinner("Running strategy..."):
        try:
            selected_agent = AGENTS[agent_choice]
            bt = Backtester(
                agent=selected_agent,
                tickers=[ticker],
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                initial_capital=initial_capital
            )
            result_df, stats = bt.run()
            st.subheader("📈 Strategy Performance")
            st.line_chart(result_df.set_index("Date")["Portfolio Value"])
            st.subheader("📊 Summary Stats")
            st.dataframe(stats)
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("## 📅 Get Trading Decisions by Date or Range")
query_ticker = st.text_input("Ticker for on-demand strategy query", value="RELIANCE.NS", key="query_ticker")
query_start = st.date_input("Start Date for Query", value=datetime.now() - timedelta(days=30), key="query_start")
query_end = st.date_input("End Date for Query", value=datetime.now(), key="query_end")
query_agents = st.multiselect("Select Agents for Query", list(AGENTS.keys()), default=["Portfolio Manager (LangGraph)"], key="query_agents")

if st.button("Get Strategy Decisions"):
    with st.spinner("Running strategy queries..."):
        for agent_name in query_agents:
            try:
                df = yf.download(query_ticker, start=query_start, end=query_end, progress=False)
                if df.empty:
                    st.warning(f"No data for {query_ticker} in selected range.")
                    continue
                df = df.rename(columns={"Adj Close": "Close"}) if "Adj Close" in df.columns else df
                df["Date"] = df.index
                selected_agent = AGENTS[agent_name]
                df["Signal"] = selected_agent(df)
                df["Action"] = df["Signal"].map({1: "BUY", 0: "HOLD"})
                st.markdown(f"### 🤖 {agent_name} Strategy Signals")
                st.dataframe(df[["Date", "Close", "Signal", "Action"]])
            except Exception as e:
                st.error(f"Agent {agent_name} failed: {e}")


# --- Combined Voting + Export Section ---

st.markdown("## 📅 Get Trading Decisions by Date or Range")
query_ticker = st.text_input("Ticker for on-demand strategy query", value="RELIANCE.NS", key="query_ticker")
query_start = st.date_input("Start Date for Query", value=datetime.now() - timedelta(days=30), key="query_start")
query_end = st.date_input("End Date for Query", value=datetime.now(), key="query_end")
query_agents = st.multiselect("Select Agents for Query", list(AGENTS.keys()), default=["Portfolio Manager (LangGraph)"], key="query_agents")

if st.button("Get Strategy Decisions"):
    with st.spinner("Running strategy queries..."):
        df = yf.download(query_ticker, start=query_start, end=query_end, progress=False)
        if df.empty:
            st.warning(f"No data for {query_ticker} in selected range.")
        else:
            df = df.rename(columns={"Adj Close": "Close"}) if "Adj Close" in df.columns else df
            df["Date"] = df.index

            signal_df = pd.DataFrame()
            signal_df["Date"] = df.index

            for agent_name in query_agents:
                try:
                    agent_df = df.copy()
                    selected_agent = AGENTS[agent_name]
                    signal_df[agent_name] = selected_agent(agent_df)
                except Exception as e:
                    st.error(f"Agent {agent_name} failed during voting: {e}")

            if not signal_df.empty:
                signal_df["Vote_Sum"] = signal_df[query_agents].sum(axis=1)
                signal_df["Combined_Decision"] = (signal_df["Vote_Sum"] >= len(query_agents) / 2).astype(int)
                signal_df["Action"] = signal_df["Combined_Decision"].map({1: "BUY", 0: "HOLD"})

                st.markdown("### 🧠 Combined Decision (Voting)")
                st.dataframe(signal_df[["Date", "Combined_Decision", "Action"]])

                csv = signal_df.to_csv(index=False).encode()
                st.download_button("📥 Download Combined Decision CSV", csv, "combined_decision.csv", "text/csv")
