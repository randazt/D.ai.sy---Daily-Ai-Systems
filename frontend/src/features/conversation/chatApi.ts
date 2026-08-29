import type { ChatRequest, ChatResponse } from "./chatTypes";

export async function sendChatMessage(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`D.AI.SY request failed with status ${response.status}.`);
  }

  return (await response.json()) as ChatResponse;
}
