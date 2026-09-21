"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { DocumentChat } from "@/components/DocumentChat";
import { DocumentPicker } from "@/components/DocumentPicker";
import { NdaChat } from "@/components/NdaChat";
import { NdaPreview } from "@/components/NdaPreview";
import type { DocumentTypeInfo } from "@/lib/documents/api";
import { downloadTextFile, slugify } from "@/lib/nda/download";
import { buildNdaDocument } from "@/lib/nda/generate";
import { defaultNdaFormData, NdaFormData } from "@/lib/nda/types";

const GENERIC_PLACEHOLDER_DOCUMENT = "_Your document will appear here as you chat._";

export default function Home() {
  const [selectedType, setSelectedType] = useState<DocumentTypeInfo | null>(null);
  const [ndaFormData, setNdaFormData] = useState<NdaFormData>(defaultNdaFormData);
  const [genericDocument, setGenericDocument] = useState(GENERIC_PLACEHOLDER_DOCUMENT);

  const ndaDocument = useMemo(() => buildNdaDocument(ndaFormData).full, [ndaFormData]);
  const isNda = selectedType?.is_special ?? false;
  const activeDocument = isNda ? ndaDocument : genericDocument;

  const handleReset = () => {
    setSelectedType(null);
    setNdaFormData(defaultNdaFormData());
    setGenericDocument(GENERIC_PLACEHOLDER_DOCUMENT);
  };

  const handleDownload = () => {
    const slug = (selectedType && slugify(selectedType.name)) || "document";
    downloadTextFile(`${slug}.md`, activeDocument);
  };

  return (
    <div className="flex flex-1 flex-col bg-zinc-50 dark:bg-black">
      <header className="flex items-start justify-between gap-4 border-b border-zinc-200 bg-white px-6 py-5 dark:border-zinc-800 dark:bg-zinc-950">
        <div>
          <h1 className="text-xl font-semibold text-[#032147] dark:text-zinc-50">Prelegal</h1>
          <p className="mt-1 max-w-2xl text-sm text-zinc-600 dark:text-zinc-400">
            {selectedType
              ? `Chat with the assistant to fill in the details of a ${selectedType.name}, then download the completed document.`
              : "Choose a document type to get started, or describe what you need."}
          </p>
        </div>
        <nav className="flex shrink-0 items-center gap-4 pt-1 text-sm">
          <Link href="/login" className="text-[#209dd7] hover:underline">
            Log in
          </Link>
          <Link href="/signup" className="text-[#209dd7] hover:underline">
            Sign up
          </Link>
        </nav>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
        {!selectedType ? (
          <DocumentPicker onSelect={setSelectedType} />
        ) : (
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            <div className="flex flex-col gap-4">
              <button
                type="button"
                onClick={handleReset}
                className="self-start text-sm text-[#209dd7] hover:underline"
              >
                &larr; Choose a different document
              </button>
              {isNda ? (
                <NdaChat fields={ndaFormData} onFieldsChange={setNdaFormData} />
              ) : (
                <DocumentChat documentType={selectedType} onDocumentChange={setGenericDocument} />
              )}
            </div>

            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Preview</h2>
                <button
                  type="button"
                  onClick={handleDownload}
                  className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
                >
                  Download .md
                </button>
              </div>
              <div className="lg:sticky lg:top-8 lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto">
                <NdaPreview document={activeDocument} />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
