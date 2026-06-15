from dotenv import load_dotenv
import os, time, warnings
warnings.filterwarnings("ignore")
from ddgs import DDGS
from langchain_groq import ChatGroq
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.callbacks.base import BaseCallbackHandler

load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    raise EnvironmentError("GROQ_API_KEY not found in .env")

class ToolLogger(BaseCallbackHandler):
    def on_agent_action(self, action, **kwargs):
        print(f"  → [{action.tool}] {str(action.tool_input)[:100]}")
    def on_tool_end(self, output, **kwargs):
        print(f"  ← {str(output)[:80]}…")

def web_search(query: str) -> str:
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=4)
        return "\n".join(f"{r['title']}: {r['body']}" for r in results)

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
tools = [
    Tool("Web Search", web_search,
         "Use for current events, news, recent AI developments, real-time info."),
    Tool("Wikipedia", WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000).run,
         "Use for background knowledge, history, concepts, people, companies."),
]
agent_executor = AgentExecutor(
    agent=create_react_agent(llm, tools, hub.pull("hwchase17/react")),
    tools=tools, verbose=False, handle_parsing_errors=True,
    max_iterations=4, early_stopping_method="generate",
    callbacks=[ToolLogger()],
)

def ask(query: str, retries: int = 1) -> str:
    for attempt in range(retries + 1):
        try:
            t0 = time.perf_counter()
            result = agent_executor.invoke({"input": query})["output"]
            print(f"\n  ⏱  {time.perf_counter() - t0:.1f}s")
            return result
        except Exception as e:
            if attempt < retries:
                print(f"  Retry {attempt+1}/{retries}… ({e})")
                time.sleep(2)
            else:
                return f"Error: {e}"

def show(title, text):
    print(f"\n{'═'*70}\n  {title}\n{'═'*70}\n{text}\n{'═'*70}")

OPENING = ("Give me today's top 4 AI news items. For each: "
           "1. Headline  2. One line summary  3. Why it matters  4. Source")

print("╔══════════════════════════════════╗")
print("║    AI Research Agent  🤖  Groq   ║")
print("╚══════════════════════════════════╝\n")
show("TODAY'S AI NEWS", ask(OPENING))

history = []
print("\nAsk anything — 'exit' to quit, '/history' to review.\n")
while True:
    try:
        q = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!"); break
    if not q: continue
    if q.lower() in ("exit", "quit"): print("Goodbye!"); break
    if q == "/history":
        print("\n".join(f"  {i+1}. {h}" for i, h in enumerate(history)) or "  No history yet.")
        continue
    show("RESPONSE", ask(q))
    history.append(q)