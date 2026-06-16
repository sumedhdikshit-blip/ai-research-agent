from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

agent = create_react_agent(
    model=llm,
    tools=[],
    prompt="""
    You are an advanced reasoning assistant.
    When solving any problem, always follow these steps:
    
    Step 1 - Identify what is being asked
    Step 2 - List all known values and assumptions
    Step 3 - Write out the formula in plain text (no Latex)
    Step 4 - Substitute values and calculate
    Step 5 - State the final answer clearly
    
    Keep your reasoning clear and easy to follow.
    """
)

print("Reasoning Agent ready! Type 'exit' to quit.\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
    print(f"\nAgent: {result['messages'][-1].content}\n")