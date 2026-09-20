import { apiBaseUrl, parseErrorMessage } from "@/lib/api";
import { getToken } from "@/lib/auth/api";

export interface SavedDocumentSummary {
  id: number;
  document_type_name: string;
  title: string;
  created_at: string;
}

export interface SavedDocument extends SavedDocumentSummary {
  content: string;
}

function authHeaders(): HeadersInit {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function saveDocumentToHistory(
  documentTypeName: string,
  title: string,
  content: string,
): Promise<SavedDocument> {
  const response = await fetch(`${apiBaseUrl()}/api/documents/history`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ document_type_name: documentTypeName, title, content }),
  });
  if (!response.ok) throw new Error(await parseErrorMessage(response));
  return response.json();
}

export async function listSavedDocuments(): Promise<SavedDocumentSummary[]> {
  const response = await fetch(`${apiBaseUrl()}/api/documents/history`, { headers: authHeaders() });
  if (!response.ok) throw new Error(await parseErrorMessage(response));
  return response.json();
}

export async function getSavedDocument(id: number): Promise<SavedDocument> {
  const response = await fetch(`${apiBaseUrl()}/api/documents/history/${id}`, {
    headers: authHeaders(),
  });
  if (!response.ok) throw new Error(await parseErrorMessage(response));
  return response.json();
}
