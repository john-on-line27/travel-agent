from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import agent_executor, parser, build_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    budget: str
    duration: str
    interests: str
    starting_location: str
    travel_scope: str
    popularity: str

@app.post("/recommend")
def recommend(request: TripRequest):
    query = build_query(
        request.budget,
        request.duration,
        request.interests,
        request.starting_location,
        request.travel_scope,
        request.popularity,
    )
    raw_response = agent_executor.invoke({"query": query})
    try:
        result = parser.parse(raw_response.get("output"))
        return result.dict()
    except Exception as e:
        return {"error": str(e), "raw_output": raw_response.get("output")}
