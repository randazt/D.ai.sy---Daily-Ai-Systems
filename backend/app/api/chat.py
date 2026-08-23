from fastapi import APIRouter

from app.schemas.chat import ChatEndpointResponse, ChatRequest
from app.services.chat_service import chat_service

router = APIRouter()


@router.post("/chat", responses={200: {"model": ChatEndpointResponse}})
async def chat(request: ChatRequest):
    print(">>> CHAT ENDPOINT REACHED")
    print(">>> MESSAGE:", request.message)

    return await chat_service.chat(
        request.message,
        clarification_token=request.clarification_token,
    )
