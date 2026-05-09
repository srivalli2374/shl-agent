from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.retriever import search_assessments

app = FastAPI()

# =========================
# REQUEST MODELS
# =========================

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


# =========================
# HEALTH ENDPOINT
# =========================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =========================
# CHAT ENDPOINT
# =========================

@app.post("/chat")
def chat(request: ChatRequest):

    messages = request.messages

    # =========================
    # GET FULL CONVERSATION
    # =========================

    full_conversation = " ".join(
        [
            msg.content
            for msg in messages
        ]
    ).lower()

    latest_user_message = ""

    for msg in reversed(messages):

        if msg.role == "user":

            latest_user_message = msg.content

            break

    query = latest_user_message.lower()

    # =========================
    # REFUSAL LOGIC
    # =========================

    off_topic_keywords = [
        "salary",
        "legal",
        "lawsuit",
        "politics",
        "religion",
        "election",
        "medical"
    ]

    injection_keywords = [
        "ignore previous instructions",
        "bypass",
        "hack",
        "override"
    ]

    for word in off_topic_keywords:

        if word in query:

            return {
                "reply": (
                    "I can only help with "
                    "SHL assessment recommendations."
                ),
                "recommendations": [],
                "end_of_conversation": False
            }

    for word in injection_keywords:

        if word in query:

            return {
                "reply": (
                    "I cannot comply with "
                    "instruction override requests."
                ),
                "recommendations": [],
                "end_of_conversation": False
            }

    # =========================
    # COMPARISON LOGIC
    # =========================
    # =========================
    # COMPARISON LOGIC
    # =========================

    if "compare" in query:

        comparison_results = search_assessments(
            query,
            top_k=2
        )

        if len(comparison_results) >= 2:

            item1 = comparison_results[0]
            item2 = comparison_results[1]

            comparison_reply = (
                f"{item1['name']} and "
                f"{item2['name']} assess "
                "different competencies and "
                "job-relevant capabilities "
                "based on the SHL catalog."
            )

            return {
                "reply": comparison_reply,
                "recommendations": [
                    {
                        "name": item1["name"],
                        "url": item1["url"]
                    },
                    {
                        "name": item2["name"],
                        "url": item2["url"]
                    }
                ],
                "end_of_conversation": False
            }

        return {
            "reply": (
                "I could not find enough "
                "assessment information "
                "for comparison."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }
    is_refinement = any(
        word in query
        for word in refinement_keywords
    )

    # =========================
    # CLARIFICATION LOGIC
    # =========================

    if (
        len(query.split()) <= 3
        and not is_refinement
    ):

        return {
            "reply": (
                "Could you share more details "
                "about the role, seniority, "
                "skills, and assessment needs?"
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    # =========================
    # USE FULL CONVERSATION
    # =========================

    retrieval_query = full_conversation

    # =========================
    # RETRIEVE RECOMMENDATIONS
    # =========================

    results = search_assessments(
        retrieval_query,
        top_k=5
    )

    recommendations = []

    for item in results:

        recommendations.append({
            "name": item["name"],
            "url": item["url"],
            "test_type": item.get("test_type", "K")
        })

    # =========================
    # RESPONSE MESSAGE
    # =========================

    if is_refinement:

        reply = (
            "I updated the recommendations "
            "based on your refined requirements."
        )

    else:

        reply = (
            "Here are recommended SHL "
            "assessments for your hiring needs."
        )

    return {
        "reply": reply,
        "recommendations": recommendations,
        "end_of_conversation": True
    }