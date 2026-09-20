"use client";

import { FormEvent, useEffect, useState } from "react";
import type { DocumentTypeInfo } from "@/lib/documents/api";
import { classifyDocumentRequest, listDocumentTypes } from "@/lib/documents/api";

interface DocumentPickerProps {
  onSelect: (documentType: DocumentTypeInfo) => void;
}

export function DocumentPicker({ onSelect }: DocumentPickerProps) {
  const [types, setTypes] = useState<DocumentTypeInfo[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [description, setDescription] = useState("");
  const [isClassifying, setIsClassifying] = useState(false);
  const [classifyMessage, setClassifyMessage] = useState<string | null>(null);
  const [classifyError, setClassifyError] = useState<string | null>(null);

  useEffect(() => {
    listDocumentTypes()
      .then(setTypes)
      .catch((err) =>
        setLoadError(err instanceof Error ? err.message : "Failed to load document types."),
      );
  }, []);

  const handleDescribe = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = description.trim();
    if (!trimmed || isClassifying) return;

    setIsClassifying(true);
    setClassifyMessage(null);
    setClassifyError(null);
    try {
      const result = await classifyDocumentRequest(trimmed);
      const match = result.matched_key ? types?.find((type) => type.key === result.matched_key) : null;
      if (match) {
        onSelect(match);
        return;
      }
      setClassifyMessage(result.reply);
    } catch (err) {
      setClassifyError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setIsClassifying(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <form
        onSubmit={handleDescribe}
        className="flex flex-col gap-2 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
      >
        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
          Not sure which one you need? Describe it:
        </label>
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm focus:border-[#209dd7] focus:outline-none focus:ring-1 focus:ring-[#209dd7] dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="e.g. something covering a vendor processing our customers' data"
            disabled={isClassifying}
          />
          <button
            type="submit"
            disabled={isClassifying || !description.trim()}
            className="shrink-0 rounded-md bg-[#753991] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#5f2d75] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isClassifying ? "Thinking..." : "Find it"}
          </button>
        </div>
        {classifyMessage && (
          <p className="rounded-md bg-zinc-100 px-3 py-2 text-sm text-[#032147] dark:bg-zinc-800 dark:text-zinc-100">
            {classifyMessage}
          </p>
        )}
        {classifyError && <p className="text-sm text-red-600 dark:text-red-400">{classifyError}</p>}
      </form>

      <div>
        <h2 className="mb-3 text-sm font-semibold text-[#032147] dark:text-zinc-100">
          Or pick a document type
        </h2>
        {loadError && <p className="text-sm text-red-600 dark:text-red-400">{loadError}</p>}
        {types === null && !loadError && (
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading document types...</p>
        )}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {types?.map((type) => (
            <button
              key={type.key}
              type="button"
              onClick={() => onSelect(type)}
              className="flex flex-col gap-1 rounded-lg border border-zinc-200 bg-white p-4 text-left shadow-sm transition-colors hover:border-[#209dd7] dark:border-zinc-800 dark:bg-zinc-900"
            >
              <span className="text-sm font-semibold text-[#032147] dark:text-zinc-50">{type.name}</span>
              <span className="text-xs text-zinc-600 dark:text-zinc-400">{type.description}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
