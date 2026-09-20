import { postJson } from "@/lib/api";
import type { NdaFormData } from "@/lib/nda/types";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface NdaChatResponse {
  reply: string;
  fields: NdaFormData;
  is_complete: boolean;
}

export function sendChatMessage(
  messages: ChatMessage[],
  fields: NdaFormData,
): Promise<NdaChatResponse> {
  return postJson("/api/nda/chat", { messages, fields });
}
