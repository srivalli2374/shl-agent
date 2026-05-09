from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from app.retriever import search_assessments

app = FastAPI()


# -----------------------------
# MODELS
# -----------------------------

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


# -----------------------------
# HEALTH ENDPOINT
# -----------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# CHAT ENDPOINT
# -----------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    messages = request.messages

    # Get latest user message
    user_message = messages[-1].content.lower()

    # -----------------------------
    # REFUSAL HANDLING
    # -----------------------------

    off_topic_keywords = [
        "salary",
        "legal",
        "politics",
        "movie",
        "weather",
        "football",
        "cricket"
    ]

    if any(word in user_message for word in off_topic_keywords):

        return {
            "reply": "I can only help with SHL assessment recommendations and comparisons.",
            "recommendations": [],
            "end_of_conversation": False
        }

    # -----------------------------
    # CLARIFICATION
    # -----------------------------

    vague_keywords = [
        "assessment",
        "test",
        "hiring"
    ]

    if (
        len(user_message.split()) < 4
        or any(word == user_message for word in vague_keywords)
    ):

        return {
            "reply": "Could you share more details about the role, seniority, and skills you are hiring for?",
            "recommendations": [],
            "end_of_conversation": False
        }

    # -----------------------------
    # COMPARISON HANDLING
    # -----------------------------

    comparison_keywords = [
        "compare",
        "difference",
        "vs",
        "versus"
    ]

    if any(word in user_message for word in comparison_keywords):

        results = search_assessments(user_message, top_k=2)

        recommendations = []

        for item in results:

            recommendations.append({
                "name": item["name"],
                "url": item["url"],
                "test_type": item.get("test_type", "K")
            })

        names = [item["name"] for item in results]

        reply = (
            f"{names[0]} and {names[1]} assess different competencies "
            f"and job-relevant capabilities based on the SHL catalog."
        )

        return {
            "reply": reply,
            "recommendations": recommendations,
            "end_of_conversation": False
        }

    # -----------------------------
    # REFINEMENT HANDLING
    # -----------------------------

    refinement_keywords = [
        "also",
        "add",
        "include",
        "personality",
        "communication",
        "leadership"
    ]

    if any(
        word in user_message
        for word in refinement_keywords
    ):

        results = search_assessments(user_message, top_k=5)

        recommendations = []

        for item in results:

            recommendations.append({
                "name": item["name"],
                "url": item["url"],
                "test_type": item.get("test_type", "K")
            })

        return {
            "reply": "I updated the recommendations based on your refined requirements.",
            "recommendations": recommendations,
            "end_of_conversation": True
        }

    # -----------------------------
    # NORMAL RECOMMENDATION FLOW
    # -----------------------------

    results = search_assessments(user_message, top_k=5)

    recommendations = []

    for item in results:

        recommendations.append({
            "name": item["name"],
            "url": item["url"],
            "test_type": item.get("test_type", "K")
        })

    return {
        "reply": "Here are some recommended SHL assessments for your hiring needs.",
        "recommendations": recommendations,
        "end_of_conversation": True
    }