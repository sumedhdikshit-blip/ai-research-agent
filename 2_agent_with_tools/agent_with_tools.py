from dotenv import load_dotenv
import os

from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from langchain_groq import ChatGroq
import yfinance as yf

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

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

agent = create_react_agent(model=llm, tools=tools)

print("Finance Agent ready! Type 'exit' to quit.\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
    print(f"\nAgent: {result['messages'][-1].content}\n")