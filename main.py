from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool



class Destination(BaseModel):
    name: str
    country: str
    reason: str

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    destinations: list[Destination]
    sources: list[str]
    tools_used: list[str]
    

llm = ChatOpenAI(model="gpt-4o-mini")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
                """
                You are an expert travel agent. Given the user's inputs, recommend exactly 3 destinations.

                For each destination you MUST:
                - Explain in 2-3 sentences why it specifically matches their budget, duration, and interests
                - Name one specific dish to try, one landmark to visit, and one budget tip
                - Only recommend places reachable from their starting location within their trip duration

                Search for each destination individually before recommending it. Do not recommend a place you haven't searched for.
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

BUDGET_CONTEXT = {
    "budget": "very low cost — hostels, street food, free attractions, cheap local transport. Countries like Portugal, Poland, Romania, Albania, Georgia, Vietnam, and Thailand fit this tier. Avoid expensive countries like Switzerland, Norway, Iceland, and Austria.",
    "mid-range": "moderate spending — 3-star hotels or guesthouses, sit-down restaurants, paid attractions. Countries like Spain, Croatia, Czech Republic, Hungary, Greece, and Mexico fit this tier. Avoid very expensive destinations like Switzerland and Scandinavia.",
    "luxury": "high-end spending — 4-5 star hotels, fine dining, premium experiences. Any destination is appropriate.",
}

def build_query(budget: str, duration: str, interests: str, starting_location: str, travel_scope: str, popularity: str) -> str:
    budget_context = BUDGET_CONTEXT.get(budget.lower().strip(), f"{budget} budget")

    if "stay" in travel_scope.lower():
        scope_instruction = f"Only recommend destinations within the same country as {starting_location}. Do NOT suggest any destinations outside that country."
    else:
        scope_instruction = f"The user wants to travel ABROAD — outside their home country. Do NOT recommend any destinations in the same country as {starting_location}. Search specifically for international destinations in other countries."

    return f"""
Trip details:
- Budget: {budget} ({budget_context})
- Duration: {duration}
- Interests: {interests}
- Starting from: {starting_location}
- Travel scope: {travel_scope}
- Popularity preference: {popularity}

{scope_instruction}
Budget is a hard constraint — only recommend destinations where the overall cost of living and travel matches the budget level described above. Do not recommend expensive countries if the budget is low or mid-range.
Search for {popularity} travel destinations matching these interests, then recommend 3 specific places with concrete reasons why each fits this exact traveler.
"""

if __name__ == "__main__":
    print("Let's plan your trip!\n")
    budget = input("What is your budget level? (budget / mid-range / luxury): ")
    duration = input("How long is your trip? (e.g. 1 week, 10 days): ")
    interests = input("What are your travel interests? (e.g. beaches, history, food): ")
    starting_location = input("Where are you starting from? (e.g. Berlin, Munich): ")
    travel_scope = input("Do you want to stay in your country or travel abroad? (stay in country / go abroad): ")
    popularity = input("How popular do you want the destination? (tourist hotspot / moderate / off the beaten path): ")

    query = build_query(budget, duration, interests, starting_location, travel_scope, popularity)
    raw_response = agent_executor.invoke({"query": query})

    try:
        structured_response = parser.parse(raw_response.get("output"))
        print(structured_response)
    except Exception as e:
        print("Error parsing response", e, "Raw Response - ", raw_response)