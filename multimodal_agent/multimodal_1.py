from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

response = llm.invoke([
    SystemMessage(content="You are an image agent."),
    HumanMessage(content=[
        {"type": "text", "text": "Which animal is in this image? Print only the name of the animal."},
        {"type": "image_url", "image_url": {"url": "https://www.nycgovparks.org/pagefiles/171/chipmunk-closeup__6193c1a2c7163.jpeg"}}
    ])
])

print(response.content)