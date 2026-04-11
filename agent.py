import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from tool import (
    search_flights_skyline,
    check_exchange_rate,
    get_destination_weather,
    research_vacation_vibe,
)
from prompt import build_prompt

load_dotenv()

def build_agent():
    
    tools = [
        search_flights_skyline,
        check_exchange_rate,
        get_destination_weather,
        research_vacation_vibe,
    ]
    prompt = build_prompt(tools)
    llm = AzureChatOpenAI(
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        openai_api_version = os.getenv("OPENAI_API_VERSION"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key = os.getenv("AZURE_OPENAI_API_KEY"),
        temperature = 0
    )
    memory = InMemorySaver()
    
    agent = create_agent(
        model = llm,
        tools = tools,
        system_prompt = prompt,
        checkpointer = memory
    )
    
    return agent