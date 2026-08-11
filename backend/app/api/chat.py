from fastapi import APIRouter

from app.schemas.chat import ChatRequest
from app.services.chat_service import chat_service

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    print(">>> CHAT ENDPOINT REACHED")
    print(">>> MESSAGE:", request.message)

    return await chat_service.chat(request.message)