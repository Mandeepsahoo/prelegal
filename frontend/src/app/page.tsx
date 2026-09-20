"use client";

import { useMemo, useState } from "react";
import { DocumentChat } from "@/components/DocumentChat";
import { DocumentPicker } from "@/components/DocumentPicker";
import { NdaChat } from "@/components/NdaChat";
import { NdaPreview } from "@/components/NdaPreview";
import { SiteHeader } from "@/components/SiteHeader";
import type { DocumentTypeInfo } from "@/lib/documents/api";
import { useAuth } from "@/lib/auth/AuthContext";
import { saveDocumentToHistory } from "@/lib/history/api";
import { downloadTextFile, slugify } from "@/lib/nda/download";
import { buildNdaDocument } from "@/lib/nda/generate";
import { defaultNdaFormData, NdaFormData } from "@/lib/nda/types";

const GENERIC_PLACEHOLDER_DOCUMENT = "_Your document will appear here as you chat._";

export default function Home() {
  const { user } = useAuth();
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

    if (user && selectedType) {
      // Best-effort: the user already has their download, so a failure here
      // shouldn't surface as an error for an action they didn't explicitly take.
      saveDocumentToHistory(selectedType.name, selectedType.name, activeDocument).catch(() => {});
    }
  };

  return (
    <div className="flex flex-1 flex-col bg-zinc-50 dark:bg-black">
      <SiteHeader
        subtitle={
          selectedType
            ? `Chat with the assistant to fill in the details of a ${selectedType.name}, then download the completed document.`
            : "Choose a document type to get started, or describe what you need."
        }
      />

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
