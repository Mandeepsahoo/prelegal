import { apiBaseUrl, parseErrorMessage, postJson } from "@/lib/api";

export interface DocumentTypeInfo {
  key: string;
  name: string;
  description: string;
  is_special: boolean;
}

export interface FieldValue {
  label: string;
  value: string;
}

export interface DocumentChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface DocumentChatResponse {
  reply: string;
  fields: FieldValue[];
  is_complete: boolean;
  document: string;
}

export interface ClassifyResponse {
  matched_key: string | null;
  reply: string;
}

export async function listDocumentTypes(): Promise<DocumentTypeInfo[]> {
  const response = await fetch(`${apiBaseUrl()}/api/documents/types`);
  if (!response.ok) throw new Error(await parseErrorMessage(response));
  return response.json();
}

export function classifyDocumentRequest(description: string): Promise<ClassifyResponse> {
  return postJson("/api/documents/classify", { description });
}

export function sendDocumentChatMessage(
  documentKey: string,
  messages: DocumentChatMessage[],
  fields: FieldValue[],
): Promise<DocumentChatResponse> {
  return postJson("/api/documents/chat", { document_key: documentKey, messages, fields });
}
