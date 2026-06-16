from dotenv import load_dotenv
import os

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain import hub
import yfinance as yf

load_dotenv()

llm = ChatGroq(model="llama3-70b-8192", temperature=0)

tools_list = []

@tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice")
    return str(price)

@tool
def get_stock_history(ticker: str, period: str = "1mo") -> str:
    """Get stock price history. Period can be 1d, 5d, 1mo, 3mo, 6mo, 1y."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist["Close"].tail(10).to_string()

@tool
def get_market_valuation_of_private_company(company_name: str) -> str:
    """Return the market valuation of a private company in billion USD."""
    company_valuations = {
        "SpaceX": 137.0,
        "Stripe": 95.0,
        "Airbnb": 100.0,
    }
    valuation = company_valuations.get(company_name, 0.0)
    return f"{valuation} billion USD"

@tool
def compare_companies(company1: str, company2: str) -> str:
    """Compare market valuations of two private companies."""
    company_valuations = {
        "SpaceX": 137.0,
        "Stripe": 95.0,
        "Airbnb": 100.0,
    }
    v1 = company_valuations.get(company1, 0.0)
    v2 = company_valuations.get(company2, 0.0)
    return f"{company1}: {v1}B USD vs {company2}: {v2}B USD"

tools = [get_stock_price, get_stock_history, get_market_valuation_of_private_company, compare_companies]

prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Interactive CLI loop
print("Finance Agent ready! Type 'exit' to quit.\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    result = agent_executor.invoke({"input": user_input})
    print(f"\nAgent: {result['output']}\n")