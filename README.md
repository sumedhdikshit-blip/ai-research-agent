Absolutely. Here's a cleaner and more professional version that reads well for a GitHub README while still sounding personal:

---

# AI Finance Agent

A terminal-based AI agent that lets you chat with financial data in natural language.

Built as part of my Generative AI learning journey, this project combines tool-calling agents with real-time financial data so you can ask questions about stocks, company valuations, and market comparisons directly from the command line.

## Features

* 📈 Fetch live stock prices for publicly traded companies
* 📊 View historical stock data for any time period
* 🏢 Retrieve valuations of private companies such as SpaceX, Stripe, and Airbnb
* ⚖️ Compare companies side by side
* 🤖 Natural language interface powered by an AI agent
* 🔧 Automatic tool selection based on user queries

## Tech Stack

* **LangGraph** — Agent workflow and tool orchestration
* **Groq (LLaMA 3.3 70B)** — Large Language Model
* **Yahoo Finance (yFinance)** — Real-time market data
* **LangChain** — Tool integration and agent utilities

## Installation

Clone the repository:

```bash
git clone https://github.com/sumedhdikshit-blip/ai-research-agent.git
cd ai-research-agent
```

Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install langchain langchain-groq langgraph yfinance python-dotenv
```

## Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key_here
```

## Run the Agent

```bash
python 2_agent_with_tools/agent_with_tools.py
```

## Example Conversations

### Company Valuation

```text
You: What is the valuation of SpaceX?

Agent: SpaceX is currently valued at approximately $137 billion.
```

### Company Comparison

```text
You: Compare SpaceX and Stripe

Agent: SpaceX is valued at approximately $137B, while Stripe is valued at around $95B. SpaceX currently has the higher valuation.
```

### Stock Price History

```text
You: Show me TSLA stock history for the last month

Agent:
2026-06-02: $423.74
2026-06-03: $423.70
...
```

## Why I Built This

I created this project to learn how modern AI agents use tools to interact with external data sources. The agent understands user intent, selects the appropriate financial tool, and returns relevant information in a conversational format.

## Get a Groq API Key


---
