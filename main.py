from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool



class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]
    

llm = ChatOpenAI(model="gpt-3.5-turbo")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a travel agent that will help generate recommendations for places to go, and generate a two sentence reason why this place is nice to visit.
            Answer the user query and use neccessary tools. 
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
print("Let's plan your trip!\n")
budget = input("What is your budget level? (budget / mid-range / luxury): ")
duration = input("How long is your trip? (e.g. 1 week, 10 days): ")
interests = input("What are your travel interests? (e.g. beaches, history, food): ")
starting_location = input("Where are you starting from? (e.g. Berlin, Munich): ")

query = f"""
I want to do a {duration} trip with a {budget} budget.
My interests are: {interests}.
I am starting from {starting_location}.
Please recommend destinations and explain why each is a good fit.
"""

raw_response = agent_executor.invoke({"query": query})

try:
    structured_response = parser.parse(raw_response.get("output"))
    print(structured_response)
except Exception as e:
    print("Error parsing response", e, "Raw Response - ", raw_response)