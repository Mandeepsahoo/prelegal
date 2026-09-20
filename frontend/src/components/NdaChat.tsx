"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
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
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const content = input.trim();
    if (!content || isSending) return;

    const nextMessages = [...messages, { role: "user", content } as ChatMessage];
    setMessages(nextMessages);
    setInput("");
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
    <div className="flex h-full flex-col rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex-1 space-y-3 overflow-y-auto p-4" style={{ minHeight: "24rem", maxHeight: "32rem" }}>
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
                message.role === "user"
                  ? "bg-[#209dd7] text-white"
                  : "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        {isSending && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-lg bg-zinc-100 px-3 py-2 text-sm text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {isComplete && (
        <p className="mx-4 mb-3 rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
          Your NDA looks ready — check the preview and download it whenever you&apos;re happy with it.
        </p>
      )}
      {error && <p className="mx-4 mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}

      <form onSubmit={handleSubmit} className="flex gap-2 border-t border-zinc-200 p-3 dark:border-zinc-800">
        <input
          className="flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm focus:border-[#209dd7] focus:outline-none focus:ring-1 focus:ring-[#209dd7] dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Type your reply..."
          disabled={isSending}
        />
        <button
          type="submit"
          disabled={isSending || !input.trim()}
          className="rounded-md bg-[#753991] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#5f2d75] disabled:cursor-not-allowed disabled:opacity-60"
        >
          Send
        </button>
      </form>
    </div>
  );
}
