import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function NdaPreview({ document }: { document: string }) {
  return (
    <div className="prose prose-zinc max-w-none rounded-lg border border-zinc-200 bg-white p-6 dark:prose-invert dark:border-zinc-800 dark:bg-zinc-900">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{document}</ReactMarkdown>
    </div>
  );
}
