<img width="1057" height="596" alt="image" src="https://github.com/user-attachments/assets/6f6e5e58-87bb-4fee-b088-a42b4d657ea1" />
**Travel Advice Agent**

An intelligent tool-integrated AI agent designed to help users plan their trips end-to-end from finding flights to checking weather, estimating budgets and discovering travel insights — all in a single conversational interface.****

**Overview**
Planning a holiday typically involves switching between multiple platforms — searching for flights, checking weather forecasts, comparing currency rates, and browsing travel blogs. This process is often fragmented and time-consuming.

This project solves that problem by building a Travel Advice AI Agent that integrates multiple external services into a unified, conversational experience. The agent is capable of understanding user intent, performing multi-step reasoning, and delivering actionable travel recommendations.

**Key Features**
•	Flight Search – Retrieve flight options using SerpAPI (Google Flights)
•	Weather Forecasting – Real-time and forecast weather using Open-Meteo
•	Currency Conversion – Live exchange rates using ExchangeRate API
•	Travel Insights – Discover hidden gems and local recommendations using Tavily
•	Contextual Memory – Maintains conversation context using thread_id
•	Multi-step Reasoning – Chains multiple tools to answer complex queries

**Tech Stack**
•	LLM Framework: LangChain / LangGraph
•	Model: Azure OpenAI (GPT-based)
•	APIs Used:
•	SerpAPI (Google Flights)
•	Open-Meteo (Weather)
•	ExchangeRate API (Currency)
•	Tavily (Search / Travel Insights)
•	UI: Jupyter Notebook with ipywidgets
•	Language: Python

**Project Structure**
project/
│
├── tool.py        # All tool functions (flight, weather, currency, search)
├── prompt.py      # Prompt construction logic
├── agent.py       # Agent setup (LLM, tools, memory)
├── notebook.ipynb # Interactive UI using widgets
├── .env           # API keys and environment variables
└── README.md

**Configuration Environment**
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
OPENAI_API_VERSION=your_version

SERPAPI_KEY=your_serpapi_key
TAVILY_API_KEY=your_tavily_key








