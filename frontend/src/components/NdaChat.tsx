"use client";

import { useState } from "react";
import { ChatPanel } from "@/components/ChatPanel";
import type { ChatMessage } from "@/lib/nda/chat";
import { sendChatMessage } from "@/lib/nda/chat";
import type { NdaFormData } from "@/lib/nda/types";

const GREETING: ChatMessage = {
  role: "assistant",
  content:
    "Hi! I'll help you put together a Common Paper Mutual NDA. Let's start with the two parties — who are they, and what companies are they with?",
};

interface NdaChatProps {
  fields: NdaFormData;
  onFieldsChange: (next: NdaFormData) => void;
}

export function NdaChat({ fields, onFieldsChange }: NdaChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  const handleSend = async (content: string) => {
    const nextMessages = [...messages, { role: "user", content } as ChatMessage];
    setMessages(nextMessages);
    setError(null);
    setIsSending(true);

    try {
      const response = await sendChatMessage(nextMessages, fields);
      setMessages([...nextMessages, { role: "assistant", content: response.reply }]);
      onFieldsChange(response.fields);
      setIsComplete(response.is_complete);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <ChatPanel
      messages={messages}
      onSend={handleSend}
      isSending={isSending}
      error={error}
      completeMessage={
        isComplete
          ? "Your NDA looks ready — check the preview and download it whenever you're happy with it."
          : null
      }
    />
  );
}
