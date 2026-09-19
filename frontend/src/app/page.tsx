"use client";

import { useMemo, useState } from "react";
import { NdaForm } from "@/components/NdaForm";
import { NdaPreview } from "@/components/NdaPreview";
import { downloadTextFile, slugify } from "@/lib/nda/download";
import { buildNdaDocument } from "@/lib/nda/generate";
import { defaultNdaFormData, NdaFormData } from "@/lib/nda/types";

export default function Home() {
  const [formData, setFormData] = useState<NdaFormData>(defaultNdaFormData);
  const document = useMemo(() => buildNdaDocument(formData).full, [formData]);

  const handleDownload = () => {
    const partyASlug = slugify(formData.partyA.company || formData.partyA.name) || "party-1";
    const partyBSlug = slugify(formData.partyB.company || formData.partyB.name) || "party-2";
    downloadTextFile(`mutual-nda-${partyASlug}-${partyBSlug}.md`, document);
  };

  return (
    <div className="flex flex-1 flex-col bg-zinc-50 dark:bg-black">
      <header className="border-b border-zinc-200 bg-white px-6 py-5 dark:border-zinc-800 dark:bg-zinc-950">
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
          Mutual NDA Creator
        </h1>
        <p className="mt-1 max-w-2xl text-sm text-zinc-600 dark:text-zinc-400">
          Fill in the details below to generate a Common Paper Mutual Non-Disclosure
          Agreement, then download the completed document.
        </p>
      </header>

      <main className="mx-auto grid w-full max-w-6xl flex-1 grid-cols-1 gap-8 px-6 py-8 lg:grid-cols-2">
        <div className="flex flex-col gap-4">
          <NdaForm value={formData} onChange={setFormData} />
        </div>

        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              Preview
            </h2>
            <button
              type="button"
              onClick={handleDownload}
              className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
            >
              Download .md
            </button>
          </div>
          <div className="lg:sticky lg:top-8 lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto">
            <NdaPreview document={document} />
          </div>
        </div>
      </main>
    </div>
  );
}
