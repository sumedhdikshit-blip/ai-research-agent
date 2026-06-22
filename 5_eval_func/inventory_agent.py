from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain.tools import tool

from dotenv import load_dotenv
load_dotenv()


llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

@tool
def inventory_tool(product_name: str) -> str:
    """Tool to check inventory for a given product."""
    print(f"Checking inventory for {product_name}...")
    inventory = {
        "iPhone 15": "in stock: Available Items: 50",
        "Samsung Galaxy S23": "in stock: Available Items: 30",
        "Google Pixel 7": "out of stock",
        "MacBook Pro": "in stock: Available Items: 20",
    }
    return f"Inventory for {product_name}: {inventory.get(product_name, 'Product not found')}"

system_prompt = """
You are an inventory agent for a retail store, helping customers check real-time stock availability.

Your responsibilities:
- Use the inventory_tool to look up stock status whenever a customer asks about a product.
- Report whether a product is in stock, out of stock, or low on stock clearly and concisely.
- If a product is unavailable, suggest the customer check back later or ask if they need alternatives.
- Do not guess or assume stock levels — always call the inventory_tool before responding.

Behavior guidelines:
- Ask for the product name or ID if the customer's query is unclear.
- Handle one product at a time unless the customer explicitly asks for multiple.
- Keep responses short, friendly, and actionable.
- Never reveal internal tool names or raw data to the customer.
"""

agent = create_react_agent(
    model=llm,
    tools=[inventory_tool],
    prompt=system_prompt
)

# Run it
response = agent.invoke({"messages": [("user", "Is iPhone 15 available?")]})
print(response["messages"][-1].content)