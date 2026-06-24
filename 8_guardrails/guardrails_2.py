from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain.agents.middleware._redaction import PIIDetectionError
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

@tool
def search_docs(query: str) -> str:
    """Search coding documentation for a given query."""
    docs = {
        # Fictional language: Fluxon
        "fluxon api":        "In Fluxon, use `flux.connect(endpoint) >> auth(token)` to call an API. Store your token in a .fluxenv file, never hardcode it.",
        "fluxon loop":       "Fluxon loops use the `cycle` keyword: `cycle x in collection { ... }`. There is no traditional for/while loop.",
        "fluxon function":   "Define functions in Fluxon with `def! myFunc(arg1, arg2) => { ... }`. All functions are pure by default.",

        # Fictional language: Zyphor
        "zyphor database":   "In Zyphor, connect to a database using `db::bind('host', schema)`. Credentials must be passed via `env::secret('DB_PASS')`, never inline.",
        "zyphor list":       "Zyphor lists are declared with `[]~` syntax: `let items = [1, 2, 3]~`. Use `.push~(value)` to append.",
        "zyphor error":      "Zyphor handles errors with `catch~` blocks: `try~ { risky() } catch~(e) { log(e) }`.",

        # Fictional language: Brevik
        "brevik file":       "Read files in Brevik using `@read('path') -> buffer`. Always wrap in `@safe { }` block to handle IO errors.",
        "brevik http":       "Brevik HTTP requests use `fetch<GET>(url, headers=[])`. Never log headers as they may contain auth tokens.",
    }
    for key, answer in docs.items():
        if key in query.lower():
            return answer

    return f"No documentation found for '{query}'. Try: 'fluxon api', 'zyphor database', or 'brevik file'."

# ── Agent setup ───────────────────────────────────────────────────────────────

agent = create_agent(
    model=llm,
    tools=[search_docs],
    system_prompt="""You are a coding assistant for three programming languages: Fluxon, Zyphor, and Brevik.
    You have NO built-in knowledge about these languages.
    ALWAYS use search_docs to look up any question about these languages.
    Generate short and precise answer all the time. 
    Never guess or make up syntax — only answer based on what search_docs returns.""",
    middleware=[
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
            apply_to_input=True,
        ),
    ],
)

def chat(user_input: str):
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": user_input}]
        })
        print(f"\n🤖 Assistant: {result['messages'][-1].content}\n")

    except PIIDetectionError as e:
        # PIIMiddleware raises PIIDetectionError when strategy="block" is triggered
        print(f"\n🚫 Blocked: {e}")
        print("⚠️  Your message contains a sensitive API key.")
        print("💡 Tip: Use environment variables instead — os.getenv('OPENAI_API_KEY')\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  Fluxon / Zyphor / Brevik Docs Assistant")
    print("  type 'quit' to exit")
    print("=" * 55)
    print("\nTry asking:")
    print("  • How do I call an API in Fluxon?")
    print("  • How do I connect to a database in Zyphor?")
    print("  • How do I read a file in Brevik?")

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break
        chat(user_input)
