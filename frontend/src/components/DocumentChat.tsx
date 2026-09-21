"use client";

import { useState } from "react";
import { ChatPanel, ChatPanelMessage } from "@/components/ChatPanel";
import type { DocumentTypeInfo, FieldValue } from "@/lib/documents/api";
import { sendDocumentChatMessage } from "@/lib/documents/api";

interface DocumentChatProps {
  documentType: DocumentTypeInfo;
  onDocumentChange: (document: string) => void;
}

export function DocumentChat({ documentType, onDocumentChange }: DocumentChatProps) {
  const [messages, setMessages] = useState<ChatPanelMessage[]>([
    {
      role: "assistant",
      content: `Hi! I'll help you put together a ${documentType.name}. Let's start with the parties involved — who are they?`,
    },
  ]);
  const [fields, setFields] = useState<FieldValue[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  const handleSend = async (content: string) => {
    const nextMessages = [...messages, { role: "user", content } as ChatPanelMessage];
    setMessages(nextMessages);
    setError(null);
    setIsSending(true);

    try {
      const response = await sendDocumentChatMessage(documentType.key, nextMessages, fields);
      setMessages([...nextMessages, { role: "assistant", content: response.reply }]);
      setFields(response.fields);
      setIsComplete(response.is_complete);
      onDocumentChange(response.document);
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
          ? "Your document looks ready — check the preview and download it whenever you're happy with it."
          : null
      }
    />
  );
}
