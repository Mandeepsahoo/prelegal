"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { NdaPreview } from "@/components/NdaPreview";
import { SiteHeader } from "@/components/SiteHeader";
import { useAuth } from "@/lib/auth/AuthContext";
import type { SavedDocument, SavedDocumentSummary } from "@/lib/history/api";
import { getSavedDocument, listSavedDocuments } from "@/lib/history/api";
import { downloadTextFile, slugify } from "@/lib/nda/download";

export default function DocumentsPage() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const [documents, setDocuments] = useState<SavedDocumentSummary[] | null>(null);
  const [selected, setSelected] = useState<SavedDocument | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    listSavedDocuments()
      .then(setDocuments)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load documents."));
  }, [user]);

  const handleView = async (id: number) => {
    setError(null);
    try {
      setSelected(await getSavedDocument(id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load document.");
    }
  };

  return (
    <div className="flex flex-1 flex-col bg-zinc-50 dark:bg-black">
      <SiteHeader subtitle="Documents you've previously generated and downloaded." />

      {isAuthLoading ? (
        <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading...</p>
        </main>
      ) : !user ? (
        <main className="mx-auto flex w-full max-w-md flex-1 flex-col items-center justify-center gap-4 px-6 py-12 text-center">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Log in to see documents you&apos;ve previously generated and downloaded.
          </p>
          <Link
            href="/login"
            className="rounded-md bg-[#753991] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#5f2d75]"
          >
            Log in
          </Link>
        </main>
      ) : (
        <main className="mx-auto grid w-full max-w-6xl flex-1 grid-cols-1 gap-8 px-6 py-8 lg:grid-cols-[18rem_1fr]">
          <div className="flex flex-col gap-3">
            {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
            {documents === null && (
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading...</p>
            )}
            {documents?.length === 0 && (
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                You haven&apos;t downloaded any documents yet.
              </p>
            )}
            <ul className="flex flex-col gap-2">
              {documents?.map((doc) => (
                <li key={doc.id}>
                  <button
                    type="button"
                    onClick={() => handleView(doc.id)}
                    className={`w-full rounded-md border px-3 py-2 text-left text-sm transition-colors ${
                      selected?.id === doc.id
                        ? "border-[#209dd7] bg-[#209dd7]/10"
                        : "border-zinc-200 bg-white hover:border-[#209dd7] dark:border-zinc-800 dark:bg-zinc-900"
                    }`}
                  >
                    <span className="block font-medium text-zinc-900 dark:text-zinc-100">
                      {doc.title}
                    </span>
                    <span className="block text-xs text-zinc-500 dark:text-zinc-400">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div>
            {selected ? (
              <div className="flex flex-col gap-3">
                <button
                  type="button"
                  onClick={() =>
                    downloadTextFile(`${slugify(selected.title) || "document"}.md`, selected.content)
                  }
                  className="self-end rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
                >
                  Download .md
                </button>
                <NdaPreview document={selected.content} />
              </div>
            ) : (
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Select a document to view it.</p>
            )}
          </div>
        </main>
      )}
    </div>
  );
}
